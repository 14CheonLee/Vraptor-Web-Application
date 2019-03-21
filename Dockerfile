FROM armv7/armhf-ubuntu:14.04

MAINTAINER Byeonggil-Jung "jbkcose@gmail.com"

RUN apt-get update -y
RUN apt-get install -y git python3 python3-dev python3-pip build-essential

RUN git clone https://github.com/14CheonLee/Vraptor-Web-Application.git

WORKDIR /Vraptor-Web-Application

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["bmc_app.py"]
