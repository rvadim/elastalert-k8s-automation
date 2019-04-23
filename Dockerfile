FROM python:3.7

LABEL description="Elastalert automation configuration"
LABEL maintainer="Dmitriy Kondyrev (dkondyrev@gmail.com)"
LABEL source="https://github.com/rvadim/elastalert-k8s-automation"

WORKDIR /home/kubernetes

ADD requirements.txt ./
RUN pip install -r requirements.txt

ADD main.py ./
ADD config.py ./
ADD ./schemas/admin_validation_schema.yaml ./schemas/

CMD ["python3", "main.py"]