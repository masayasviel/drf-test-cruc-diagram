# DRF test crud diagram

## venv

```sh
make venv
```

### activate

```sh
source .venv/bin/activate
deactivate
```

## Docker

```shell
make up
```

### migrate

```sh
# create migrate file
docker-compose run web python manage.py makemigrations myapp
# migrate
docker-compose run web python manage.py migrate
```

### php my admin

`http://localhost:8080`

### down

```shell
make down
make down_volume
docker images -qa | xargs docker rmi
```