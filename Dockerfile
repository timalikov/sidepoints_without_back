FROM python:3.12 AS backend-builder

WORKDIR /app
COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.12-slim
WORKDIR /app

COPY --from=backend-builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=backend-builder /app /app

CMD [ "python", "./main.py" ]