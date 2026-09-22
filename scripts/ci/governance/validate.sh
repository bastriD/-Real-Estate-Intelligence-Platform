#!/bin/sh
# governance:validate / script. Sourced by GitLab; run from the project checkout.

echo "Validating Governance-as-Code files..."
python -m py_compile governance/scripts/main.py
python governance/scripts/validate_config.py --repository .
python -m json.tool governance/docs/governance-config.json > /dev/null
python -m json.tool governance/glossary/real_estate_glossary.json > /dev/null
python -m json.tool governance/ownership/real_estate_ownership.json > /dev/null
python -m json.tool governance/quality/real_estate_quality.json > /dev/null
python -m json.tool governance/tagging/real_estate_tags.json > /dev/null
python -m json.tool governance/tagging/real_estate_data_layers.json > /dev/null
python -m json.tool governance/metrics/real_estate_metrics.json > /dev/null
python -m json.tool governance/descriptions/real_estate_descriptions.json > /dev/null
echo "Governance-as-Code validation succeeded."
