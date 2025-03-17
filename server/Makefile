DOCKER_USERNAME ?= ilikeblue
APPLICATION_NAME ?= data-masking-server
SERVER_PORT ?= 80
CURRENT_DIR = $(shell pwd)

.PHONY: run
run:
	./scripts/run_with_env.sh python app/main.py

.PHONY: dbuild
dbuild:
	$(info ==================== building dockerfile ====================)
	docker buildx build --platform linux/amd64 --tag ${DOCKER_USERNAME}/${APPLICATION_NAME}:latest -f Dockerfile .

dbuild_debug:
	$(info ==================== building dockerfile with debug on ====================)
	docker buildx build --debug --progress=plain --no-cache --platform linux/amd64 --tag ${DOCKER_USERNAME}/${APPLICATION_NAME}:latest -f Dockerfile . 
