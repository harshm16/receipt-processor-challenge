FROM python:3.12-rc-bullseye

WORKDIR /app

RUN apt-get update -y

#File containing all dependencies
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

#File containing the webservice code
COPY app.py /app

#File containing the receipt schema
COPY given_schema.py /app

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]