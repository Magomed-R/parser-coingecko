run_postgres:
	docker run -d --name postgresql -p 5434:5432 -e POSTGRES_PASSWORD=dockerpostgres -e POSTGRES_USER=postgres -e POSTGRES_DB=coingecko -v "/home/magomed/Рабочий стол/work/parser-coingecko/pgdata_test":/var/lib/postgresql/data --network test postgres
run_module:
	docker run -d --name $(image) -v ./:/code --network test $(image)
build:
	docker build -t $(image) -f dockerfile.$(image) .