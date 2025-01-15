FROM python:3.11-alpine

RUN apk update && apk add --virtual build-dependencies build-base gcc wget git

RUN mkdir /templates /static
ADD /templates /templates

ADD app.py /
ADD requirements.txt /
ADD titanic_model.joblib /

ADD /static /static

ADD utils.py /

RUN pip install -r requirements.txt
CMD ["python", "app.py"]
