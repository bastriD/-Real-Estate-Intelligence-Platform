#!/usr/bin/env python3

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("real-estate-governance")


# =============================================================================
# Paths
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILE = BASE_DIR / "docs" / "governance-config.json"


# =============================================================================
# Utility functions
# =============================================================================

def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not defined"
        )

    return value


def normalize_base_url(url: str) -> str:
    return url.rstrip("/")


# =============================================================================
# OpenMetadata REST client
# =============================================================================

class OpenMetadataClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = normalize_base_url(base_url)

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        payload: Any | None = None,
        params: dict[str, Any] | None = None,
        content_type: str | None = None,
        allow_status: tuple[int, ...] = (),
    ) -> requests.Response:

        headers = {}

        if content_type:
            headers["Content-Type"] = content_type

        response = self.session.request(
            method=method,
            url=self.url(endpoint),
            json=payload,
            params=params,
            headers=headers,
            timeout=30,
        )

        if response.status_code in allow_status:
            return response

        if not response.ok:
            logger.error(
                "OpenMetadata request failed: %s %s -> HTTP %s",
                method,
                endpoint,
                response.status_code,
            )

            logger.error(response.text)

            response.raise_for_status()

        return response

    def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        allow_status: tuple[int, ...] = (),
    ) -> requests.Response:

        return self.request(
            "GET",
            endpoint,
            params=params,
            allow_status=allow_status,
        )

    def put(
        self,
        endpoint: str,
        payload: Any,
    ) -> requests.Response:

        return self.request(
            "PUT",
            endpoint,
            payload=payload,
        )

    def post(
        self,
        endpoint: str,
        payload: Any,
        *,
        allow_status: tuple[int, ...] = (),
    ) -> requests.Response:

        return self.request(
            "POST",
            endpoint,
            payload=payload,
            allow_status=allow_status,
        )

    def patch(
        self,
        endpoint: str,
        operations: list[dict[str, Any]],
    ) -> requests.Response:

        return self.request(
            "PATCH",
            endpoint,
            payload=operations,
            content_type="application/json-patch+json",
        )

    # =========================================================================
    # Entity lookup
    # =========================================================================

    def get_by_name(
        self,
        entity_endpoint: str,
        fqn: str,
        *,
        fields: str | None = None,
    ) -> dict[str, Any] | None:

        encoded_fqn = quote(fqn, safe="")

        params = {}

        if fields:
            params["fields"] = fields

        response = self.get(
            f"{entity_endpoint}/name/{encoded_fqn}",
            params=params,
            allow_status=(404,),
        )

        if response.status_code == 404:
            return None

        return response.json()

    # =========================================================================
    # Glossary
    # =========================================================================

    def upsert_glossary(self, glossary: dict[str, Any]) -> dict[str, Any]:

        payload = {
            "name": glossary["name"],
            "displayName": glossary.get("display_name"),
            "description": glossary["description"],
            "mutuallyExclusive": glossary.get(
                "mutually_exclusive",
                False,
            ),
        }

        response = self.put(
            "/v1/glossaries",
            payload,
        )

        entity = response.json()

        logger.info(
            "Glossary applied: %s",
            entity.get("fullyQualifiedName", glossary["name"]),
        )

        return entity

    def upsert_glossary_term(
        self,
        glossary_name: str,
        term: dict[str, Any],
    ) -> dict[str, Any]:

        payload = {
            "name": term["name"],
            "displayName": term.get(
                "display_name",
                term["name"],
            ),
            "description": term["description"],
            "glossary": glossary_name,
        }

        synonyms = term.get("synonyms")

        if synonyms:
            payload["synonyms"] = synonyms

        response = self.put(
            "/v1/glossaryTerms",
            payload,
        )

        entity = response.json()

        logger.info(
            "Glossary term applied: %s",
            entity.get(
                "fullyQualifiedName",
                f"{glossary_name}.{term['name']}",
            ),
        )

        return entity

    # =========================================================================
    # Classification / Tags
    # =========================================================================

    def upsert_classification(
        self,
        classification: dict[str, Any],
    ) -> dict[str, Any]:

        payload = {
            "name": classification["name"],
            "displayName": classification.get(
                "display_name",
                classification["name"],
            ),
            "description": classification["description"],
            "mutuallyExclusive": classification.get(
                "mutually_exclusive",
                False,
            ),
        }

        response = self.put(
            "/v1/classifications",
            payload,
        )

        entity = response.json()

        logger.info(
            "Classification applied: %s",
            entity.get(
                "fullyQualifiedName",
                classification["name"],
            ),
        )

        return entity

    def upsert_tag(
        self,
        classification_name: str,
        tag: dict[str, Any],
    ) -> dict[str, Any]:

        payload = {
            "name": tag["name"],
            "displayName": tag.get(
                "display_name",
                tag["name"],
            ),
            "description": tag["description"],
            "classification": classification_name,
        }

        response = self.put(
            "/v1/tags",
            payload,
        )

        entity = response.json()

        logger.info(
            "Tag applied: %s",
            entity.get(
                "fullyQualifiedName",
                f"{classification_name}.{tag['name']}",
            ),
        )

        return entity

    # =========================================================================
    # Teams
    # =========================================================================

    def ensure_team(
        self,
        team: dict[str, Any],
    ) -> dict[str, Any]:

        existing = self.get_by_name(
            "/v1/teams",
            team["name"],
        )

        if existing:
            logger.info(
                "Team already exists: %s",
                team["name"],
            )

            return existing

        payload = {
            "name": team["name"],
            "displayName": team.get(
                "display_name",
                team["name"],
            ),
            "description": team["description"],
            "teamType": team.get(
                "team_type",
                "Group",
            ),
        }

        response = self.post(
            "/v1/teams",
            payload,
            allow_status=(409,),
        )

        if response.status_code == 409:
            existing = self.get_by_name(
                "/v1/teams",
                team["name"],
            )

            if existing:
                return existing

            raise RuntimeError(
                f"Team conflict but team cannot be retrieved: {team['name']}"
            )

        entity = response.json()

        logger.info(
            "Team created: %s",
            team["name"],
        )

        return entity

    # =========================================================================
    # Ownership
    # =========================================================================

    def apply_owner(
        self,
        entity_endpoint: str,
        fqn: str,
        team_name: str,
    ) -> None:

        entity = self.get_by_name(
            entity_endpoint,
            fqn,
            fields="owners",
        )

        if not entity:
            logger.warning(
                "Ownership target not found: %s",
                fqn,
            )

            return

        team = self.get_by_name(
            "/v1/teams",
            team_name,
        )

        if not team:
            raise RuntimeError(
                f"Owner team does not exist: {team_name}"
            )

        desired_owner = {
            "id": team["id"],
            "type": "team",
        }

        current_owners = entity.get("owners") or []

        owner_already_present = any(
            owner.get("id") == team["id"]
            for owner in current_owners
        )

        if owner_already_present:
            logger.info(
                "Ownership already correct: %s -> %s",
                fqn,
                team_name,
            )

            return

        operation = "replace" if current_owners else "add"

        patch = [
            {
                "op": operation,
                "path": "/owners",
                "value": [desired_owner],
            }
        ]

        self.patch(
            f"{entity_endpoint}/{entity['id']}",
            patch,
        )

        logger.info(
            "Ownership applied: %s -> %s",
            fqn,
            team_name,
        )

    # =========================================================================
    # Tags
    # =========================================================================

    def apply_tags_to_table(
        self,
        fqn: str,
        required_tags: list[str],
    ) -> None:

        entity = self.get_by_name(
            "/v1/tables",
            fqn,
            fields="tags",
        )

        if not entity:
            logger.warning(
                "Tagging target not found: %s",
                fqn,
            )

            return

        existing_tags = entity.get("tags") or []

        existing_fqns = {
            tag.get("tagFQN")
            for tag in existing_tags
            if tag.get("tagFQN")
        }

        new_tags = list(existing_tags)

        changed = False

        for tag_fqn in required_tags:

            if tag_fqn in existing_fqns:
                continue

            new_tags.append(
                {
                    "tagFQN": tag_fqn,
                    "labelType": "Manual",
                    "state": "Confirmed",
                }
            )

            existing_fqns.add(tag_fqn)

            changed = True

        if not changed:
            logger.info(
                "Required tags already present: %s",
                fqn,
            )

            return

        operation = "replace" if existing_tags else "add"

        patch = [
            {
                "op": operation,
                "path": "/tags",
                "value": new_tags,
            }
        ]

        self.patch(
            f"/v1/tables/{entity['id']}",
            patch,
        )

        logger.info(
            "Tags applied to: %s",
            fqn,
        )


