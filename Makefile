.PHONY: dev backend frontend test

dev:
	./dev.sh

backend:
	cd backend && PYTHONPATH=. ../venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

frontend:
	cd frontend && npm run dev

test:
	cd backend && PYTHONPATH=. ../venv/bin/pytest -v
	cd frontend && npm test -- --run
