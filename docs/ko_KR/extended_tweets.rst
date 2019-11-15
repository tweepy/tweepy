.. _extended_tweets:
.. _트위터의 Tweet 업데이트 관련 문서: https://developer.twitter.com/en/docs/tweets/tweet-updates

***************
확장된 트윗
***************

이 문서는 `트위터의 Tweet 업데이트 관련 문서`_ 에 대한 보충입니다.

들어가며
========

2016년 5월 24일, 트위터는 이러한 자사 API의 변경사항에 대한 지원 및
API 옵션의 업데이트에 대해 설명하는 초기 기술 문서와 관련,
답글 및 URL의 처리 및
`게시 방법 <https://blog.twitter.com/2016/doing-more-with-140-characters>`_
에 대한
`변경사항을 발표 <https://blog.twitter.com/express-even-more-in-140-characters>`_
했습니다.\ [#]_

또한 2017년 9월 26일, 트위터는 특정 언어에 대한 280자 트윗 작성을 
`테스트하기 시작 <https://blog.twitter.com/official/en_us/topics/product/2017/Giving-you-more-characters-to-express-yourself.html>`_
했으며,\ [#]_ 당해 11월 7일에 글자 수 제한으로 인한 부당한 요금 부과 등의 문제를을 해결하기 위해 
글자 수 제한을 상향 조정한다고
`발표 <https://blog.twitter.com/official/en_us/topics/product/2017/tweetingmadeeasier.html>`_
했습니다.\ [#]_

표준 API 메소드
===============

``tweepy.API`` 의 Status 객체를 반환하는 모든 메소드는 새로운
``tweet_mode`` 매개변수를 받습니다. 유효한 형식의 매개변수로는 ``compat`` 과
``extended`` 가 있으며, 이는 각각 호환성 모드 (Compatibility Mode)와
확장 모드 (Extended Mode)를 제공합니다.

전달받은 매개변수가 없을 경우, 기본값인 호환성 모드가 제공됩니다.

호환성 모드 (Compatibility Mode)
--------------------------------

기본적으로, 호환성 모드를 사용할 경우 ``tweepy.API`` 에 의해 반환되는
Status 객체의 ``text`` 속성값에서 필요에 따라 140자를 초과하는 데이터가 잘린 후 버려집니다.
데이터를 잘라 냈을 경우, Status 객체의 ``truncated`` 속성값은 ``True`` 가 되며,
``entities`` 속성에는 범위 내의 데이터, 즉 잘린 후의 엔티티만이 채워지게 될 것입니다.
이는 Status 객체의 ``text`` 속성값에 줄임표 문자, 공백 그리고
해당 트윗 자기 자신에 대한 영구적인 링크(Permalink)가 포함되는 것으로 식별이 가능합니다.

확장 모드 (Extended Mode)
-------------------------

확장 모드를 사용할 경우, Status 객체의 ``text`` 속성은
잘리지 않은(Untruncated) 온전한 텍스트 데이터를 가지는 ``full_text`` 속성으로 대체됩니다.
이 때 Status 객체의 ``truncated`` 속성값은 ``False`` 가 될 것이며,
``entities`` 속성에는 모든 엔티티들이 채워지게 될 것입니다.
또한, Status 객체는 트윗 중 표시 가능한 컨텐츠의 내부 첫 부분(Inclusive Start)과
외부 끝 부분(Exclusive End)을 가리키는, 두 가지 원소를 가지는 배열(Array) 형태의
``display_text_range`` 라는 속성을 갖게 될 것입니다.

스트리밍
========

기본적으로, 스트림으로부터의 Status 객체에는 트윗의 원본 데이터(Raw data)와
페이로드(Payload)에 대응하는 필드를 가진 ``extended_tweet`` 속성이 포함될 수 있습니다.
이 속성/필드는 '확장된 트윗'에만 존재하며, 하위 필드에 대한 딕셔너리가 포함되어 있습니다.
이 딕셔너리의 ``full_text`` 하위 필드/키에는 트윗에 대한 잘리지 않은(Untruncated),
온전한 텍스트 데이터가 포함될 것이며, ``entities`` 하위 필드/키에는
모든 엔티티들이 채워지게 될 것입니다.
만약 확장된 엔티티가 있다면, ``extended_entities`` 하위 필드/키에 그 엔티티들이 채워질 것입니다.
추가적으로, ``display_text_range`` 하위 필드/키에는
트윗 중 표시 가능한 컨텐츠의 내부 첫 부분(Inclusive Start)과
외부 끝 부분(Exclusive End)을 가리키는,
두 가지 원소를 가지는 배열(Array) 형태의 데이터가 저장될 것입니다.

리트윗 다루기
=============

리트윗을 다룰 때 확장 모드를 사용할 경우,
Status 객체의 ``full_text`` 속성이 리트윗된 트윗의 전체 텍스트를 포함하지 않고,
줄임표 문자 등으로 잘릴 수 있습니다. 물론 그렇다 하더라도,
리트윗 트윗에 대한 Status 객체의 ``retweeted_status`` 속성 그 자체가
또 하나의 Status 객체이기 때문에, 해당 개체의 ``full_text`` 속성을 대신 사용할 수 있습니다.

또, 이는 스트림으로부터의 리트윗 트윗에 대한 Status 객체 및 페이로드(Payload)에도 유사하게 적용됩니다.
``extended_tweet`` 으로부터의 딕셔너리에는 위와 비슷하게, 줄임표 문자 등으로 잘릴 수 있는
``full_text`` 하위 필드/키가 포함되어 있습니다.
이 때 역시 리트윗된 Status 객체로부터의 (``retweeted_status`` 로부터의 속성/필드로부터의)
``extended_tweet`` 속성/필드를 대신 사용할 수 있습니다.

예시
====

아래의 예시는, ``tweepy.API`` 객체와 트윗에 대한 ``id`` 를 이용,
해당 트윗의 모든 텍스트를 온전하게 출력하는 예시입니다.
이 때 해당 트윗이 리트윗된 트윗일 경우, 리트윗된 트윗의 모든 텍스트를 출력합니다::

   status = api.get_status(id, tweet_mode="extended")
   try:
       print(status.retweeted_status.full_text)
   except AttributeError:  # 리트윗이 아님
       print(status.full_text)

``status`` 가 Retweet일 경우(리트윗된 트윗일 경우), ``status.full_text`` 가 잘릴 수 있습니다.

아래의 ``StreamListener`` 를 위한 Status 이벤트 핸들러는, 트윗의 모든 텍스트를 출력합니다.
이 때, 해당 트윗이 리트윗된 트윗일 경우, 리트윗된 트윗의 모든 텍스트를 출력합니다::

   def on_status(self, status):
       if hasattr(status, "retweeted_status"):  # 리트윗 트윗인지 확인
           try:
               print(status.retweeted_status.extended_tweet["full_text"])
           except AttributeError:
               print(status.retweeted_status.text)
       else:
           try:
               print(status.extended_tweet["full_text"])
           except AttributeError:
               print(status.text)

``status`` 가 Retweet일 경우(리트윗된 트윗일 경우),
``extended_tweet`` 속성을 가지지 않을 것이며,
``status.full_text`` 가 잘릴 수 있습니다.

.. rubric:: 각주

.. [#] https://twittercommunity.com/t/upcoming-changes-to-simplify-replies-and-links-in-tweets/67497
.. [#] https://twittercommunity.com/t/testing-280-characters-for-certain-languages/94126
.. [#] https://twittercommunity.com/t/updating-the-character-limit-and-the-twitter-text-library/96425
