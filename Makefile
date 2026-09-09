.PHONY: dev backend frontend test

dev:
	./dev.sh

backend:
	cd backend && PYTHONPATH=. ../venv/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && PYTHONPATH=. ../venv/bin/pytest -v
	cd frontend && npm test -- --run
