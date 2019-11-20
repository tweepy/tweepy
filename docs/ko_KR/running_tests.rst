.. _running_tests:

***********
테스트하기
***********

이 단계들은 트위피 실행을 테스트하는 방법의 대략적인 설명입니다:

1. 트위피의 소스코드를 디렉토리에 다운로드하세요.

2. 다운로드한 소스에서 ``test`` 의 추가 정보를 사용하여 설치하세요. (예시: ``pip install .[test]`` ) 추가적으로 ``tox`` 와 ``coverage`` 의 사용이 필요하다면 ``dev`` 추가 정보와 같이 설치해주세요. (예시: ``pip install .[dev,test]`` )

3. 소스 디렉토리에서 ``python setup.py nonsetests`` 또는 간단하게 ``nonsetests`` 를 실행시키세요. ``dev`` 추가 정보를 포함했다면 ``coverage`` 를 볼 수 있으며, ``tox`` 를 이용해 다른 버전의 파이썬으로 실행할 수도 있습니다.

새로운 카세트를 기록하기 위해선 다음의 환경 변수들을 사용할 수 있어야 합니다:

``TWITTER_USERNAME``
``CONSUMER_KEY``
``CONSUMER_SECRET``
``ACCESS_KEY``
``ACCESS_SECRET``
``USE_REPLAY``

이는 단순히 ``USE_REPLAY`` 를 ``False`` 로 설정하고 앱과 계정의 자격 증명과 사용자의 이름을 제공하는 것입니다.