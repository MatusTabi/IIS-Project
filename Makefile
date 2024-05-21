APPLICATION_NAME ?= iis-app

build:
	docker build --tag ${APPLICATION_NAME} --no-cache .

up:
	docker-compose -f ./docker-compose.yaml up -d

restart:
	docker-compose -f ./docker-compose.yaml restart

down:
	docker-compose -f ./docker-compose.yaml down

db-migrate-init:
	docker-compose exec app /bin/sh -c ". /venv/bin/activate && cd ./app && flask db init"

db-migrate:
	docker-compose exec app /bin/sh -c ". /venv/bin/activate && cd ./app && flask db migrate"

db-upgrade:
	docker-compose exec app /bin/sh -c ". /venv/bin/activate && cd ./app && flask db upgrade"
