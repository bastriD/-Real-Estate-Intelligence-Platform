#!/bin/sh
# observability:validate / script. Sourced by GitLab; run from the project checkout.

python --version
test -f deploy/observability/application.yaml
test -f deploy/observability/grafana-datasource.yaml.template
test -f observability/grafana/dashboards/real-estate-business-platform.json
test -f observability/grafana/dashboards/real-estate-data-quality.json
test -f observability/alerts/real-estate-prometheus-rules.yaml
python - <<'PY'
import json
from pathlib import Path

dashboards = {
    "observability/grafana/dashboards/real-estate-business-platform.json": {
        "uid": "real-estate-platform",
        "title": "Real Estate â€” Business KPIs & Platform",
    },
    "observability/grafana/dashboards/real-estate-data-quality.json": {
        "uid": "real-estate-data-quality",
        "title": "Real Estate â€” Data Quality",
    },
}

for path_str, expected in dashboards.items():
    path = Path(path_str)

    dashboard = json.loads(
        path.read_text(encoding="utf-8")
    )

    required = [
        "title",
        "uid",
        "panels",
    ]

    for key in required:
        if key not in dashboard:
            raise SystemExit(
                f"{path}: missing Grafana dashboard field: {key}"
            )

    if dashboard["uid"] != expected["uid"]:
        raise SystemExit(
            f"{path}: unexpected Grafana dashboard UID: "
            f"{dashboard['uid']}"
        )

    if dashboard["title"] != expected["title"]:
        raise SystemExit(
            f"{path}: unexpected Grafana dashboard title: "
            f"{dashboard['title']!r}"
        )

    if not isinstance(
        dashboard["panels"],
        list,
    ):
        raise SystemExit(
            f"{path}: Grafana dashboard panels must be a list"
        )

    if len(dashboard["panels"]) == 0:
        raise SystemExit(
            f"{path}: Grafana dashboard must contain panels"
        )

    print(
        f"Grafana dashboard validation passed: {path}"
    )

    print(
        f"Title: {dashboard['title']}"
    )

    print(
        f"UID: {dashboard['uid']}"
    )

    print(
        f"Panels: {len(dashboard['panels'])}"
    )

print("All Grafana dashboards validated successfully.")
PY
python - <<'PY'
from pathlib import Path
import sys

path = Path(
    "observability/alerts/"
    "real-estate-prometheus-rules.yaml"
)

content = path.read_text(
    encoding="utf-8"
)

required_strings = [
    "apiVersion: monitoring.coreos.com/v1",
    "kind: PrometheusRule",
    "name: real-estate-data-platform",
    "namespace: monitoring",
    "release: monitoring",
    "RealEstateDataQualityLayerFailed",
    "RealEstateDataQualityStale",
    "RealEstateMetricsCollectionFailed",
    "RealEstateMetricsCollectionStale",
]

missing = [
    item
    for item in required_strings
    if item not in content
]

if missing:
    print(
        "PrometheusRule validation failed.",
        file=sys.stderr,
    )

    for item in missing:
        print(
            f"Missing expected content: {item}",
            file=sys.stderr,
        )

    raise SystemExit(1)

print(
    "PrometheusRule source validation passed."
)
PY
python -m py_compile \
  observability/metrics/collect_metrics.py \
  observability/metrics/dq_runner.py \
  observability/metrics/metrics_exporter.py
echo "Observability validation succeeded."
