.. _streaming_how_to:
.. _트위터 스트리밍 API 설명서: https://developer.twitter.com/en/docs/tweets/filter-realtime/overview
.. _트위터 스트리밍 API 연결 설명서: https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data
.. _트위터 응답 코드 설명서: https://dev.twitter.com/overview/api/response-codes

************************
Tweepy를 이용한 스트리밍
************************
Tweepy는 인증, 연결, 세션 생성 및 삭제, 수신 메시지 읽기 및 메시지 라우팅 등을 처리해줌으로써 트위터 스트리밍 API를 더 쉽게 사용할 수 있게 해줍니다.

이 페이지는 당신이 Tweepy로 트위터 스트림을 사용하기 위한 첫 걸음을 제시하여 도움을 주는 것을 목표로 합니다. 트위터 스트리밍의 일부 기능은 여기에서 다루지 않습니다. 트위피 소스 코드의 streaming.py를 참조해주세요.

트위터 스트림에 접근하기 위해선 API 인증이 필요합니다. 인증 과정에 도움이 필요하다면 :ref:`auth_tutorial` 를 참조해주세요.

요약
====
트위터 스트리밍 API는 트위터의 메세지를 실시간으로 다운로드 하는 데에 사용됩니다. 대량의 트윗을 얻거나 사이트 스트림 또는 사용자 스트림을 사용해서 라이브 피드를 만드는 데에 유용합니다. `트위터 스트리밍 API 설명서`_.을 봐주세요.

스트리밍 API는 REST API와는 상당히 다릅니다. 왜냐하면 REST API는 트위터에서 데이터를 가져오는 데에 사용되는 반면에 스트리밍 API는 메세지를 지속되는 세션으로 보내주기 때문입니다. 이를 통해 스트리밍 API는 REST API를 사용하는 것보다 더 많은 데이터를 실시간으로 다운로드 할 수 있습니다.

Tweepy에서 **tweepy.Stream** 의 경우엔 스트리밍 세션을 설정하고, **StreamListener** 인스턴스에게 메시지를 보내는 일을 합니다. 스트림 수신자의 **on_data** 메소드는 모든 메시지를 수신하고 메시지의 종류에 따라 함수를 호출합니다. 기본 **StreamListener** 는 가장 일반적인 트위터 메시지를 분류하여 적절하게 설정된 메소드로 보낼 수 있습니다. 하지만 기본 **StreamListener** 의 메소드들은 스텁 메소드에 불과합니다.

그러므로 스트리밍 API를 사용할 때는 다음의 세 단계를 거쳐야 합니다.

1. **StreamListener** 를 상속받은 클래스를 생성

2. 그 클래스를 사용해서 **Stream** 객체를 생성

3. **Stream** 를 사용해서 트위터 API에 연결


1단계: **StreamListener** 생성
==============================
아래의 간단한 스트림 수신자는 status의 글을 출력합니다. Tweepy의 **StreamListener** 의 **on_data** 메소드는 손쉽게 status의 데이터를 **on_status** 메소드로 보내줍니다. **StreamListener** 를 상속받은 **MyStreamListener** 클래스를 생성하고 **on_status** 를 오버라이딩 합니다. ::

  import tweepy
  #tweepy.StreamListener에 on_status의 로직을 추가해서 오버라이딩
  class MyStreamListener(tweepy.StreamListener):
  
      def on_status(self, status):
          print(status.text)

2단계: 스트림 생성
==================
스트림을 얻기 위해선 api 인스턴스가 필요합니다. api 객체를 얻는 방법은 :ref:`auth_tutorial` 를 참조해주세요. api와 status 수신자를 얻어낸 후엔 스트림 객체를 만들 수 있습니다. ::

  myStreamListener = MyStreamListener()
  myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

3단계: 스트림을 시작
====================
Tweepy는 많은 트위터 스트림을 지원합니다. 대부분의 경우에는 filter, user_stream, sitestream 등을 사용하게 됩니다. 더 많은 다른 스트림의 지원 여부에 관한 정보는 `트위터 스트리밍 API 설명서`_.를 참조해주세요.

이 예제에선 **filter** 를 사용해서 *python* 이라는 단어를 포함하는 모든 트윗을 스트리밍 합니다. **track** 매개변수는 스트림에서 검색할 단어들의 배열입니다. ::
  
  myStream.filter(track=['python'])

이 예제는 **filter** 를 사용해서 특정 사용자의 트윗을 스트리밍 하는 방법을 보여줍니다. **follow** 매개변수는 사용자들의 ID의 배열입니다. ::

  myStream.filter(follow=["2211149702"])

ID를 찾는 쉬운 방법은 변환 웹사이트를 이용하는 것입니다: 'what is my twitter ID' 를 검색하세요.

추가적인 조언
=============

비동기 스트리밍
---------------
스트림은 연결이 끊어지지 않으면 종료되지 않아 스레드가 차단됩니다. Tweepy는 **filter** 에서 편리성을 높여줄 매개변수인 **is_async** 를 제공하여 스트림이 새로운 스레드에서 실행 되도록 합니다. 예시 ::

  myStream.filter(track=['python'], is_async=True)

오류 처리
---------
트위터의 스트리밍 API를 사용할 때에는 속도 제한을 초과할 위험을 고려해야 합니다. 만약 클라이언트가 정해진 시간동안 스트리밍 API에 접근 시도 횟수가 제한된 수를 초과한다면, 420 오류를 수신하게 됩니다. 클라이언트가 420 오류를 수신한 후 기다려야 하는 시간은 접속에 실패할 때마다 기하급수적으로 증가합니다.

Tweepy의 **Stream Listener** 은 오류 코드를 **on_error** 스텁 메소드로 전송합니다. **on_error** 의 기본 구현은 모든 코드에서 **False** 을 반환하지만, `트위터 스트리밍 API 연결 설명서`_ 에서 권장하는 백오프 전략을 사용하여 어떤, 혹은 모든 코드에서 Tweepy가 다시 연결할 수 있도록 오버라이딩 할 수 있습니다. ::

  class MyStreamListener(tweepy.StreamListener):
  
      def on_error(self, status_code):
          if status_code == 420:
              # on_error에서 False를 반환하면 스트림의 연결 차단
              return False

          # Fasle가 아닌 값을 반환하면 백오프 형식으로 스트림에 재연결

트위터 API의 더 많은 오류 코드에 대한 정보를 보려면 `트위터 응답 코드 설명서`_. 를 참조하세요.