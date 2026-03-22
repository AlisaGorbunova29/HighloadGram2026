quick-start:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run-backend:
	docker build -t highload-api .
	docker run --rm -p 8000:8000 highload-api

NGINX-up:
	docker compose up --build -d

NGINX-down:
	docker compose down -v

GET-backend:
	curl http://localhost:8080/api/history

GET-NGINX:		
	curl http://localhost:8080/api/history

POST-backend:
	curl -X POST http://localhost:8080/api/generate

POST-NGINX:
	curl -X POST http://localhost:8080/api/generate				

demonstration-balance:
	bash ./scripts/demonstration_balance.sh

ab-test:
	bash ./scripts/ab_test.sh
