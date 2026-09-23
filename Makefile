# Run everything from the repo root so relative paths (data/…) resolve the same way.
DBT = uv run dbt --no-use-colors
DBT_ARGS = --project-dir dbt --profiles-dir dbt

.PHONY: ingest build test docs app eval all

ingest:            ## raw xlsx -> DuckDB raw schema
	uv run python ingest/load_raw.py

build:             ## seeds + models + tests, in dependency order
	$(DBT) build $(DBT_ARGS)
	@cp dbt/target/run_results.json dbt/target/last_build_results.json  # `dbt docs generate` overwrites run_results.json

test:              ## python unit tests (no network)
	uv run pytest -q

docs:              ## lineage graph + column docs at http://localhost:8080
	$(DBT) docs generate $(DBT_ARGS) && $(DBT) docs serve $(DBT_ARGS)

app:               ## dashboard + natural-language assistant
	uv run streamlit run app/Home.py

eval:              ## run the Text-to-SQL eval set against the LLM (costs API calls)
	uv run python -m assistant.eval

all: ingest build
