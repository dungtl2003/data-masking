BUILD_ARGS ?= NEXT_PUBLIC_API_ENDPOINT=http://localhost:8000/api/v1
DOCKER_USERNAME ?= ilikeblue
APPLICATION_NAME ?= data-masking-client
SERVER_PORT ?= 80
CURRENT_DIR = $(shell pwd)

.PHONY: dbuild
dbuild:
	$(info ==================== building dockerfile ====================)
	docker buildx build --build-arg $(BUILD_ARGS) --platform linux/amd64 --tag ${DOCKER_USERNAME}/${APPLICATION_NAME}:latest -f Dockerfile .

dbuild_debug:
	$(info ==================== building dockerfile with debug on ====================)
	docker buildx build --build-arg $(BUILD_ARGS) --debug --progress=plain --no-cache --platform linux/amd64 --tag ${DOCKER_USERNAME}/${APPLICATION_NAME}:latest -f Dockerfile . 
