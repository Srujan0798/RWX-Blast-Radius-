FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/tobymao/sqlglot.git /app/sqlglot && \
    cd /app/sqlglot && \
    git checkout eb11aec4be8cb2122afe713a4816662c3f0fb2fa

COPY src/ /app/src/
COPY maps/maps.json.z /app/maps/maps.json.z
COPY maps/type_index.json.z /app/maps/type_index.json.z
COPY maps/precomputed.json.z /app/maps/precomputed.json.z
COPY tests.json /app/tests.json

RUN mkdir -p /app/graph_artifacts && python -m src.ast_analyzer > /app/graph_artifacts/ast_metadata.json

RUN chmod -R a+rX /app/src /app/maps /app/graph_artifacts

CMD ["python", "-m", "src.main"]