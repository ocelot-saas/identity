FROM ubuntu:latest

MAINTAINER Horia Coman <horia141@gmail.com>

RUN apt-get update -y
RUN apt-get install -y --no-install-recommends python python-pip
RUN apt-get clean

RUN mkdir /ocelot
RUN mkdir /ocelot/pack

COPY . /ocelot/pack/identity

RUN cd /ocelot/pack/identity && python setup.py install

RUN groupadd ocelot && \
    useradd -ms /bin/bash -g ocelot ocelot
RUN chown -R ocelot:ocelot /ocelot

WORKDIR /ocelot
EXPOSE 10000
USER ocelot
ENTRYPOINT ["gunicorn", "identity:app"]
