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
        raise FileNotFoundError(
            f"Configuration file not found: {path}"
        )

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
    def __init__(
        self,
        base_url: str,
        token: str,
    ) -> None:

        self.base_url = normalize_base_url(base_url)

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def url(
        self,
        endpoint: str,
    ) -> str:

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

            logger.error(
                response.text
            )

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

    def apply_tags_to_column(
        self,
        table_fqn: str,
        column_name: str,
        required_tags: list[str],
    ) -> str:

        entity = self.get_by_name(
            "/v1/tables",
            table_fqn,
            fields="columns,tags",
        )

        if not entity:
            logger.warning(
                "Column tagging table target not found: %s",
                table_fqn,
            )
            return "missing"

        for tag_fqn in required_tags:
            tag_entity = self.get_by_name(
                "/v1/tags",
                tag_fqn,
            )

            if not tag_entity:
                raise RuntimeError(
                    f"Classification tag does not exist: {tag_fqn}"
                )

        columns = entity.get("columns") or []

        column_index = None
        column = None

        for index, current_column in enumerate(columns):
            if current_column.get("name") == column_name:
                column_index = index
                column = current_column
                break

        if column is None or column_index is None:
            logger.warning(
                "Column tagging target not found: %s.%s",
                table_fqn,
                column_name,
            )
            return "missing"

        existing_tags = column.get("tags") or []

        existing_fqns = {
            tag.get("tagFQN")
            for tag in existing_tags
            if tag.get("tagFQN")
        }

        desired_tags = list(existing_tags)
        changed = False

        for tag_fqn in required_tags:
            if tag_fqn in existing_fqns:
                continue

            desired_tags.append(
                {
                    "tagFQN": tag_fqn,
                    "source": "Classification",
                    "labelType": "Manual",
                    "state": "Confirmed",
                }
            )

            existing_fqns.add(tag_fqn)
            changed = True

        if not changed:
            logger.info(
                "Privacy tags already assigned to column: %s.%s",
                table_fqn,
                column_name,
            )
            return "already"

        operation = "replace" if existing_tags else "add"

        patch = [
            {
                "op": operation,
                "path": f"/columns/{column_index}/tags",
                "value": desired_tags,
            }
        ]

        self.patch(
            f"/v1/tables/{entity['id']}",
            patch,
        )

        logger.info(
            "Privacy tags assigned to column: %s.%s -> %s",
            table_fqn,
            column_name,
            ", ".join(required_tags),
        )

        return "changed"
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

        encoded_fqn = quote(
            fqn,
            safe="",
        )

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
    # Table discovery
    # =========================================================================

    def list_tables_in_schema(
        self,
        schema_fqn: str,
    ) -> list[dict[str, Any]]:

        tables: list[dict[str, Any]] = []

        params: dict[str, Any] = {
            "databaseSchema": schema_fqn,
            "limit": 100,
        }

        while True:
            response = self.get(
                "/v1/tables",
                params=params,
            )

            payload = response.json()

            current_tables = payload.get(
                "data",
                [],
            )

            tables.extend(
                current_tables
            )

            paging = payload.get(
                "paging",
                {},
            )

            after = paging.get(
                "after"
            )

            if not after:
                break

            params["after"] = after

        return tables

    # =========================================================================
    # Domains
    # =========================================================================

    def upsert_domain(
        self,
        domain: dict[str, Any],
        parent_fqn: str | None = None,
    ) -> dict[str, Any]:

        payload = {
            "name": domain["name"],
            "displayName": domain.get(
                "display_name",
                domain["name"],
            ),
            "description": domain["description"],
            "domainType": domain.get(
                "domain_type",
                "Aggregate",
            ),
        }

        if parent_fqn:
            payload["parent"] = parent_fqn

        response = self.put(
            "/v1/domains",
            payload,
        )

        entity = response.json()

        logger.info(
            "Domain applied: %s",
            entity.get(
                "fullyQualifiedName",
                domain["name"],
            ),
        )

        return entity

    def assign_domain_to_entity(
        self,
        entity_endpoint: str,
        fqn: str,
        domain_name: str,
    ) -> None:

        entity = self.get_by_name(
            entity_endpoint,
            fqn,
            fields="domains",
        )

        if not entity:
            logger.warning(
                "Domain assignment target not found: %s",
                fqn,
            )

            return

        domain = self.get_by_name(
            "/v1/domains",
            domain_name,
        )

        if not domain:
            raise RuntimeError(
                f"Domain does not exist: {domain_name}"
            )

        current_domains = entity.get(
            "domains"
        ) or []

        domain_already_present = any(
            current_domain.get("id") == domain["id"]
            for current_domain in current_domains
        )

        if domain_already_present:
            logger.info(
                "Domain already assigned: %s -> %s",
                fqn,
                domain_name,
            )

            return

        desired_domains = list(
            current_domains
        )

        desired_domains.append(
            {
                "id": domain["id"],
                "type": "domain",
            }
        )

        operation = (
            "replace"
            if current_domains
            else "add"
        )

        patch = [
            {
                "op": operation,
                "path": "/domains",
                "value": desired_domains,
            }
        ]

        self.patch(
            f"{entity_endpoint}/{entity['id']}",
            patch,
        )

        logger.info(
            "Domain assigned: %s -> %s",
            fqn,
            domain_name,
        )

    # =========================================================================
    # Glossary definitions
    # =========================================================================

    def upsert_glossary(
        self,
        glossary: dict[str, Any],
    ) -> dict[str, Any]:

        payload = {
            "name": glossary["name"],
            "displayName": glossary.get(
                "display_name"
            ),
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
            entity.get(
                "fullyQualifiedName",
                glossary["name"],
            ),
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

        synonyms = term.get(
            "synonyms"
        )

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
    # Glossary assignment helpers
    # =========================================================================

    def ensure_glossary_term_exists(
        self,
        term_fqn: str,
    ) -> dict[str, Any]:

        term = self.get_by_name(
            "/v1/glossaryTerms",
            term_fqn,
        )

        if not term:
            raise RuntimeError(
                f"Glossary term does not exist: {term_fqn}"
            )

        return term

    def apply_glossary_terms_to_table(
        self,
        fqn: str,
        required_terms: list[str],
    ) -> str:

        entity = self.get_by_name(
            "/v1/tables",
            fqn,
            fields="tags",
        )

        if not entity:
            logger.warning(
                "Glossary table target not found: %s",
                fqn,
            )

            return "missing"

        for term_fqn in required_terms:
            self.ensure_glossary_term_exists(
                term_fqn
            )

        existing_tags = entity.get(
            "tags"
        ) or []

        existing_fqns = {
            tag.get("tagFQN")
            for tag in existing_tags
            if tag.get("tagFQN")
        }

        desired_tags = list(
            existing_tags
        )

        changed = False

        for term_fqn in required_terms:

            if term_fqn in existing_fqns:
                continue

            desired_tags.append(
                {
                    "tagFQN": term_fqn,
                    "source": "Glossary",
                    "labelType": "Manual",
                    "state": "Confirmed",
                }
            )

            existing_fqns.add(
                term_fqn
            )

            changed = True

        if not changed:
            logger.info(
                "Glossary terms already assigned to table: %s -> %s",
                fqn,
                ", ".join(
                    required_terms
                ),
            )

            return "already"

        operation = (
            "replace"
            if existing_tags
            else "add"
        )

        patch = [
            {
                "op": operation,
                "path": "/tags",
                "value": desired_tags,
            }
        ]

        self.patch(
            f"/v1/tables/{entity['id']}",
            patch,
        )

        logger.info(
            "Glossary terms assigned to table: %s -> %s",
            fqn,
            ", ".join(
                required_terms
            ),
        )

        return "changed"

    def apply_glossary_terms_to_column(
        self,
        table_fqn: str,
        column_name: str,
        required_terms: list[str],
    ) -> str:

        entity = self.get_by_name(
            "/v1/tables",
            table_fqn,
            fields="columns,tags",
        )

        if not entity:
            logger.warning(
                "Glossary column table target not found: %s",
                table_fqn,
            )

            return "missing"

        for term_fqn in required_terms:
            self.ensure_glossary_term_exists(
                term_fqn
            )

        columns = entity.get(
            "columns"
        ) or []

        column_index: int | None = None
        column: dict[str, Any] | None = None

        for index, current_column in enumerate(
            columns
        ):
            if current_column.get(
                "name"
            ) == column_name:
                column_index = index
                column = current_column
                break

        if column is None or column_index is None:
            logger.warning(
                "Glossary column target not found: %s.%s",
                table_fqn,
                column_name,
            )

            return "missing"

        existing_tags = column.get(
            "tags"
        ) or []

        existing_fqns = {
            tag.get("tagFQN")
            for tag in existing_tags
            if tag.get("tagFQN")
        }

        desired_tags = list(
            existing_tags
        )

        changed = False

        for term_fqn in required_terms:

            if term_fqn in existing_fqns:
                continue

            desired_tags.append(
                {
                    "tagFQN": term_fqn,
                    "labelType": "Manual",
                    "state": "Confirmed",
                    "source": "Glossary"
                }
            )

            existing_fqns.add(
                term_fqn
            )

            changed = True

        if not changed:
            logger.info(
                "Glossary terms already assigned to column: "
                "%s.%s -> %s",
                table_fqn,
                column_name,
                ", ".join(
                    required_terms
                ),
            )

            return "already"

        operation = (
            "replace"
            if existing_tags
            else "add"
        )

        patch = [
            {
                "op": operation,
                "path": f"/columns/{column_index}/tags",
                "value": desired_tags,
            }
        ]

        self.patch(
            f"/v1/tables/{entity['id']}",
            patch,
        )

        logger.info(
            "Glossary terms assigned to column: %s.%s -> %s",
            table_fqn,
            column_name,
            ", ".join(
                required_terms
            ),
        )

        return "changed"

    # =========================================================================
    # Classification / Tags
    # =========================================================================

    def upsert_metric(
        self,
        metric: dict[str, Any],
        *,
        owner_id: str | None = None,
        domain_fqn: str | None = None,
    ) -> dict[str, Any]:

        metric_type = metric.get(
            "metric_type",
            "COUNT",
        ).upper()

        granularity = metric.get(
            "granularity",
            "DAY",
        ).upper()

        unit = metric.get(
            "unit",
            "OTHER",
        ).upper()

        standard_units = {
            "COUNT",
            "DOLLARS",
            "PERCENTAGE",
            "OTHER",
        }

        if unit in standard_units:
            unit_of_measurement = unit
            custom_unit = None
        else:
            unit_of_measurement = "OTHER"
            custom_unit = unit

        payload: dict[str, Any] = {
            "name": metric["name"],
            "displayName": metric.get(
                "display_name",
                metric["name"],
            ),
            "description": metric["description"],
            "metricExpression": {
                "language": metric.get(
                    "expression_language",
                    "SQL",
                ),
                "code": metric["expression"],
            },
            "metricType": metric_type,
            "granularity": granularity,
            "unitOfMeasurement": unit_of_measurement,
        }

        if custom_unit:
            payload["customUnitOfMeasurement"] = custom_unit

        if owner_id:
            payload["owners"] = [
                {
                    "id": owner_id,
                    "type": "team",
                }
            ]

        if domain_fqn:
            payload["domains"] = [
                domain_fqn
            ]

        response = self.put(
            "/v1/metrics",
            payload,
        )

        entity = response.json()

        logger.info(
            "Metric applied: %s",
            entity.get(
                "fullyQualifiedName",
                metric["name"],
            ),
        )

        return entity

    # =========================================================================
    # Metrics
    # =========================================================================

    def upsert_metric(
        self,
        metric: dict[str, Any],
        *,
        owner_id: str | None = None,
        domain_fqn: str | None = None,
    ) -> dict[str, Any]:

        metric_type = metric.get(
            "metric_type",
            "COUNT",
        ).upper()

        granularity = metric.get(
            "granularity",
            "DAY",
        ).upper()

        unit = metric.get(
            "unit",
            "OTHER",
        ).upper()

        standard_units = {
            "COUNT",
            "DOLLARS",
            "PERCENTAGE",
            "OTHER",
        }

        if unit in standard_units:
            unit_of_measurement = unit
            custom_unit = None
        else:
            unit_of_measurement = "OTHER"
            custom_unit = unit

        payload: dict[str, Any] = {
            "name": metric["name"],
            "displayName": metric.get(
                "display_name",
                metric["name"],
            ),
            "description": metric["description"],
            "metricExpression": {
                "language": metric.get(
                    "expression_language",
                    "SQL",
                ),
                "code": metric["expression"],
            },
            "metricType": metric_type,
            "granularity": granularity,
            "unitOfMeasurement": unit_of_measurement,
        }

        if custom_unit:
            payload["customUnitOfMeasurement"] = custom_unit

        if owner_id:
            payload["owners"] = [
                {
                    "id": owner_id,
                    "type": "team",
                }
            ]

        if domain_fqn:
            payload["domains"] = [
                domain_fqn
            ]

        response = self.put(
            "/v1/metrics",
            payload,
        )

        entity = response.json()

        logger.info(
            "Metric applied: %s",
            entity.get(
                "fullyQualifiedName",
                metric["name"],
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
                "Team conflict but team cannot "
                f"be retrieved: {team['name']}"
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

        current_owners = entity.get(
            "owners"
        ) or []

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

        operation = (
            "replace"
            if current_owners
            else "add"
        )

        patch = [
            {
                "op": operation,
                "path": "/owners",
                "value": [
                    desired_owner
                ],
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
    # Generic table tags
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

        existing_tags = entity.get(
            "tags"
        ) or []

        existing_fqns = {
            tag.get("tagFQN")
            for tag in existing_tags
            if tag.get("tagFQN")
        }

        new_tags = list(
            existing_tags
        )

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

            existing_fqns.add(
                tag_fqn
            )

            changed = True

        if not changed:
            logger.info(
                "Required tags already present: %s",
                fqn,
            )

            return

        operation = (
            "replace"
            if existing_tags
            else "add"
        )

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

    # =========================================================================
    # Data Layer tags
    # =========================================================================

    def apply_data_layer_to_table(
        self,
        fqn: str,
        desired_tag_fqn: str,
    ) -> str:

        entity = self.get_by_name(
            "/v1/tables",
            fqn,
            fields="tags",
        )

        if not entity:
            logger.warning(
                "DataLayer target not found: %s",
                fqn,
            )
            return "missing"

        existing_tags = entity.get(
            "tags"
        ) or []

        data_layer_prefix = (
            "RealEstateDataLayer."
        )

        current_data_layer_tags = [
            tag
            for tag in existing_tags
            if (
                tag.get("tagFQN")
                and tag["tagFQN"].startswith(
                    data_layer_prefix
                )
            )
        ]

        current_data_layer_fqns = {
            tag["tagFQN"]
            for tag in current_data_layer_tags
        }

        if current_data_layer_fqns == {
            desired_tag_fqn
        }:
            logger.info(
                "DataLayer already correct: %s -> %s",
                fqn,
                desired_tag_fqn,
            )
            return "already"

        preserved_tags = [
            tag
            for tag in existing_tags
            if not (
                tag.get("tagFQN")
                and tag["tagFQN"].startswith(
                    data_layer_prefix
                )
            )
        ]

        desired_tags = list(
            preserved_tags
        )

        desired_tags.append(
            {
                "tagFQN": desired_tag_fqn,
                "labelType": "Manual",
                "state": "Confirmed",
            }
        )

        operation = (
            "replace"
            if existing_tags
            else "add"
        )

        patch = [
            {
                "op": operation,
                "path": "/tags",
                "value": desired_tags,
            }
        ]

        self.patch(
            f"/v1/tables/{entity['id']}",
            patch,
        )

        if current_data_layer_fqns:
            logger.info(
                "DataLayer corrected: %s | %s -> %s",
                fqn,
                ", ".join(
                    sorted(
                        current_data_layer_fqns
                    )
                ),
                desired_tag_fqn,
            )
        else:
            logger.info(
                "DataLayer applied: %s -> %s",
                fqn,
                desired_tag_fqn,
            )

        return "changed"
  
  
  
  
  # =========================================================================
    # Data Products
    # =========================================================================


    # =========================================================================
    # Data Products
    # =========================================================================

       

    def upsert_data_product(
        self,
        data_product: dict[str, Any],
        *,
        owner_id: str | None = None,
    ) -> dict[str, Any]:

        domain_fqn = data_product["domain"]

        domain = self.get_by_name(
            "/v1/domains",
            domain_fqn,
        )

        if not domain:
            raise RuntimeError(
                f"Data Product domain does not exist: {domain_fqn}"
            )

        payload: dict[str, Any] = {
            "name": data_product["name"],
            "displayName": data_product.get(
                "display_name",
                data_product["name"],
            ),
            "description": data_product["description"],
            "domains": [
                domain_fqn
            ],
        }

        if owner_id:
            payload["owners"] = [
                {
                    "id": owner_id,
                    "type": "team",
                }
            ]

        entity = self.put(
            "/v1/dataProducts",
            payload,
        ).json()

        logger.info(
            "Data Product applied: %s",
            entity.get(
                "fullyQualifiedName",
                data_product["name"],
            ),
        )

        return entity

    def add_assets_to_data_product(
        self,
        data_product_name: str,
        data_product_id: str,
        asset_fqns: list[str],
    ) -> tuple[int, int]:

        data_product = self.get(
            f"/v1/dataProducts/{data_product_id}",
            params={"fields": "assets"},
        ).json()

        existing_asset_ids = {
            asset.get("id")
            for asset in data_product.get("assets") or []
            if asset.get("id")
        }

        assets_to_add: list[dict[str, str]] = []
        already_count = 0

        for asset_fqn in asset_fqns:
            asset = self.get_by_name(
                "/v1/tables",
                asset_fqn,
            )

            if not asset:
                raise RuntimeError(
                    f"Data Product asset does not exist: {asset_fqn}"
                )

            if asset["id"] in existing_asset_ids:
                logger.info(
                    "Data Product asset already assigned: %s",
                    asset_fqn,
                )

                already_count += 1
                continue

            assets_to_add.append(
                {
                    "id": asset["id"],
                    "type": "table",
                }
            )

            existing_asset_ids.add(
                asset["id"]
            )

        if assets_to_add:
            payload = {
                "assets": assets_to_add
            }

            self.put(
                f"/v1/dataProducts/{data_product_name}/assets/add",
                payload,
            )

            for asset_fqn in asset_fqns:
                logger.info(
                    "Data Product asset assigned: %s",
                    asset_fqn,
                )

        return len(assets_to_add), already_count

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

    def validate_connection(
        self,
    ) -> None:

        logger.info(
            "Checking OpenMetadata connectivity..."
        )

        response = self.client.get(
            "/v1/system/version"
        )

        version_payload = response.json()

        if isinstance(
            version_payload,
            dict,
        ):
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
    # Domains
    # =========================================================================

    def apply_domains(
        self,
    ) -> None:

        governance_config = (
            self.config["governance"].get(
                "domains",
                {},
            )
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Domain governance disabled"
            )

            return

        created_domains: dict[
            str,
            dict[str, Any],
        ] = {}

        for relative_path in governance_config.get(
            "files",
            [],
        ):

            path = (
                BASE_DIR
                / relative_path
            )

            data = load_json(
                path
            )

            domains = data.get(
                "domains",
                [],
            )

            # -----------------------------------------------------------------
            # First pass: root domains
            # -----------------------------------------------------------------

            for domain in domains:

                if domain.get(
                    "parent"
                ):
                    continue

                entity = (
                    self.client.upsert_domain(
                        domain
                    )
                )

                created_domains[
                    domain["name"]
                ] = entity

            # -----------------------------------------------------------------
            # Second pass: child domains
            # -----------------------------------------------------------------

            for domain in domains:

                parent_name = domain.get(
                    "parent"
                )

                if not parent_name:
                    continue

                parent = (
                    created_domains.get(
                        parent_name
                    )
                    or self.client.get_by_name(
                        "/v1/domains",
                        parent_name,
                    )
                )

                if not parent:
                    raise RuntimeError(
                        "Parent domain does not exist: "
                        f"{parent_name}"
                    )

                parent_fqn = parent.get(
                    "fullyQualifiedName"
                )

                if not parent_fqn:
                    raise RuntimeError(
                        "Parent domain does not expose "
                        f"a fullyQualifiedName: {parent_name}"
                    )

                entity = (
                    self.client.upsert_domain(
                        domain,
                        parent_fqn=parent_fqn,
                    )
                )

                created_domains[
                    domain["name"]
                ] = entity

            # -----------------------------------------------------------------
            # Third pass: assignments
            # -----------------------------------------------------------------

            for assignment in data.get(
                "assignments",
                [],
            ):

                domain_name = assignment["domain"]

                domain_entity = (
                    created_domains.get(
                        domain_name
                    )
                    or self.client.get_by_name(
                        "/v1/domains",
                        domain_name,
                    )
                )

                if not domain_entity:
                    raise RuntimeError(
                        f"Domain does not exist: {domain_name}"
                    )

                domain_fqn = domain_entity.get(
                    "fullyQualifiedName"
                )

                if not domain_fqn:
                    raise RuntimeError(
                        "Domain has no fullyQualifiedName: "
                        f"{domain_name}"
                    )

                entity_type = assignment[
                    "entity_type"
                ]

                if entity_type == "databaseSchema":
                    endpoint = "/v1/databaseSchemas"

                elif entity_type == "table":
                    endpoint = "/v1/tables"

                elif entity_type == "database":
                    endpoint = "/v1/databases"

                else:
                    logger.warning(
                        "Unsupported domain assignment "
                        "entity type: %s",
                        entity_type,
                    )

                    continue

                for target in assignment.get(
                    "targets",
                    [],
                ):

                    self.client.assign_domain_to_entity(
                        endpoint,
                        target,
                        domain_fqn,
                    )

        logger.info(
            "Domain governance completed"
        )

    # =========================================================================
    # Glossary definitions
    # =========================================================================

    def apply_glossary(
        self,
    ) -> None:

        governance_config = (
            self.config[
                "governance"
            ][
                "glossary"
            ]
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Glossary governance disabled"
            )

            return

        path = (
            BASE_DIR
            / governance_config["file"]
        )

        data = load_json(
            path
        )

        glossary = data[
            "glossary"
        ]

        self.client.upsert_glossary(
            glossary
        )

        for term in data.get(
            "terms",
            [],
        ):

            self.client.upsert_glossary_term(
                glossary["name"],
                term,
            )

        logger.info(
            "Glossary governance completed: %s terms",
            len(
                data.get(
                    "terms",
                    [],
                )
            ),
        )

    # =========================================================================
    # Classifications
    # =========================================================================

    def apply_classifications(
        self,
    ) -> None:

        governance_config = (
            self.config[
                "governance"
            ][
                "classification"
            ]
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Classification governance disabled"
            )

            return

        classification_count = 0
        tag_count = 0

        for relative_path in governance_config.get(
            "files",
            [],
        ):

            path = (
                BASE_DIR
                / relative_path
            )

            data = load_json(
                path
            )

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
    # Data Layer Governance
    # =========================================================================

    def apply_data_layers(
        self,
    ) -> None:

        governance_config = (
            self.config["governance"].get(
                "data_layer",
                {},
            )
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Data Layer governance disabled"
            )

            return

        openmetadata_config = self.config[
            "openmetadata"
        ]

        database_service = openmetadata_config[
            "database_service"
        ]

        database = openmetadata_config[
            "database"
        ]

        changed_count = 0
        already_count = 0
        missing_count = 0
        processed_count = 0

        for relative_path in governance_config.get(
            "files",
            [],
        ):

            path = (
                BASE_DIR
                / relative_path
            )

            data = load_json(
                path
            )

            for rule in data.get(
                "layer_rules",
                [],
            ):

                schema_name = rule[
                    "schema"
                ]

                tag_fqn = rule[
                    "tag"
                ]

                tag_entity = self.client.get_by_name(
                    "/v1/tags",
                    tag_fqn,
                )

                if not tag_entity:
                    raise RuntimeError(
                        "DataLayer tag does not exist: "
                        f"{tag_fqn}"
                    )

                schema_fqn = (
                    f"{database_service}."
                    f"{database}."
                    f"{schema_name}"
                )

                schema_entity = self.client.get_by_name(
                    "/v1/databaseSchemas",
                    schema_fqn,
                )

                if not schema_entity:
                    logger.warning(
                        "DataLayer schema not found: %s",
                        schema_fqn,
                    )

                    missing_count += 1
                    continue

                tables = (
                    self.client.list_tables_in_schema(
                        schema_fqn
                    )
                )

                if not tables:
                    logger.warning(
                        "No catalogued tables found for "
                        "DataLayer schema: %s",
                        schema_fqn,
                    )

                    continue

                logger.info(
                    "Applying %s to schema %s: %s tables discovered",
                    tag_fqn,
                    schema_fqn,
                    len(tables),
                )

                for table in tables:

                    table_fqn = table.get(
                        "fullyQualifiedName"
                    )

                    if not table_fqn:
                        logger.warning(
                            "OpenMetadata table without "
                            "fullyQualifiedName in schema: %s",
                            schema_fqn,
                        )

                        continue

                    result = (
                        self.client.apply_data_layer_to_table(
                            table_fqn,
                            tag_fqn,
                        )
                    )

                    processed_count += 1

                    if result == "changed":
                        changed_count += 1

                    elif result == "already":
                        already_count += 1

                    elif result == "missing":
                        missing_count += 1

        logger.info(
            "Data Layer governance completed: "
            "%s processed, %s changed, %s already correct, %s missing",
            processed_count,
            changed_count,
            already_count,
            missing_count,
        )

    # =========================================================================
    # Ownership
    # =========================================================================

    def apply_ownership(
        self,
    ) -> None:

        governance_config = (
            self.config[
                "governance"
            ][
                "ownership"
            ]
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Ownership governance disabled"
            )

            return

        for relative_path in governance_config.get(
            "files",
            [],
        ):

            path = (
                BASE_DIR
                / relative_path
            )

            data = load_json(
                path
            )

            for team in data.get(
                "teams",
                [],
            ):

                self.client.ensure_team(
                    team
                )

            for rule in data.get(
                "ownership_rules",
                [],
            ):

                owner = rule[
                    "owner"
                ]

                entity_type = rule[
                    "entity_type"
                ]

                if entity_type == "table":
                    endpoint = "/v1/tables"

                elif entity_type == "schema":
                    endpoint = "/v1/databaseSchemas"

                else:
                    logger.warning(
                        "Unsupported ownership "
                        "entity type: %s",
                        entity_type,
                    )

                    continue

                for target in rule.get(
                    "targets",
                    [],
                ):

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

    def apply_quality_governance(
        self,
    ) -> None:

        governance_config = (
            self.config[
                "governance"
            ][
                "data_quality"
            ]
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Data Quality governance disabled"
            )

            return

        for relative_path in governance_config.get(
            "files",
            [],
        ):

            path = (
                BASE_DIR
                / relative_path
            )

            data = load_json(
                path
            )

            for rule in data.get(
                "asset_rules",
                [],
            ):

                entity = rule[
                    "entity"
                ]

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
        requirements: list[
            dict[str, Any]
        ],
    ) -> None:

        for requirement in requirements:

            fqn = requirement[
                "entity"
            ]

            entity = self.client.get_by_name(
                "/v1/tables",
                fqn,
            )

            if not entity:
                logger.warning(
                    "Cannot verify lineage: "
                    "entity not found: %s",
                    fqn,
                )

                continue

            entity_id = entity[
                "id"
            ]

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
                node.get(
                    "fullyQualifiedName"
                )
                for node in nodes
                if node.get(
                    "fullyQualifiedName"
                )
            }

            expected = set(
                requirement.get(
                    "required_upstream",
                    [],
                )
            )

            missing = (
                expected
                - node_names
            )

            if missing:
                logger.warning(
                    "Lineage verification incomplete "
                    "for %s. Missing: %s",
                    fqn,
                    ", ".join(
                        sorted(
                            missing
                        )
                    ),
                )

            else:
                logger.info(
                    "Required lineage verified: %s",
                    fqn,
                )

            logger.debug(
                "Lineage edge count for %s: %s",
                fqn,
                len(
                    upstream_nodes
                ),
            )

    # =========================================================================
    # Glossary assignment governance
    # =========================================================================

    def apply_glossary_assignments(
        self,
    ) -> None:

        governance_config = (
            self.config["governance"].get(
                "glossary_assignments",
                {},
            )
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Glossary assignment governance disabled"
            )

            return

        processed_count = 0
        changed_count = 0
        already_count = 0
        missing_count = 0

        for relative_path in governance_config.get(
            "files",
            [],
        ):

            path = (
                BASE_DIR
                / relative_path
            )

            data = load_json(
                path
            )

            # -----------------------------------------------------------------
            # Table-level assignments
            # -----------------------------------------------------------------

            for assignment in data.get(
                "table_assignments",
                [],
            ):

                entity_fqn = assignment[
                    "entity"
                ]

                terms = assignment.get(
                    "terms",
                    [],
                )

                if not terms:
                    logger.warning(
                        "Glossary table assignment without terms: %s",
                        entity_fqn,
                    )

                    continue

                result = (
                    self.client.apply_glossary_terms_to_table(
                        entity_fqn,
                        terms,
                    )
                )

                processed_count += 1

                if result == "changed":
                    changed_count += 1

                elif result == "already":
                    already_count += 1

                elif result == "missing":
                    missing_count += 1

            # -----------------------------------------------------------------
            # Column-level assignments
            # -----------------------------------------------------------------

            for assignment in data.get(
                "column_assignments",
                [],
            ):

                entity_fqn = assignment[
                    "entity"
                ]

                column_name = assignment[
                    "column"
                ]

                terms = assignment.get(
                    "terms",
                    [],
                )

                if not terms:
                    logger.warning(
                        "Glossary column assignment without terms: "
                        "%s.%s",
                        entity_fqn,
                        column_name,
                    )

                    continue

                result = (
                    self.client.apply_glossary_terms_to_column(
                        entity_fqn,
                        column_name,
                        terms,
                    )
                )

                processed_count += 1

                if result == "changed":
                    changed_count += 1

                elif result == "already":
                    already_count += 1

                elif result == "missing":
                    missing_count += 1

        logger.info(
            "Glossary assignment governance completed: "
            "%s processed, %s changed, "
            "%s already correct, %s missing",
            processed_count,
            changed_count,
            already_count,
            missing_count,
        )

    # =========================================================================
    # Privacy assignments
    # =========================================================================

    def apply_privacy_assignments(
        self,
    ) -> None:

        governance_config = (
            self.config["governance"].get(
                "privacy_assignments",
                {},
            )
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Privacy assignment governance disabled"
            )
            return

        processed_count = 0
        changed_count = 0
        already_count = 0
        missing_count = 0

        for relative_path in governance_config.get(
            "files",
            [],
        ):
            path = BASE_DIR / relative_path
            data = load_json(path)

            for assignment in data.get(
                "column_assignments",
                [],
            ):
                entity_fqn = assignment["entity"]
                column_name = assignment["column"]
                tags = assignment.get("tags", [])

                if not tags:
                    logger.warning(
                        "Privacy column assignment without tags: %s.%s",
                        entity_fqn,
                        column_name,
                    )
                    continue

                result = self.client.apply_tags_to_column(
                    entity_fqn,
                    column_name,
                    tags,
                )

                processed_count += 1

                if result == "changed":
                    changed_count += 1
                elif result == "already":
                    already_count += 1
                elif result == "missing":
                    missing_count += 1

        logger.info(
            "Privacy assignment governance completed: "
            "%s processed, %s changed, "
            "%s already correct, %s missing",
            processed_count,
            changed_count,
            already_count,
            missing_count,
        )

    # =========================================================================
    # Data Products
    # =========================================================================

    def apply_data_products(
        self,
    ) -> None:

        governance_config = self.config["governance"].get(
            "data_products",
            {},
        )

        if not governance_config.get("enabled", False):
            logger.info("Data Product governance disabled")
            return

        processed_count = 0
        added_asset_count = 0
        already_asset_count = 0

        for relative_path in governance_config.get("files", []):
            data = load_json(BASE_DIR / relative_path)

            for data_product in data.get("data_products", []):
                domain_fqn = data_product["domain"]
                domain = self.client.get_by_name(
                    "/v1/domains",
                    domain_fqn,
                )

                if not domain:
                    raise RuntimeError(
                        "Data Product domain does not exist: "
                        f"{domain_fqn}"
                    )

                owner_name = data_product.get(
                    "governance",
                    {},
                ).get("owner")
                owner_id = None

                if owner_name:
                    owner = self.client.get_by_name(
                        "/v1/teams",
                        owner_name,
                    )

                    if not owner:
                        raise RuntimeError(
                            "Data Product owner team does not exist: "
                            f"{owner_name}"
                        )

                    owner_id = owner["id"]

                entity = self.client.upsert_data_product(
                    data_product,
                    owner_id=owner_id,
                )

                all_assets = list(
                    dict.fromkeys(
                        data_product.get("primary_assets", [])
                        + data_product.get("supporting_assets", [])
                    )
                )

                added, already = self.client.add_assets_to_data_product(
                    entity["name"],
                    entity["id"],
                    all_assets,
                )

                processed_count += 1
                added_asset_count += added
                already_asset_count += already

        logger.info(
            "Data Product governance completed: "
            "%s products processed, "
            "%s assets added, "
            "%s assets already assigned",
            processed_count,
            added_asset_count,
            already_asset_count,
        )

    # =========================================================================
    # Metrics
    # =========================================================================

    def apply_metrics(
        self,
    ) -> None:

        governance_config = self.config["governance"].get(
            "metrics",
            {},
        )

        if not governance_config.get(
            "enabled",
            False,
        ):
            logger.info(
                "Metric governance disabled"
            )
            return

        processed_count = 0

        for relative_path in governance_config.get(
            "files",
            [],
        ):
            path = BASE_DIR / relative_path
            data = load_json(path)

            for metric in data.get(
                "metrics",
                [],
            ):
                owner_id = None
                domain_fqn = None

                owner_name = metric.get("owner")

                if owner_name:
                    owner = self.client.get_by_name(
                        "/v1/teams",
                        owner_name,
                    )

                    if not owner:
                        raise RuntimeError(
                            "Metric owner team does not exist: "
                            f"{owner_name}"
                        )

                    owner_id = owner["id"]

                domain_name = metric.get("domain")

                if domain_name:
                    domain = self.client.get_by_name(
                        "/v1/domains",
                        domain_name,
                    )

                    if not domain:
                        raise RuntimeError(
                            "Metric domain does not exist: "
                            f"{domain_name}"
                        )

                    domain_fqn = (
                        domain.get("fullyQualifiedName")
                        or domain_name
                    )

                source_fqn = metric.get("source")

                if source_fqn:
                    source = self.client.get_by_name(
                        "/v1/tables",
                        source_fqn,
                    )

                    if not source:
                        logger.warning(
                            "Metric source asset not found in "
                            "OpenMetadata: %s",
                            source_fqn,
                        )

                for term_fqn in metric.get(
                    "glossary_terms",
                    [],
                ):
                    self.client.ensure_glossary_term_exists(
                        term_fqn
                    )

                self.client.upsert_metric(
                    metric,
                    owner_id=owner_id,
                    domain_fqn=domain_fqn,
                )

                processed_count += 1

        logger.info(
            "Metric governance completed: %s metrics processed",
            processed_count,
        )

    # =========================================================================
    # Main execution
    # =========================================================================

    def run(
        self,
    ) -> None:

        project = self.config[
            "project"
        ]

        logger.info(
            "============================================================"
        )

        logger.info(
            "Real Estate Governance-as-Code"
        )

        logger.info(
            "Project: %s",
            project[
                "display_name"
            ],
        )

        logger.info(
            "Governance version: %s",
            project[
                "governance_version"
            ],
        )

        logger.info(
            "============================================================"
        )

        self.validate_connection()

        logger.info(
            "Step 1/10 - Applying domains"
        )

        self.apply_domains()

        logger.info(
            "Step 2/10 - Applying business glossary"
        )

        self.apply_glossary()

        logger.info(
            "Step 3/10 - Applying classifications and tags"
        )

        self.apply_classifications()

        logger.info(
            "Step 4/10 - Applying Data Layer governance"
        )

        self.apply_data_layers()

        logger.info(
            "Step 5/10 - Applying ownership"
        )

        self.apply_ownership()

        logger.info(
            "Step 6/10 - Applying Data Quality governance"
        )

        self.apply_quality_governance()

        logger.info(
            "Step 7/10 - Applying glossary assignments"
        )

        self.apply_glossary_assignments()

        logger.info(
            "Step 8/10 - Applying privacy assignments"
        )

        self.apply_privacy_assignments()

        logger.info(
            "Step 9/10 - Applying Data Products"
        )

        self.apply_data_products()

        logger.info(
            "Step 10/10 - Applying Metrics"
        )

        self.apply_metrics()

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
        config = load_json(
            CONFIG_FILE
        )

        openmetadata_config = config[
            "openmetadata"
        ]

        url_env = openmetadata_config[
            "base_url_env"
        ]

        token_env = openmetadata_config[
            "token_env"
        ]

        base_url = required_env(
            url_env
        )

        token = required_env(
            token_env
        )

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
    sys.exit(
        main()
    )
