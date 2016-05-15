FROM ubuntu:latest

MAINTAINER Horia Coman <horia141@gmail.com>

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends python python-pip && \
    apt-get clean

RUN mkdir /ocelot
RUN mkdir /ocelot/pack

COPY . /ocelot/pack/identity

RUN cd /ocelot/pack/identity && python setup.py install

RUN gunicorn --check-config identity.server:app

RUN groupadd ocelot && \
    useradd -ms /bin/bash -g ocelot ocelot
RUN chown -R ocelot:ocelot /ocelot

WORKDIR /ocelot
EXPOSE 10000
USER ocelot
ENTRYPOINT ["gunicorn", "--config", "pack/identity/src/identity/config.py", "identity.server:app"]
