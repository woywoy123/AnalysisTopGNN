FROM ubuntu:latest
MAINTAINER woywoy123

ENV DEBIAN_FRONTEND=noninteractive
RUN useradd --create-home --shell /bin/bash AnalysisG
WORKDIR /home/AnalysisG

COPY . ./
RUN apt-get update
RUN apt-get install -y python3-pip gcc g++ wget lsb-release 
RUN chmod -R 0750 ./setup-scripts/docker-script.sh
RUN setup-scripts/docker-script.sh
RUN apt-get clean all

RUN pip install --upgrade pip setuptools wheel torch
RUN pip install -v .
RUN config_pyami
RUN install_pyc

RUN ln -s /usr/bin/python3 /usr/bin/python
USER AnalysisG

CMD ["bash"]


