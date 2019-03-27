FROM armv7/armhf-ubuntu:14.04

MAINTAINER Byeonggil-Jung "jbkcose@gmail.com"

RUN apt-get update -y
RUN apt-get install -y git python3 python3-dev python3-pip build-essential

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

COPY . /app

WORKDIR /app

ENTRYPOINT ["python3"]
CMD ["bmc_app.py"]
