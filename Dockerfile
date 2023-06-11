FROM amd64/ubuntu:20.04
RUN apt-get update && apt-get install -y tzdata && apt install -y python3 python3-pip
RUN apt install python3-dev libpq-dev nginx -y
ADD . .
RUN pip install -r ./requirements.txt
WORKDIR .
EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "fokusin_api.wsgi"]