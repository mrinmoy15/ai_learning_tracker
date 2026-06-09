.PHONY: help run-frontend start stop

help:
	@echo "Makefile targets:"
	@echo "  run-frontend  Build and serve frontend locally on port 3000 (no Docker)"
	@echo "  start         Build and run frontend in Docker on port 3000"
	@echo "  stop          Stop Docker container"

run-frontend:
	cd frontend && npm run dev

start:
	docker compose up -d --build

stop:
	docker compose down
