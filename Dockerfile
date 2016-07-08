FROM ubuntu:latest

MAINTAINER Horia Coman <horia141@gmail.com>

# Install global packages.

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
            python3 \
            python3-pip \
            python3-dev \
            build-essential \
            libffi-dev \
	    libpq-dev \
            libssl-dev && \
    apt-get clean

RUN pip3 install setuptools

# Setup directory structure.

RUN mkdir /ocelot
RUN mkdir /ocelot/pack
RUN mkdir /ocelot/pack/identity
RUN mkdir /ocelot/var
RUN mkdir /ocelot/var/db
RUN mkdir /ocelot/var/db/identity

# Setup users and groups.

RUN groupadd ocelot && \
    useradd -ms /bin/bash -g ocelot ocelot
RUN chown -R ocelot:ocelot /ocelot

# Install package requirements.

COPY requirements.txt /ocelot/pack/identity/requirements.txt
RUN cd /ocelot/pack/identity && pip3 install -r requirements.txt

# Copy source code.

COPY . /ocelot/pack/identity

# Setup the runtime environment for the application.

ENV ENVIRON LOCAL
VOLUME ["/ocelot/pack/identity"]
WORKDIR /ocelot/pack/identity/src
EXPOSE 10000
USER ocelot
ENTRYPOINT ["gunicorn", "--config", "identity/config.py", "identity.server:app"]
