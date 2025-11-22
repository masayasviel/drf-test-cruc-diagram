FROM python
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r /app/requirements.txt && pip install tox
COPY . /app/
