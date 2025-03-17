.PHONY: up
up:
	$(info ==================== up docker compose ====================)
	docker-compose -f docker-compose.yaml up -d

.PHONY: down
down:
	$(info ==================== down docker compose ====================)
	docker-compose -f docker-compose.yaml down
