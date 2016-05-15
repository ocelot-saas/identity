#!/bin/sh

python setup.py sdist
curl -s -F package=@dist/`ls dist` https://$GEMFURY_KEY@push.fury.io/ocelot-saas/ > result
if [ -z "$(grep -e ok result)" ]
then
  exit 1
fi
