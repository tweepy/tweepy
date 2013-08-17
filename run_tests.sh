#! /usr/bin/env bash

if [[ $TRAVIS_SECURE_ENV_VARS == "false" ]]; then
  USE_REPLAY=1 nosetests -v tests.test_api tests.test_utils
else
  nosetests -v tests.test_api tests.test_streaming tests.test_cursors tests.test_utils
fi
