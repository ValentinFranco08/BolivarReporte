.PHONY: dev backend frontend test test-python migrate seed

dev:
	./dev.sh

backend:
	cd backend && PYTHONPATH=. ../venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

frontend:
	cd frontend && npm run dev

test:
	$(MAKE) test-python
	cd frontend && npm test -- --run

test-python:
	PYTHONPATH=backend:. HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 venv/bin/python -m pytest backend/tests ml/test_forward.py ml/tests -q

migrate:
	venv/bin/python backend/scripts/manage.py migrate

seed:
	venv/bin/python backend/scripts/manage.py seed
