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

```shell
# create migrate file
docker-compose run web python ./src/manage.py makemigrations myapp
# migrate
docker-compose run web python ./src/manage.py migrate
```

### php my admin

`http://localhost:8080`

### down

```shell
make down
make down_volume
docker images -qa | xargs docker rmi
```

### test

```shell
# make up後に行う
docker-compose run web pytest
```
