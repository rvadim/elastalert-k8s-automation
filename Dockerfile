FROM python:3.7

LABEL description="Elastalert automation configuration"
LABEL maintainer="Dmitriy Kondyrev (dkondyrev@gmail.com)"
LABEL source="https://github.com/rvadim/elastalert-k8s-automation"

WORKDIR /home/kubernetes

ADD main.py ./
ADD requirements.txt ./
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]