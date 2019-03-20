FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get -y install python3.6 python3-pip

WORKDIR /home/kubernetes

ADD requirements.txt ./
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]