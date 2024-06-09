build_modules:
	docker build -t module1 -f dockerfile.module1 .
	docker build -t module2 -f dockerfile.module2 .
	docker build -t fullparser -f dockerfile.fullparser .