
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./api/app /code/api/app
COPY ./api/app/output /code/api/app/output
COPY ./api/app/output/model-last/ /code/api/app/output/model-last/
COPY ./api/app/output/model-last/tok2vec /code/api/app/output/model-last/tok2vec


CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "80"]

