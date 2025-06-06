FLASK_APP=app.py

.PHONY: dev migrate

dev:
	flask run --debug

migrate:
	flask db upgrade
