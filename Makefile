.PHONY: demo test lint run web start install-hooks

install-hooks:
	@pip install pre-commit -q && pre-commit install

# Une commande : setup + lancement (pour celui qui clone le repo)
start:
	@chmod +x scripts/start.sh 2>/dev/null; bash scripts/start.sh

run:
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd apps/web && npm run dev

demo: start

test:
	pytest tests/ -v

test-web:
	cd apps/web && npm run test

test-cov:
	pytest tests/ -v --cov=po_agent --cov=apps --cov-report=term-missing --cov-fail-under=35

lint:
	ruff check .
format:
	ruff format .
