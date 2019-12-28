.. _code_snippet:


*************
코드 조각
*************

소개
============

여기에는 당신이 트위피를 사용하는 데에 도움을 줄 몇 개의 코드 조각들이 있습니다. 마음껏 당신의 코드로 기여하거나 여기 있는 코드를 개선해주세요!

OAuth
=====

.. code-block :: python

   auth = tweepy.OAuthHandler("consumer_key", "consumer_secret")
   
   # 권한을 얻기 위해 트위터로 리다이렉트
   redirect_user(auth.get_authorization_url())
   
   # 접근 토큰을 얻음
   auth.get_access_token("verifier_value")
   
   # API 인스턴스를 생성
   api = tweepy.API(auth)

페이지 나누기
=============

.. code-block :: python

   # 인증된 사용자의 모든 친구 사이를 반복
   for friend in tweepy.Cursor(api.friends).items():
       # 여기서 friend의 처리
       process_friend(friend)
   
   # 타임라인의 가장 처음 200개의 status 사이를 반복
   for status in tweepy.Cursor(api.home_timeline).items(200):
       # 여기서 status의 처리
       process_status(status)

모든 팔로워를 팔로우
====================

이 코드는 인증된 사용자의 모든 팔로워를 팔로우 하도록 합니다.

.. code-block :: python

   for follower in tweepy.Cursor(api.followers).items():
       follower.follow()

커서 이용 속도 제한의 처리
==========================
   
커서는 커서 안의 ``next()``\ 메소드 안에서 ``RateLimitError``\ 를 일으킵니다. 이 오류는 커서를 반복자로 감쌈으로써 처리할 수 있습니다.
   
이 코드를 실행하면 당신이 팔로우한 모든 유저 중 300명 이하를 팔로우하는 유저들을 출력하고, 속도 제한에 도달할 때마다 15분간 기다릴 것입니다. 이 코드는 명백한 스팸봇을 제외하기 위한 예제입니다.
   
.. code-block :: python
   
   # 이 예제에서 처리자는 time.sleep(15*60)
   # 하지만 물론 당신이 원하는 어떤 방법으로든 처리 가능
   
   def limit_handled(cursor):
       while True:
           try:
               yield cursor.next()
           except tweepy.RateLimitError:
               time.sleep(15 * 60)
   
   for follower in limit_handled(tweepy.Cursor(api.followers).items()):
       if follower.friends_count < 300:
           print(follower.screen_name)
