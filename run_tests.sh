#! /usr/bin/env bash

if [[ $TRAVIS_SECURE_ENV_VARS == "false" ]]; then
  curl https://www.dropbox.com/s/zsvzl6sl8gw8o6y/record.json -o tests/record.json
  USE_REPLAY=1 nosetests -v tests.test_api tests.test_utils
else
  nosetests -v --with-coverage tests.test_api tests.test_streaming tests.test_cursors tests.test_utils
fi
