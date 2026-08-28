FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY docs /app/docs
COPY glossary /app/glossary
COPY ownership /app/ownership
COPY quality /app/quality
COPY scripts /app/scripts
COPY tagging /app/tagging
COPY domains /app/domains
COPY data-products /app/data-products
COPY lineage /app/lineage
COPY metrics /app/metrics

COPY apply-governance.sh /app/apply-governance.sh

RUN chmod +x /app/apply-governance.sh

ENTRYPOINT ["/app/apply-governance.sh"]