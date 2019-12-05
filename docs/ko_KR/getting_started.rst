.. _getting_started:


***************
Tweepy 시작하기
***************

들어가며
========

Tweepy가 처음이라면, 이 문서를 참조하시는 것을 권장합니다.
이 문서의 목표는 여러분이 Tweepy를 어떻게 설정하고 롤링하는지
알게 되는 것입니다. 여기서는 세부적인 언급은 피할 것이며, 
몇 가지 중요한 기초 사항들만 다룰 것입니다.

Hello Tweepy
============

.. code-block :: python

   import tweepy

   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(access_token, access_token_secret)

   api = tweepy.API(auth)
   
   public_tweets = api.home_timeline()
   for tweet in public_tweets:
       print(tweet.text)

위 예제는 내 타임라인의 트윗을 다운로드하여, 콘솔에 각 트윗을 텍스트로써
출력하는 예제입니다. 참고로, 트위터는 모든 요청에 OAuth 인증을 요구합니다.
인증에 대한 보다 자세한 내용은 :ref:`auth_tutorial` 를 참고해주세요.

API
===

API 클래스는 트위터의 모든 RESTful API 메소드에 대한 접근을 지원합니다.
각 메소드는 다양한 매개변수를 전달받고 적절한 값을 반환할 수 있습니다.
보다 자세한 내용은 :ref:`API Reference <api_reference>` 를 참고해주세요.

모델 (Models)
=============

API 메소드를 호출할 때, 반환받는 것의 대부분은 Tweepy의 모델 클래스 인스턴스가
될 것입니다. 이는 애플리케이션에서 사용 가능한,
트위터로부터 반환받은 데이터를 포함할 것입니다.
예를 들어, 아래의 코드는 User 모델을 반환합니다::

   # Get the User object for twitter...
   user = api.get_user('twitter')

모델에는 다음과 같이, 사용 가능한 데이터 및 메소드가 포함되어 있습니다::

   print(user.screen_name)
   print(user.followers_count)
   for friend in user.friends():
      print(friend.screen_name)

모델에 대한 보다 자세한 내용은 ModelsReference를 참고해주세요.

