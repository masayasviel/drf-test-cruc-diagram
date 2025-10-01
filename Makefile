down:
	docker-compose down

down_volume:
	docker-compose down -v

venv:
	python3 -m venv .venv
	cat ./requirements.txt | grep -v mysql | xargs ./.venv/bin/pip install
