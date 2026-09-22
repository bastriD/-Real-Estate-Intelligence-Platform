"""Offline governance contracts, shared by CI and the publication preflight.

No network calls. Asset existence is checked against dbt sources/models in CI;
the deployed engine still resolves assets against OpenMetadata at runtime.
"""
import json
import re
from pathlib import Path

# Required collections and record fields for every supported engine operation.
# A trailing [] denotes a nonempty list of strings; {} denotes an object.
CONTRACTS = {
    "domains": {"domains": "name description domain_type", "assignments": "domain entity_type targets[]"},
    "data_products": {"data_products": "name description domain primary_assets[] supporting_assets[] governance{}"},
    "metrics": {"metrics": "name description metric_type unit granularity expression_language expression source owner domain glossary_terms[]"},
    "privacy_assignments": {"column_assignments": "entity column tags[]"},
    "glossary": {"terms": "name description"},
    "glossary_assignments": {"table_assignments": "entity terms[]", "column_assignments": "entity column terms[]"},
    "classification": {"classifications": "name description tags{}[]"},
    "data_layer": {"layer_rules": "id schema tag description"},
    "certification": {"schema_rules": "schema certification"},
    "ownership": {"teams": "name description team_type", "ownership_rules": "id owner owner_type entity_type targets[]"},
    "descriptions": {"table_descriptions": "entity description"},
    "lineage": {"lineage_edges": "from to entity_type description"},
    "data_quality": {"quality_domains": "id name layer execution{}", "asset_rules": "id entity tags[] quality_domains[]", "lineage_requirements": "entity required_upstream[]"},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"{path}: duplicate JSON key {key}")
            result[key] = value
        return result
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    require(isinstance(data, dict), f"{path}: expected an object")
    return data


