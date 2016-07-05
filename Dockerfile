FROM ubuntu:latest

MAINTAINER Horia Coman <horia141@gmail.com>

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
            python3 \
            python3-pip \
            python3-dev \
            build-essential \
            libssl-dev \
            libffi-dev && \
    apt-get clean

RUN mkdir /ocelot
RUN mkdir /ocelot/pack
RUN mkdir /ocelot/var
RUN mkdir /ocelot/var/db
RUN mkdir /ocelot/var/db/identity

COPY . /ocelot/pack/identity

RUN pip3 install setuptools
RUN cd /ocelot/pack/identity && pip3 install -r requirements.txt
RUN cd /ocelot/pack/identity && python3 setup.py develop
RUN /ocelot/pack/identity/bin/migrate.sh
RUN gunicorn --check-config identity.server:app

RUN groupadd ocelot && \
    useradd -ms /bin/bash -g ocelot ocelot
RUN chown -R ocelot:ocelot /ocelot

WORKDIR /ocelot
EXPOSE 10000
USER ocelot
ENTRYPOINT ["gunicorn", "--config", "pack/identity/src/identity/config.py", "identity.server:app"]