# =============================================================================
# Governance engine
# =============================================================================

class GovernanceEngine:
    def __init__(
        self,
        config: dict[str, Any],
        client: OpenMetadataClient,
    ) -> None:

        self.config = config
        self.client = client

    # =========================================================================
    # Connectivity
    # =========================================================================

    def validate_connection(self) -> None:

        logger.info(
            "Checking OpenMetadata connectivity..."
        )

        response = self.client.get(
            "/v1/system/version"
        )

        version_payload = response.json()

        if isinstance(version_payload, dict):
            version = (
                version_payload.get("version")
                or version_payload.get("versionString")
                or version_payload
            )
        else:
            version = version_payload

        logger.info(
            "Connected to OpenMetadata: %s",
            version,
        )

    # =========================================================================
    # Glossary
    # =========================================================================

    def apply_glossary(self) -> None:

        governance_config = self.config["governance"]["glossary"]

        if not governance_config.get("enabled", False):
            logger.info("Glossary governance disabled")
            return

        path = BASE_DIR / governance_config["file"]

        data = load_json(path)

        glossary = data["glossary"]

        self.client.upsert_glossary(glossary)

        for term in data.get("terms", []):
            self.client.upsert_glossary_term(
                glossary["name"],
                term,
            )

        logger.info(
            "Glossary governance completed: %s terms",
            len(data.get("terms", [])),
        )

    # =========================================================================
    # Classifications
    # =========================================================================

    def apply_classifications(self) -> None:

        governance_config = self.config["governance"]["classification"]

        if not governance_config.get("enabled", False):
            logger.info("Classification governance disabled")
            return

        classification_count = 0
        tag_count = 0

        for relative_path in governance_config.get("files", []):

            path = BASE_DIR / relative_path

            data = load_json(path)

            for classification in data.get(
                "classifications",
                [],
            ):

                self.client.upsert_classification(
                    classification
                )

                classification_count += 1

                for tag in classification.get(
                    "tags",
                    [],
                ):

                    self.client.upsert_tag(
                        classification["name"],
                        tag,
                    )

                    tag_count += 1

        logger.info(
            "Classification governance completed: "
            "%s classifications, %s tags",
            classification_count,
            tag_count,
        )

    # =========================================================================
    # Ownership
    # =========================================================================

    def apply_ownership(self) -> None:

        governance_config = self.config["governance"]["ownership"]

        if not governance_config.get("enabled", False):
            logger.info("Ownership governance disabled")
            return

        for relative_path in governance_config.get("files", []):

            path = BASE_DIR / relative_path

            data = load_json(path)

            for team in data.get("teams", []):
                self.client.ensure_team(team)

            for rule in data.get(
                "ownership_rules",
                [],
            ):

                owner = rule["owner"]
                entity_type = rule["entity_type"]

                if entity_type == "table":
                    endpoint = "/v1/tables"

                elif entity_type == "schema":
                    endpoint = "/v1/databaseSchemas"

                else:
                    logger.warning(
                        "Unsupported ownership entity type: %s",
                        entity_type,
                    )

                    continue

                for target in rule.get("targets", []):

                    self.client.apply_owner(
                        endpoint,
                        target,
                        owner,
                    )

        logger.info(
            "Ownership governance completed"
        )

    # =========================================================================
    # Quality metadata
    # =========================================================================

    def apply_quality_governance(self) -> None:

        governance_config = self.config["governance"]["data_quality"]

        if not governance_config.get("enabled", False):
            logger.info("Data Quality governance disabled")
            return

        for relative_path in governance_config.get("files", []):

            path = BASE_DIR / relative_path

            data = load_json(path)

            for rule in data.get(
                "asset_rules",
                [],
            ):

                entity = rule["entity"]

                tags = rule.get(
                    "tags",
                    [],
                )

                self.client.apply_tags_to_table(
                    entity,
                    tags,
                )

            self.verify_required_lineage(
                data.get(
                    "lineage_requirements",
                    [],
                )
            )

        logger.info(
            "Data Quality governance completed"
        )

    # =========================================================================
    # Lineage verification
    # =========================================================================

    def verify_required_lineage(
        self,
        requirements: list[dict[str, Any]],
    ) -> None:

        for requirement in requirements:

            fqn = requirement["entity"]

            entity = self.client.get_by_name(
                "/v1/tables",
                fqn,
            )

            if not entity:
                logger.warning(
                    "Cannot verify lineage: entity not found: %s",
                    fqn,
                )

                continue

            entity_id = entity["id"]

            response = self.client.get(
                f"/v1/lineage/table/{entity_id}",
                allow_status=(404,),
            )

            if response.status_code == 404:
                logger.warning(
                    "No lineage found for: %s",
                    fqn,
                )

                continue

            lineage = response.json()

            upstream_nodes = lineage.get(
                "upstreamEdges",
                [],
            )

            nodes = lineage.get(
                "nodes",
                [],
            )

            node_names = {
                node.get("fullyQualifiedName")
                for node in nodes
                if node.get("fullyQualifiedName")
            }

            expected = set(
                requirement.get(
                    "required_upstream",
                    [],
                )
            )

            missing = expected - node_names

            if missing:
                logger.warning(
                    "Lineage verification incomplete for %s. Missing: %s",
                    fqn,
                    ", ".join(sorted(missing)),
                )

            else:
                logger.info(
                    "Required lineage verified: %s",
                    fqn,
                )

            logger.debug(
                "Lineage edge count for %s: %s",
                fqn,
                len(upstream_nodes),
            )

    # =========================================================================
    # Main execution
    # =========================================================================

    def run(self) -> None:

        project = self.config["project"]

        logger.info(
            "============================================================"
        )

        logger.info(
            "Real Estate Governance-as-Code"
        )

        logger.info(
            "Project: %s",
            project["display_name"],
        )

        logger.info(
            "Governance version: %s",
            project["governance_version"],
        )

        logger.info(
            "============================================================"
        )

        self.validate_connection()

        logger.info(
            "Step 1/4 - Applying business glossary"
        )
        self.apply_glossary()

        logger.info(
            "Step 2/4 - Applying classifications and tags"
        )
        self.apply_classifications()

        logger.info(
            "Step 3/4 - Applying ownership"
        )
        self.apply_ownership()

        logger.info(
            "Step 4/4 - Applying Data Quality governance"
        )
        self.apply_quality_governance()

        logger.info(
            "============================================================"
        )

        logger.info(
            "Governance-as-Code execution completed successfully"
        )

        logger.info(
            "============================================================"
        )


# =============================================================================
# Entrypoint
# =============================================================================

def main() -> int:

    try:
        config = load_json(CONFIG_FILE)

        openmetadata_config = config["openmetadata"]

        url_env = openmetadata_config["base_url_env"]
        token_env = openmetadata_config["token_env"]

        base_url = required_env(url_env)
        token = required_env(token_env)

        logger.info(
            "Governance configuration loaded: %s",
            CONFIG_FILE,
        )

        client = OpenMetadataClient(
            base_url=base_url,
            token=token,
        )

        engine = GovernanceEngine(
            config=config,
            client=client,
        )

        engine.run()

        return 0

    except KeyboardInterrupt:
        logger.warning(
            "Governance execution interrupted"
        )

        return 130

    except Exception as exc:
        logger.exception(
            "Governance execution failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())