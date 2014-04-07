#!/bin/sh

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

if [ -z "$MOZ_ONYX_PROD" ]
then
    set -x
    echo "setting up development virtualenv"
    export MOZ_ONYX_DEV=1
else
    echo "setting up production virtualenv"
fi

rm -rf onyx-env

virtualenv --python=python2.7 --no-site-packages onyx-env
. onyx-env/bin/activate


python setup.py develop
