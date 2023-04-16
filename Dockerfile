FROM python:3.9

WORKDIR /blackwidowapi

COPY ./requirements.txt /blackwidowapi/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /blackwidowapi/requirements.txt

COPY ./api/app /blackwidowapi/app
COPY ./api/app/output/model-last blackwidowapi/app/output/model-last


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]