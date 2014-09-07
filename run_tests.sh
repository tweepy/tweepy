#! /usr/bin/env bash

if [[ $TRAVIS_BRANCH == "production" ]]; then
  nosetests -v --with-coverage tests.test_api tests.test_streaming tests.test_cursors tests.test_utils
else
  USE_REPLAY=1 nosetests -v --with-coverage tests.test_api tests.test_utils
fi
