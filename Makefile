# Docker
up:
	docker compose up -d

down:
	docker compose down

log:
	docker compose logs -f bot

rebuild:
	docker compose down -v
	docker compose build
	docker compose up -d
	docker compose exec bot alembic upgrade head
	docker compose logs -f

# Alembic
migrate:
	docker compose exec bot alembic upgrade head

revision:
	docker compose exec bot alembic revision --autogenerate -m "$(m)"
