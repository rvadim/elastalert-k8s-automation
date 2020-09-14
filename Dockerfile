FROM python:3.7-slim

LABEL   description="Elastalert automation configuration" \
        maintainer="Dmitriy Kondyrev (dkondyrev@gmail.com)" \
        source="https://github.com/rvadim/elastalert-k8s-automation"

RUN groupadd --gid 1024 kubernetes \
    && useradd \
        --uid 1024 \
        --gid 1024 \
        --create-home \
        --shell /bin/bash \
        kubernetes

WORKDIR /home/kubernetes

ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD main.py ./
ADD config.py ./
ADD config_generator.py ./
ADD config_readers.py ./
ADD schemas ./schemas
ADD templates ./templates

CMD ["python3", "main.py"]
