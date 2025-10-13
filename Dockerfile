FROM python:3.13-slim
WORKDIR /app/src
COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
RUN pip install tox tox-docker
COPY . /app/
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
