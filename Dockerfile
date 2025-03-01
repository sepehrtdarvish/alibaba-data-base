ARG DOCKER_REG
FROM ${DOCKER_REG:-}python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

ADD ./requirements.txt /temp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /temp/requirements.txt

RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get install -y netcat-traditional
RUN apt-get install -y dos2unix

ADD ./src /home/alibaba
WORKDIR /home/alibaba

ADD ./docker-entrypoint.sh /tmp/docker-entrypoint.sh
RUN dos2unix /tmp/docker-entrypoint.sh && apt-get --purge remove -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN chmod +x /tmp/docker-entrypoint.sh

ENTRYPOINT ["bash", "/tmp/docker-entrypoint.sh"]