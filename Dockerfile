FROM ubuntu:latest

MAINTAINER Horia Coman <horia141@gmail.com>

# Install global packages.

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
            build-essential \
            libffi-dev \
            libpq-dev \
            libssl-dev \
            python3 \
            python3-dev \
            python3-pip \
            python3-setuptools && \
    apt-get clean

# Setup directory structure.

RUN mkdir /ocelot
RUN mkdir /ocelot/pack
RUN mkdir /ocelot/var

# Setup users and groups.

RUN groupadd ocelot && \
    useradd -ms /bin/bash -g ocelot ocelot

# Install package requirements.

COPY requirements.txt /ocelot/pack/requirements.txt
RUN cd /ocelot/pack && pip3 install -r requirements.txt

# Copy source code.

COPY . /ocelot/pack

# Setup the runtime environment for the application.

ENV ENV LOCAL
ENV ADDRESS 0.0.0.0
ENV PORT 10000
ENV MIGRATIONS_PATH /ocelot/pack/migrations
ENV DATABASE_URL postgresql://ocelot:ocelot@ocelot-postgres:5432/ocelot
ENV AUTH0_DOMAIN ocelot-saas.eu.auth0.com
ENV CLIENTS ocelot-inventory:10000,localhost:10000
ENV PYTHONPATH /ocelot/pack/src

RUN chown -R ocelot:ocelot /ocelot
VOLUME ["/ocelot/pack/src"]
WORKDIR /ocelot/pack/src
EXPOSE 10000
USER ocelot
ENTRYPOINT ["gunicorn", "--config", "identity/config.py", "identity.server:app"]
