FROM python:3.7-slim

LABEL description="Elastalert automation configuration"
LABEL maintainer="Dmitriy Kondyrev (dkondyrev@gmail.com)"
LABEL source="https://github.com/rvadim/elastalert-k8s-automation"

WORKDIR /home/kubernetes

ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD main.py ./
ADD config.py ./
ADD schemas ./schemas
ADD templates ./templates

CMD ["python3", "main.py"]