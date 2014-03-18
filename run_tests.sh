#! /usr/bin/env bash

if [[ $TRAVIS_BRANCH == "production" ]]; then
  nosetests -v --with-coverage tests.test_api tests.test_streaming tests.test_cursors tests.test_utils
else
  curl "https://dl.dropboxusercontent.com/u/231242/record.json" -o tests/record.json
  USE_REPLAY=1 nosetests -v tests.test_api tests.test_utils
fi
