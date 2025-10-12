down:
	docker-compose down

down_volume:
	docker-compose down -v

test:
	docker-compose run --rm web tox -- -vv $(TEST_TARGET)

venv:
	python3 -m venv .venv
	cat ./requirements.txt | grep -v mysql | xargs ./.venv/bin/pip install
	./.venv/bin/pip install pytest pytest-django factory-boy
