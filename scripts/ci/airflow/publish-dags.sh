#!/bin/sh
# airflow:publish-dags / script. Sourced by GitLab; run from the project checkout.

git --version
test -f airflow-dags/real_estate_ingestion_dag.py
: "${DATA_PIPELINE_IMAGE:?Missing data-pipeline image build artifact}"
grep -F "$DATA_PIPELINE_IMAGE" airflow-dags/real_estate_ingestion_dag.py
rm -rf ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-airflow-dags
git clone \
  "https://${AIRFLOW_DAGS_GIT_USER}:${AIRFLOW_DAGS_GIT_TOKEN}@gitlab.local/root/airflow-dags.git" \
  ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-airflow-dags
mkdir -p ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-airflow-dags/dags
cp airflow-dags/*.py ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-airflow-dags/dags/
cd ${CI_PROJECT_DIR}/.ci-tmp/${CI_JOB_ID}/chasse-airflow-dags
git config user.name "chasse-immobiliere-ci"
git config user.email "gitlab-ci@lab.local"
git add dags/
if git diff --cached --quiet; then
  echo "No Airflow DAG changes to publish."
  exit 0
fi
git commit -m "deploy: publish real-estate Airflow DAGs"
git push origin main
