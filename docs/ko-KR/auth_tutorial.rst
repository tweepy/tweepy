.. _auth_tutorial:


***********************
인증 지침
***********************

들어가며
============

Tweepy는 OAuth 1a(응용 프로그램-사용자)와 OAuth 2a(응용프로그램 전용)을 모두 지원합니다.
인증은 tweepy.AuthHandler 클래스를 통해 처리합니다.

OAuth 1a 인증
=======================

Tweepy는 OAuth 1a를 가능한 편리하게 제공하기 위해 노력합니다.
과정을 시작하기 위해선 클라이언트 응용 프로그램을 등록할 필요가 있습니다.
새로운 응용 프로그램을 생성하고 끝내기 위해선 consumer key와 secret을 가져야 합니다.
이 2가지는 필요하므로 잘 보관합시다.

다음 단계는 OAuthHandler 인스턴스를 생성하는 것입니다.
여기서 이전 단락에서 주어진 consumer key와 secret을 전달합니다::

   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

웹 응용 프로그램이 있고 동적일 필요가 있는 콜백 URL을 사용하는 경우에는 다음과 같이 전달합니다::

   auth = tweepy.OAuthHandler(consumer_key, consumer_secret,
   callback_url)

콜백 URL을 변경하지 않을 경우, 응용 프로그램의 프로필을 설정할 때 twitter.com에서 정적으로 설정하는 것이 가장 좋습니다.

기초적인 인증과는 다르게, 우리는 API를 사용하기 전에 다음의 "OAuth 1a Dance"과정이 필요합니다.
다음의 과정을 완벽하게 따라해야 합니다.

#. 트위터에서 요청 토큰을 가져오세요.

#. 사용자를 twitter.com으로 리다이렉트 시켜서 응용 프로그램을 인증하세요.

#. 콜백을 이용하는 경우, 트위터는 사용자를 우리에게 리다이렉트 할 것입니다. 그렇지 않으면 사용자가 수동으로 검증 코드를 제공해야만 합니다.

#. 공인된 요청 토큰을 접근을 위한 토큰으로 교체하세요.

그러면, 동작을 위해 우리의 요청 토큰을 가져 옵시다::

   try:
       redirect_url = auth.get_authorization_url()
   except tweepy.TweepError:
       print('에러! 요청 토큰을 받는데 실패했습니다.')

이 명령은 트위터를 통하여 토큰을 요청하고, 사용자가 인증을 위해 리다이렉트 해야하는 인증 URL을 반환합니다.
만약 데스크탑 응용 프로그램인 경우, 사용자가 돌아올 때까지 OAuthHandler 인스턴스를 유지할 수 있습니다.
따라서 요청 토큰은 콜백 URL 요청에 필요하므로 세션에 저장해야 합니다.
다음은 요청한 토큰을 세션에 저장하는 예시 코드입니다::

   session.set('request_token', auth.request_token['oauth_token'])

이제 get_authorization_url() 메소드를 통하여 이전에 반환된 URL로 사용자를 리다이렉트 할 수 있습니다.

만약 데스크탑 응용 프로그램(또는 콜백을 사용하지 않는 응용 프로그램)이라면, 트위터가 승인 후 제공하는 “검증 코드”를 사용자에게 요구해야 합니다.
웹 응용 프로그램 내에서 이 검증 코드는 URL에서 GET 쿼리 매개변수의 형태로 트위터의 콜백 요청에 의해 제공됩니다.

.. code-block :: python

   # 콜백 사용 예시 (웹)
   verifier = request.GET.get('oauth_verifier')

   # 콜백 w/o 예시 (데스크톱)
   verifier = raw_input('Verifier:')

마지막 단계는 요청 토큰을 접근 토근으로 교체하는 것입니다.
접근 토큰은 트위터 API라는 보물 상자에 접근하기 위한 “열쇠”입니다.
이 토큰을 가져오기 위해 다음을 해야합니다::

   # 이것이 웹 응용 프로그램이라 가정하면, 인증 핸들러를 다시 만들 필요가 있음
   # 우선...
   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   token = session.get('request_token')
   session.delete('request_token')
   auth.request_token = { 'oauth_token' : token,
                            'oauth_token_secret' : verifier }

   try:
       auth.get_access_token(verifier)
   except tweepy.TweepError:
       print('에러! 접근 토큰을 받는데 실패했습니다.')

이것은 접근 토큰을 추후에 사용하기 위한 좋은 저장 방식입니다.
수시로 재접근할 필요가 없습니다. 트위터는 현재 토큰을 만료시키지 않으므로, 비활성화 되는 때는 사용자가 응용 프로그램 접근을 취소할 때입니다.
접근 토큰을 저장하는 방법은 응용 프로그램에 따라 달라지지만, 기본적으로 key와 secret 문자열 값은 저장할 필요가 있습니다::

   auth.access_token
   auth.access_token_secret

토큰 값은 데이터베이스, 파일, 그 외 데이터 저장 장소에 저장이 가능합니다.
저장된 접근 토큰으로 다시 OAuthHandler를 다시 실행하기 위해선 다음을 해야 합니다::

   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(key, secret)

OAuthHandler가 접근 토큰을 받아들였다면, 이제 다음 명령을 수행할 준비가 되었습니다::

   api = tweepy.API(auth)
   api.update_status('tweepy + oauth!')

OAuth 2 인증
======================

Tweepy는 OAuth 2 인증 방식도 지원합니다.
OAuth 2는 응용 프로그램이 사용자 없이 API 요청을 하는 인증 방식입니다.
공공 정보에 대해 읽기 전용 접근만 필요한 경우 이 방식을 사용하세요.

OAuth 1a처럼, 먼저 클라이언트 응용프로그램을 등록하고 consumer key와 secret값을 얻어야 합니다.

그 다음 AppAuthHandler 인스턴스를 생성하고, consumer key와 secret을 전달합니다::

   auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

토큰을 받았다면, 이제 작업을 시작할 준비가 되었습니다::

   api = tweepy.API(auth)
   for tweet in tweepy.Cursor(api.search, q='tweepy').items(10):
       print(tweet.text)
