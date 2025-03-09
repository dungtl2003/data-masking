.PHONY: all
all: up

.PHONY: up
up:
	echo "Starting the containers"
	docker compose -f compose.yaml up -d

.PHONY: down
down:
	echo "Stopping the containers"
	docker compose -f compose.yaml down

clean: down
	echo "Cleaning up the volumes"
	docker volume rm data-masking-db-data

.PHONY: access_db
access_db:
	docker container exec -it data-masking-db bash -c "mysql -u admin -ptestpass123 -h localhost data-masking"
