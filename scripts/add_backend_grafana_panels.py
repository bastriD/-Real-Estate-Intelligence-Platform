import json
from pathlib import Path


path = Path(
    "observability/grafana/dashboards/"
    "real-estate-business-platform.json"
)

with path.open("r", encoding="utf-8") as file:
    dashboard = json.load(file)

prometheus = {
    "type": "prometheus",
    "uid": "prometheus",
}

panel_31 = {
    "datasource": prometheus,
    "description": (
        "Current Prometheus scrape availability of the "
        "Real Estate Backend API."
    ),
    "fieldConfig": {
        "defaults": {
            "mappings": [],
            "thresholds": {
                "mode": "absolute",
                "steps": [
                    {
                        "color": "red",
                        "value": None,
                    },
                    {
                        "color": "green",
                        "value": 1,
                    },
                ],
            },
            "unit": "none",
        },
        "overrides": [],
    },
    "gridPos": {
        "h": 8,
        "w": 6,
        "x": 0,
        "y": 92,
    },
    "id": 31,
    "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
            "calcs": ["lastNotNull"],
            "fields": "",
            "values": False,
        },
        "textMode": "auto",
    },
    "pluginVersion": "12.4.3",
    "targets": [
        {
            "datasource": prometheus,
            "editorMode": "code",
            "expr": 'up{job="real-estate-backend"}',
            "instant": True,
            "legendFormat": "Backend",
            "range": False,
            "refId": "A",
        }
    ],
    "title": "Backend API Availability",
    "type": "stat",
}

panel_32 = {
    "datasource": prometheus,
    "description": (
        "Backend API request throughput measured "
        "over a 5-minute window."
    ),
    "fieldConfig": {
        "defaults": {
            "unit": "reqps",
        },
        "overrides": [],
    },
    "gridPos": {
        "h": 8,
        "w": 18,
        "x": 6,
        "y": 92,
    },
    "id": 32,
    "options": {
        "legend": {
            "calcs": [
                "lastNotNull",
                "mean",
            ],
            "displayMode": "table",
            "placement": "bottom",
            "showLegend": True,
        },
        "tooltip": {
            "mode": "single",
            "sort": "none",
        },
    },
    "pluginVersion": "12.4.3",
    "targets": [
        {
            "datasource": prometheus,
            "editorMode": "code",
            "expr": (
                'sum(rate(real_estate_api_requests_total{'
                'job="real-estate-backend",'
                'path!~"/(health|ready|metrics)"'
                '}[5m]))'
            ),
            "instant": False,
            "legendFormat": "Requests / second",
            "range": True,
            "refId": "A",
        }
    ],
    "title": "Backend API Request Rate",
    "type": "timeseries",
}

panel_33 = {
    "datasource": prometheus,
    "description": (
        "Percentage of Backend API requests returning "
        "HTTP 5xx responses."
    ),
    "fieldConfig": {
        "defaults": {
            "unit": "percent",
            "min": 0,
        },
        "overrides": [],
    },
    "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 100,
    },
    "id": 33,
    "options": {
        "legend": {
            "calcs": [
                "lastNotNull",
                "mean",
                "max",
            ],
            "displayMode": "table",
            "placement": "bottom",
            "showLegend": True,
        },
        "tooltip": {
            "mode": "single",
            "sort": "none",
        },
    },
    "pluginVersion": "12.4.3",
    "targets": [
        {
            "datasource": prometheus,
            "editorMode": "code",
            "expr": (
                "100 * "
                "sum(rate(real_estate_api_requests_total{"
                'job="real-estate-backend",'
                'status_code=~"5..",'
                'path!~"/(health|ready|metrics)"'
                "}[5m])) "
                "/ "
                "clamp_min("
                "sum(rate(real_estate_api_requests_total{"
                'job="real-estate-backend",'
                'path!~"/(health|ready|metrics)"'
                "}[5m])), "
                "0.001"
                ")"
            ),
            "instant": False,
            "legendFormat": "5xx rate",
            "range": True,
            "refId": "A",
        }
    ],
    "title": "Backend API 5xx Error Rate",
    "type": "timeseries",
}

panel_34 = {
    "datasource": prometheus,
    "description": (
        "95th percentile response time for "
        "Backend API business requests."
    ),
    "fieldConfig": {
        "defaults": {
            "unit": "s",
            "decimals": 3,
        },
        "overrides": [],
    },
    "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 100,
    },
    "id": 34,
    "options": {
        "legend": {
            "calcs": [
                "lastNotNull",
                "mean",
                "max",
            ],
            "displayMode": "table",
            "placement": "bottom",
            "showLegend": True,
        },
        "tooltip": {
            "mode": "single",
            "sort": "none",
        },
    },
    "pluginVersion": "12.4.3",
    "targets": [
        {
            "datasource": prometheus,
            "editorMode": "code",
            "expr": (
                "histogram_quantile("
                "0.95, "
                "sum by (le) ("
                "rate("
                "real_estate_api_request_duration_seconds_bucket{"
                'job="real-estate-backend",'
                'path!~"/(health|ready|metrics)"'
                "}[5m]"
                ")"
                ")"
                ")"
            ),
            "instant": False,
            "legendFormat": "p95 latency",
            "range": True,
            "refId": "A",
        }
    ],
    "title": "Backend API p95 Latency",
    "type": "timeseries",
}

existing_ids = {
    panel.get("id")
    for panel in dashboard.get("panels", [])
}

for panel in [
    panel_31,
    panel_32,
    panel_33,
    panel_34,
]:
    if panel["id"] not in existing_ids:
        dashboard["panels"].append(panel)

dashboard["version"] = 8

with path.open("w", encoding="utf-8", newline="\n") as file:
    json.dump(
        dashboard,
        file,
        ensure_ascii=False,
        indent=2,
    )
    file.write("\n")

print(
    f"Updated {path} "
    f"with {len(dashboard['panels'])} panels"
)