def fields(record, specification, context):
    require(isinstance(record, dict), f"{context}: expected a record")
    for field in specification.split():
        key = field.rstrip("[]{}")
        value = record.get(key)
        if field.endswith("[]"):
            require(isinstance(value, list) and bool(value), f"{context}.{key}: expected nonempty list")
            if field.endswith("{}[]"):
                for item in value:
                    fields(item, "name description", f"{context}.{key}")
            else:
                require(all(isinstance(v, str) and v.strip() for v in value), f"{context}.{key}: expected strings")
        elif field.endswith("{}"):
            require(isinstance(value, dict), f"{context}.{key}: expected object")
        else:
            require(isinstance(value, str) and bool(value.strip()), f"{context}.{key}: expected nonempty string")


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate(base, repository=None):
    base = Path(base).resolve()
    config = load(base / "docs/governance-config.json")
    fields(config, "openmetadata{} governance{}", "configuration")
    fields(config["openmetadata"], "database_service database base_url_env token_env", "openmetadata")
    sections = config["governance"]
    require(not set(sections) - set(CONTRACTS), "Unknown governance operation")
    documents = {}
    for operation, section in sections.items():
        require(isinstance(section, dict) and type(section.get("enabled")) is bool,
                f"{operation}: enabled must be a boolean")
        if not section["enabled"]:
            continue
        paths = [section["file"]] if "file" in section else section.get("files")
        require(isinstance(paths, list) and paths and all(isinstance(p, str) for p in paths),
                f"{operation}: expected configuration files")
        documents[operation] = []
        for relative in paths:
            path = (base / relative).resolve()
            require(path.is_relative_to(base), f"{operation}: path escapes governance directory")
            data = load(path)
            for collection, specification in CONTRACTS[operation].items():
                rows = data.get(collection)
                require(isinstance(rows, list) and bool(rows), f"{relative}: missing/nonempty list required: {collection}")
                identities = set()
                for index, row in enumerate(rows):
                    context = f"{relative}:{collection}[{index}]"
                    fields(row, specification, context)
                    identity = (row.get("name") or row.get("id") or row.get("entity")
                                or row.get("from") or row.get("schema"), row.get("column"), row.get("to"))
                    if identity[0] is not None:
                        require(identity not in identities, f"{context}: duplicate identifier {identity}")
                        identities.add(identity)
            if operation == "glossary":
                fields(data, "glossary{}", relative)
                fields(data["glossary"], "name description", relative)
            if operation == "certification":
                fields(data, "classification{}", relative)
                fields(data["classification"], "name description tags{}[]", relative)
            documents[operation].append(data)

    def rows(operation, key):
        return [r for d in documents.get(operation, []) for r in d.get(key, [])]

    classifications = rows("classification", "classifications") + [d["classification"] for d in documents.get("certification", [])]
    tags = {c["name"] + "." + t["name"] for c in classifications for t in c["tags"]}
    for c in classifications:
        require(len({t["name"] for t in c["tags"]}) == len(c["tags"]), f"Duplicate tag in {c['name']}")
        require(type(c.get("mutually_exclusive", False)) is bool, "mutually_exclusive must be boolean")
    terms = {d["glossary"]["name"] + "." + t["name"] for d in documents.get("glossary", []) for t in d["terms"]}
    owners = {r["name"] for r in rows("ownership", "teams")}
    domains = {r["name"] for r in rows("domains", "domains")}
    domains |= {r["parent"] + "." + r["name"] for r in rows("domains", "domains") if "parent" in r}
    quality_domains = {r["id"] for r in rows("data_quality", "quality_domains")}
    schema_names = set(config.get("target_schemas", []) + config.get("protected_schemas", []))
    prefix = config["openmetadata"]["database_service"] + "." + config["openmetadata"]["database"] + "."
    assets = set()
    for group in documents.values():
        for document in group:
            for record in walk(document):
                for key, value in record.items():
                    if key in {"terms", "quality_domains"} and isinstance(value, list) and all(isinstance(v, dict) for v in value):
                        continue
                    choices = {"terms": terms, "glossary_terms": terms, "tag": tags,
                               "certification": tags, "owner": owners, "domain": domains,
                               "parent": domains, "quality_domains": quality_domains}
                    if key == "tags" and isinstance(value, list) and all(isinstance(v, str) for v in value):
                        choices[key] = tags
                    if key in choices:
                        values = value if isinstance(value, list) else [value]
                        require(all(isinstance(v, str) and v in choices[key] for v in values), f"Unknown {key}: {value}")
                    if key in {"entity", "from", "to", "source", "source_of_truth", "targets", "primary_assets", "supporting_assets", "required_upstream"}:
                        for asset in value if isinstance(value, list) else [value]:
                            require(isinstance(asset, str) and asset.startswith(prefix), f"Invalid asset: {asset}")
                            parts = asset[len(prefix):].split(".")
                            require(len(parts) in (1, 2) and parts[0] in schema_names and all(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", p) for p in parts), f"Invalid asset: {asset}")
                            if len(parts) == 2:
                                assets.add(".".join(parts))
    if repository is not None:
        validate_repository_assets(Path(repository), assets)
        validate_metric_columns(Path(repository), rows("metrics", "metrics"))
    return documents


def validate_metric_columns(repository, metrics):
    """Check identifiers against simple dbt mart projections, not arbitrary SQL."""
    models = {p.stem: p for p in (repository / "pipelines/dbt/models").rglob("*.sql")}
    keywords = {"COUNT", "SUM", "AVG", "MIN", "MAX", "COALESCE", "NULLIF",
                "FILTER", "WHERE", "GROUP", "BY", "AND", "OR", "NOT", "IS", "NULL", "DISTINCT"}
    for metric in metrics:
        source = metric["source"].split(".")
        expression = metric["expression"]
        require(not re.search(r";|--|/\*|\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b", expression, re.I),
                f"{metric['name']}: expected a measure expression, not a statement")
        if source[-2] != "analytics":
            continue
        path = models[source[-1]]
        projection = re.split(r"\bfrom\b", path.read_text(encoding="utf-8"), maxsplit=1, flags=re.I)[0]
        columns = set(re.findall(r"\bas\s+(\w+)", projection, re.I))
        columns.update(re.findall(r"^\s*(?:\w+\.)?(\w+)\s*,?\s*$", projection, re.M))
        identifiers = set(re.findall(r"\b[A-Za-z_]\w*\b", re.sub(r"'[^']*'", "", expression)))
        used = {v for v in identifiers if v.upper() not in keywords} | set(metric.get("dimensions", []))
        require(not used - columns, f"{metric['name']}: unknown source columns {sorted(used - columns)}")
        if source[-1].startswith("mart_market_"):
            require(not re.search(r"COUNT\s*\(\s*\*\s*\)", expression, re.I),
                    f"{metric['name']}: COUNT(*) counts summary rows, not listings")


def validate_repository_assets(repository, assets):
    import yaml
    known = {"analytics." + p.stem for p in (repository / "pipelines/dbt/models").rglob("*.sql")}
    for path in (repository / "pipelines/dbt/models").rglob("*.yml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for source in data.get("sources", []):
            for table in source.get("tables", []):
                known.add(source.get("schema", source["name"]) + "." + table.get("identifier", table["name"]))
    # Includes operational views and tables not exposed as dbt sources.
    for path in (repository / "database").rglob("*.sql"):
        known.update(re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_0-9]+\.[A-Za-z_0-9]+)", path.read_text(encoding="utf-8"), re.I))
    require(not assets - known, f"Unknown repository assets: {sorted(assets - known)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path)
    args = parser.parse_args()
    validate(Path(__file__).resolve().parents[1], args.repository)
    print("Governance configuration and references validated.")
