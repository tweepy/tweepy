.. _api_reference:

.. include:: parameters.rst

API 레퍼런스
============

이 페이지는 Tweepy 모듈에 대한 기초적인 안내를 포함하고 있습니다.


:mod:`tweepy.api` --- Twitter API 래퍼(Wrapper)
================================================

.. class:: API([auth_handler=None], [host='api.twitter.com'], \
               [search_host='search.twitter.com'], [cache=None], \
               [api_root='/1'], [search_root=''], [retry_count=0], \
               [retry_delay=0], [retry_errors=None], [timeout=60], \
               [parser=ModelParser], [compression=False], \
               [wait_on_rate_limit=False], [wait_on_rate_limit_notify=False], \
               [proxy=None])

   이 클래스는 트위터로부터 제공되는 API의 래퍼를 제공합니다.
   이 클래스가 제공하는 함수들은 아래와 같습니다.

   :param auth_handler: 인증 핸들러
   :param host: 일반 API 호스트
   :param search_host: 검색 API 호스트
   :param cache: 캐시 백엔드
   :param api_root: 일반 API 루트 경로
   :param search_root: 검색 API 루트 경로
   :param retry_count: 에러가 발생했을 때 기본적으로 재시도할 횟수
   :param retry_delay: 다음 재시도까지의 지연시간(초 단위)
   :param retry_errors: 재시도할 HTTP 상태 코드
   :param timeout: 트위터로부터의 응답을 기다릴 최대 시간
   :param parser: 트위터로부터의 응답 결과를 파싱하는 데 사용할 객체
   :param compression: 요청에 GZIP 압축을 사용할지의 여부
   :param wait_on_rate_limit: 트위터 API 호출 제한 횟수 보충을 기다릴지의 여부
   :param wait_on_rate_limit_notify: 트위터 API 호출 제한 횟수 보충을 기다릴 때,
                                     따로 안내 메세지를 출력할지의 여부
   :param proxy: 트위터에 연결할 때 사용할 HTTPS 프록시의 전체 주소.


타임라인 메소드
---------------

.. method:: API.home_timeline([since_id], [max_id], [count], [page])

   현재 인증된 사용자와 이 사용자의 친구들에 의해 작성된 Status 중, 가장 최근에 작성된 20개의
   Status를 (리트윗을 포함해) 반환합니다. 웹 상에서의 /timeline/home와 동일합니다.

   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param page: |page|
   :rtype: :class:`Status` 객체 리스트


.. method:: API.statuses_lookup(id_, [include_entities], [trim_user], [map_], \
                                [include_ext_alt_text], [include_card_uri])

   요청 1회당 트윗 객체를 최대 100개 반환합니다. ``id_`` 매개변수에 의해 구분됩니다.

   :param id\_: 반환받을 트윗의 ID 리스트(최대 100개).
   :param include_entities: |include_entities|
   :param trim_user: |trim_user|
   :param map\_: 볼 수 없는 트윗을 포함할지의 여부를 설정하는 boolean 형태의 변수입니다. 기본값은 False.
   :param include_ext_alt_text: |include_ext_alt_text|
   :param include_card_uri: |include_card_uri|
   :rtype: :class:`Status` 객체 리스트


.. method:: API.user_timeline([id/user_id/screen_name], [since_id], [max_id], \
                              [count], [page])

   현재 인증된 사용자 또는 지정된 사용자의 Status 중 가장 최근의 20개를 반환합니다.
   ``id_`` 매개변수를 이용하면, 다른 사용자의 타임라인을 요청하는 것이 가능합니다.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param page: |page|
   :rtype: :class:`Status` 객체 리스트


.. method:: API.retweets_of_me([since_id], [max_id], [count], [page])

   현재 인증된 사용자의 최근 트윗 중, 다른 사용자에 의해 리트윗된 트윗 20개를 반환합니다.

   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param page: |page|
   :rtype: :class:`Status` 객체 리스트


.. method:: API.mentions_timeline([since_id], [max_id], [count])

   리트윗을 포함하는, 가장 최근의 멘션(답글) 20개를 반환합니다.

   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :rtype: :class:`Status` 객체 리스트


Status 메소드
-------------

.. method:: API.get_status(id, [trim_user], [include_my_retweet], \
                           [include_entities], [include_ext_alt_text], \
                           [include_card_uri])

   ID 매개변수에 의해 구분된 하나의 Status 객체를 반환합니다.

   :param id: |sid|
   :param trim_user: |trim_user|
   :param include_my_retweet: boolean 형태의 변수. 현재 인증된 사용자에 의해 리트윗된 트윗이,
      추가적으로 리트윗된 원본 트윗의 ID를 포함하는 current_user_retweet 노드를 포함해야 하는지를 지정합니다.
   :param include_entities: |include_entities|
   :param include_ext_alt_text: |include_ext_alt_text|
   :param include_card_uri: |include_card_uri|
   :rtype: :class:`Status` object


.. method:: API.update_status(status, [in_reply_to_status_id], \
                              [auto_populate_reply_metadata], \
                              [exclude_reply_user_ids], [attachment_url], \
                              [media_ids], [possibly_sensitive], [lat], \
                              [long], [place_id], [display_coordinates], \
                              [trim_user], [enable_dmcommands], \
                              [fail_dmcommands], [card_uri])

   현재 인증된 사용자의 Status를 업데이트합니다. 흔히 '트윗을 작성한다'라고 불립니다.

   Status 업데이트를 시도할 때 마다, 포함된 텍스트를 현재 인증된 사용자의 가장 최근 트윗과
   비교합니다. 이에 따라, 중복된 업데이트 시도를 차단할 수 있으며, 이를 성공적으로 차단한 후에는
   403 에러를 반환합니다. 참고: 사용자는 같은 Status 객체를 두 번 이상 연속해 게시할 수 없습니다.

   트위터 API상에서의 제한은 초과하지 않았으나, 사용자의 일일 트윗 작성 제한수를 초과하는
   경우가 발생할 수 있습니다. 업데이트 시도가 이 제한을 초과할 경우에도, HTTP 403 에러를
   반환받을 것입니다.

   :param status: 포함된 텍스트. Status 업데이트(트윗 작성)에 쓰입니다.
   :param in_reply_to_status_id: 답글을 작성할 대상 트윗의 ID.
      참고: 따로 값을 전달하지 않으면, 이 매개변수는 무시됩니다.
      따라서, @username를 반드시 포함해야 하며, 이는 대상 트윗을 작성한 사람의 @username
      이어야 합니다.
   :param auto_populate_reply_metadata: True로 설정되고
      in_reply_to_status_id와 같이 사용되었을 경우,
      원본 트윗에 달린 답글 @멘션을 찾아, 새 트윗을 그 곳에 추가합니다.
      @멘션은 @멘션 갯수 제한 이하에서, 트윗 타래가 '확장된 트윗들의 메타데이터 형태'로 사용될 것입니다.
      원본 트윗이 삭제되었을 경우, 반환값 생성이 실패할 수 있습니다.
   :param exclude_reply_user_ids: auto_populate_reply_metadata와
      같이 사용되었을 경우, 서버에서 생성된 @멘션 머릿말 중
      반점(,)으로 구분된 사용자 ID를 삭제합니다. 참고: 답글 @멘션은 제거될 수 없습니다.
      (∵ in_reply_to_status_id의 의미를 깨트릴 수 있음) 이 @멘션 ID를 제거하려는 시도는
      무시됩니다.
   :param attachment_url: URL이 Status 객체 중
      확장된 트윗의 텍스트에 포함되지 않도록, 트윗에 첨부되는 형식으로 제공합니다.
      이 URL은 트윗의 링크(Permalink) 또는 다이렉트 메세지(DM)의 깊은(Deep) 링크여야 합니다.
      단, 트위터와 관련 없는 임의의 URL은 포함됩니다. 즉, attachment_url에 트윗의 링크 또는
      다이렉트 메세지의 깊은 링크가 아닐 경우, 트윗 생성에 실패하며 예외를 발생시킬 것입니다.
   :param media_ids: 트윗과 연결할 media_ids 리스트.
      트윗 하나당 최대 4개의 이미지, 1개의 움직이는 GIF 형식의 이미지 또는 1개의 동영상만
      포함할 수 있습니다.
   :param possibly_sensitive: 나체 사진 또는 수술 과정 사진 등의,
      민감한 내용으로 여겨질 수 있는 미디어를 업로드할 경우
      반드시 이 속성값을 True로 설정해야 합니다.
   :param lat: 이 트윗이 가리킬 위치의 위도. -90.0 부터 +90.0 (북반구가 양수값) 범위 안의
      값 이외의 값이 주어지면 전달된 값을 무시합니다. 아래의 ``long`` 매개변수가 지정되지
      않은 경우에도 무시합니다.
   :param long: 이 트윗이 가리킬 위치의 경도. -180.0부터 +180.0 (동쪽이 양수값) 범위 안의
      값 이외의 값이 주어지거나, 숫자 이외의 값이 주어졌거나, ``geo_enabled`` 가 비활성화 되었거나,
      위의 ``lat`` 매개변수가 지정되지 않은 경우 전달된 값을 무시합니다.
   :param place_id: (사용자가 위치 정보를 사용할 수 있는 경우)
                    트윗이 작성된 위치의 정보 (ID).
   :param display_coordinates: 트윗이 작성되어 전송된 위치를 표시할지 말지의 여부.
   :param trim_user: |trim_user|
   :param enable_dmcommands: True로 설정되었다면,
      Status 객체를 다이렉트 메세지로 사용자에게 보낼 때 텍스트의 일부를
      숏코드 커맨드(Shortcode Command)로 대체하여 보냅니다.
      False로 설정되었다면,
      Status 객체를 다이렉트 메세지로 사용자에게 보낼 때,
      위와 같은 변환 과정을 거치지 않고 텍스트 그대로를 보냅니다..
   :param fail_dmcommands: When set to true, causes any status text that starts
      with shortcode commands to return an API error. When set to false, allows
      shortcode commands to be sent in the status text and acted on by the API.
      True로 설정되었다면, 객체 텍스트가 숏코드 커맨드(Shortcode Command)로 시작할 때
      API 에러를 발생시킵니다.
      False로 설정되었다면, 숏코드 커맨드가 객체의 텍스트에 포함되고 API상에서 동작하는 것을 허용합니다.
   :param card_uri: 트윗에 ``card_uri`` 속성을 이용하여 광고 카드를 추가합니다.

   :rtype: :class:`Status` 객체


.. method:: API.update_with_media(filename, [status], \
                                  [in_reply_to_status_id], \
                                  [auto_populate_reply_metadata], [lat], \
                                  [long], [source], [place_id], [file])

   *더 이상 사용되지 않음*: :func:`API.media_upload` 를 대신 사용하세요.
   현재 인증된 사용자의 Status를 미디어와 함께 업데이트합니다.
   중복된 Status 작성 시도 또는 너무 긴 트윗의 작성 시도는 별다른 경고 없이 무시될 것입니다.

   :param filename: 업로드할 이미지의 이름. `file` 이 따로 지정된 것이 아니라면, 자동으로 열릴 것입니다.
   :param status: Status 객체 업데이트에 사용할 텍스트
   :param in_reply_to_status_id: 답글을 작성할 대상 트윗의 ID
   :param auto_populate_reply_metadata: Status 메타데이터에 @멘션들을 포함할지의 여부
   :param lat: 이 트윗이 가리킬 위치의 위도
   :param long: 이 트윗이 가리킬 위치의 경도
   :param source: 업데이트에 사용할 소스. Identi.ca 에서만 지원되며, 트위터는 이 매개변수를 무시합니다.
   :param place_id: (사용자가 위치 정보를 사용할 수 있는 경우)
                    트윗이 작성된 위치의 정보 (ID).
   :param file: 파일 객체로, `filename` 를 직접 여는 것 대신 사용됩니다.
                물론 MIME 타입 감지 및 POST 데이터 형식의 필드로 `filename` 가 필요하기는 합니다.
   :rtype: :class:`Status` 객체


.. method:: API.destroy_status(id)

   지정한 Status 객체를 파괴합니다.
   파괴하려는 Status 객체는 현재 인증된 사용자의 것이어야만 합니다.

   :param id: |sid|
   :rtype: :class:`Status` 객체


.. method:: API.retweet(id)

   지정한 트윗을 리트윗합니다. 리트윗하려는 트윗의 ID를 필요로 합니다.

   :param id: |sid|
   :rtype: :class:`Status` 객체


.. method:: API.retweeters(id, [cursor], [stringify_ids])

   매개변수 ``id`` 에 의해 지정된 트윗을 리트윗한 사용자의 ID 중, 최대 100개를 반환합니다.

   :param id: |sid|
   :param cursor: |cursor|
   :param stringify_ids: 사용자 ID를 정수 타입 대신 문자열 타입으로 반환받습니다.
   :rtype: 정수 리스트 (또는 문자열 리스트)


.. method:: API.retweets(id, [count])

   Returns up to 100 of the first retweets of the given tweet.
   지정한 트윗의 리트윗 중 가장 최근의 100개까지를 반환합니다.

   :param id: |sid|
   :param count: 가져올 트윗의 갯수
   :rtype: :class:`Status` 객체 리스트


.. method:: API.unretweet(id)

   리트윗 Status를 취소합니다. 리트윗 취소할 트윗의 ID를 필요로 합니다.

   :param id: |sid|
   :rtype: :class:`Status` 객체


User methods
------------

.. method:: API.get_user(id/user_id/screen_name)

   지정한 사용자의 정보를 반환합니다.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :rtype: :class:`User` 객체


.. method:: API.me()

   현재 인증된 사용자의 정보를 반환합니다.

   :rtype: :class:`User` 객체


.. method:: API.friends([id/user_id/screen_name], [cursor], [skip_status], \
                        [include_user_entities])

   대상 사용자의 팔로잉 목록을, 목록에 추가된 순서대로, 요청 1회당 최대 100개씩 반환합니다.
   ``id`` 또는 ``screen_name`` 을 통해 대상을 지정하지 않으면,
   현재 인증된 사용자를 대상으로 합니다.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param skip_status: |skip_status|
   :param include_user_entities: |include_user_entities|
   :rtype: class:`User` 객체 리스트


.. method:: API.followers([id/screen_name/user_id], [cursor])

   대상 사용자의 팔로워 목록을, 목록에 추가된 순서대로, 요청 1회당 최대 100개씩 반환합니다.
   ``id`` 또는 ``screen_name`` 을 통해 대상을 지정하지 않으면,
   현재 인증된 사용자를 대상으로 합니다.

   :param id: |uid|
   :param user_id: |user_id|
   :param screen_name: |screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param skip_status: |skip_status|
   :param include_user_entities: |include_user_entities|
   :rtype: :class:`User` 객체 리스트


.. method:: API.lookup_users([user_ids], [screen_names], [include_entities], \
                             [tweet_mode])

   매개변수에 의한 검색 기준을 충족하는 사용자 객체를 요청 1회당 최대 100개씩 반환합니다.

   이 메소드를 사용할때는 아래 사항을 참고하세요.

   * 비공개 설정된 사용자의 Status 객체 업데이트 내역을 보기 위해서는 해당 사용자를
     팔로우하고 있는 상태여야 합니다. 팔로우하고 있지 않다면, 해당 Status 객체는 삭제될 것입니다.
   * 사용자 ID 또는 ``screen_name`` 의 순서는 반환받은 배열의 사용자 순서와 일치하지 않을 수 있습니다.
   * 요청한 사용자를 찾을 수 없거나, 계정이 정지 또는 삭제되었다면, 해당 계정은 결과값 리스트로 반환되지 않을 것입니다.
   * 검색 기준을 충족하는 결과가 아예 없을 경우, HTTP 404 오류가 발생합니다.

   :param user_ids: 사용자 ID 리스트이며, ID는 요청 1회당 최대 100개까지만 허용됩니다.
   :param screen_names: ``screen_name`` 의 리스트이며, 이 역시 요청 1회당 최대 100개까지만 허용됩니다.
   :param include_entities: |include_entities|
   :param tweet_mode: 인자로 compat 또는 extended를 넘길 수 있으며,
                      각각 140자 이상의 데이터가 포함된 트윗에 대해 호환성 모드와 확장 모드를 제공합니다.
   :rtype: list of :class:`User` 객체


.. method:: API.search_users(q, [count], [page])

   트위터의 '사용자 검색' 과 동일한 검색 기능을 실행합니다.
   이 API를 이용한 검색은, 트위터에서 제공하는 것과 동일한 검색 결과를
   반환합니다. 단, 최대 첫 1000개의 결과만 가져올 수 있습니다.

   :param q: 사용자 검색에 사용할 검색어
   :param count: 한 번에 가져올 결과의 수. 20보다 클 수 없습니다.
   :param page: |page|
   :rtype: list of :class:`User` 객체


다이렉트 메시지(DM) 메소드
--------------------------

.. method:: API.get_direct_message([id], [full_text])

   지정한 DM을 반환합니다.

   :param id: |id|
   :param full_text: |full_text|
   :rtype: :class:`DirectMessage` 객체


.. method:: API.list_direct_messages([count], [cursor])

   최근 30일 이내의 모든 DM의 내역(송수신 모두)을 반환합니다. 반환값은
   시간 역순으로 정렬되어 있습니다.

   :param count: |count|
   :param cursor: |cursor|
   :rtype: :class:`DirectMessage` 객체의 리스트


.. method:: API.send_direct_message(recipient_id, text, [quick_reply_type], \
                                    [attachment_type], [attachment_media_id])

   인증한 사용자의 계정으로 지정한 사용자에게 DM을 보냅니다.

   :param recipient_id: DM을 받을 사용자의 ID
   :param text: DM의 내용. 최대 글자수는 10000
   :param quick_reply_type: 사용자에게 표시할 빠른 응답 유형:

                            * options - Options 객체의 배열(최대 20)
                            * text_input - Text Input 객체
                            * location - Location 객체
   :param attachment_type: 첨부 유형. 미디어 또는 위치 등입니다.
   :param attachment_media_id: 메시지와 연결할 미디어의 id. DM은 하나의
                               미디어 ID만을 참조할 수 있습니다.
   :rtype: :class:`DirectMessage` 객체


.. method:: API.destroy_direct_message(id)

   ID 매개변수가 지정하는 DM을 삭제합니다. 삭제하기 위해서는 인증된
   사용자가 해당 DM의 수신자여야 합니다. DM은 사용자 콘텍스트에서
   제공하는 인터페이스에서만 제거됩니다. 대화에 참여한 다른 사용자는
   삭제한 이후에도 해당 DM에 접근할 수 있습니다.

   :param id: 삭제할 DM의 ID
   :rtype: None


친구 관계 메소드
----------------

.. method:: API.create_friendship(id/screen_name/user_id, [follow])

   지정한 사용자와 친구를 맺습니다. (일명 팔로우)

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param follow: 지정한 사용자를 팔로우 하고 대상 사용자에 대한 알림을 활성화합니다.
   :rtype: :class:`User` 객체


.. method:: API.destroy_friendship(id/screen_name/user_id)

   지정한 사용자를 친구 삭제 합니다. (일명 언팔로우)

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` 객체


.. method:: API.show_friendship(source_id/source_screen_name, \
                                target_id/target_screen_name)

   두 사용자의 관계에 대한 자세한 정보를 반환합니다.

   :param source_id: 주대상 사용자의 user_id
   :param source_screen_name: 주대상 사용자의 screen_name
   :param target_id: 대상 사용자의 user_id
   :param target_screen_name: 대상 사용자의 screen_name
   :rtype: :class:`Friendship` 객체


.. method:: API.friends_ids(id/screen_name/user_id, [cursor])

   지정한 사용자가 팔로우한 사용자들의 ID를 담은 배열을 반환합니다.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :rtype: 정수의 리스트


.. method:: API.followers_ids(id/screen_name/user_id)

   지정한 사용자를 팔로우한 사용자들의 ID를 담은 배열을 반환합니다.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :rtype: 정수의 리스트


계정 메소드
-----------

.. method:: API.verify_credentials([include_entities], [skip_status], \
                                   [include_email])

   제출한 사용자의 계정 사용 자격이 유효한지 판별합니다.

   :param include_entities: |include_entities|
   :param skip_status: |skip_status|
   :param include_email: True로 설정한다면 이메일이 문자열 형태로 user 객체 안에 같이
                         반환됩니다.
   :rtype: 자격이 유효하다면 :class:`User` 객체, 아니라면 False


.. method:: API.rate_limit_status()

   지정한 리소스 그룹에 속하는 메소드들의 현재 속도 제한을 반환합니다. 애플리케이션 전용 인증을
   사용하고 있다면, 이 메소드의 응답은 애플리케이션 전용 인증의 속도 제한의 상황을 나타냅니다.

   :param resources: 현재 속도 제한의 처리를 알고 싶은 리소스 그룹을 쉼표로 구분한 리스트
   :rtype: :class:`JSON` 객체


.. method:: API.update_profile_image(filename)

   인증된 사용자의 프로필 사진을 갱신합니다. 유효한 형식: GIF, JPG, PNG

   :param filename: 업로드할 이미지 파일의 로컬 경로. URL에 연결하는 것이 아닙니다!
   :rtype: :class:`User` 객체


.. method:: API.update_profile_background_image(filename)

   인증된 사용자의 배경 사진을 업데이트 합니다. 유효한 형식: GIF, JPG, PNG

   :param filename: 업로드할 이미지 파일의 로컬 경로. URL에 연결하는 것이 아닙니다!
   :rtype: :class:`User` 객체


.. method:: API.update_profile([name], [url], [location], [description])

   설정 페이지의 계정 탭에서 설정할 수 있는 값을 설정합니다.

   :param name: 최대 20글자
   :param url: 최대 100글자.
               "http://"가 없는 경우 덧붙입니다.
   :param location: 최대 30글자
   :param description: 최대 100글자
   :rtype: :class:`User` 객체


마음에 들어요 메소드
--------------------

.. method:: API.favorites([id], [page])

   인증된 사용자 또는 ID 매개변수로 특정되는 사용자가 마음에 들어요를 누른 status들을
   반환합니다.

   :param id: 마음에 들어요 목록을 요청할 사용자의 ID나 닉네임
   :param page: |page|
   :rtype: :class:`Status` 객체의 리스트


.. method:: API.create_favorite(id)

   ID 매개변수로 특정되는 status에 인증된 사용자의 계정으로 마음에 들어요를 누릅니다.

   :param id: |sid|
   :rtype: :class:`Status` 객체


.. method:: API.destroy_favorite(id)

   ID 매개변수로 특정되는 status에 인증된 사용자의 계정으로 마음에 들어요를 해제 합니다.

   :param id: |sid|
   :rtype: :class:`Status` 객체


차단 메소드
-----------

.. method:: API.create_block(id/screen_name/user_id)

   ID 매개변수로 특정되는 사용자를 인증된 사용자의 계정에서 차단합니다. 차단된 사용자를
   팔로우 중이었을 경우 언팔로우 합니다.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` 객체


.. method:: API.destroy_block(id/screen_name/user_id)

   인증된 사용자의 계정에서 ID 매개변수로 특정되는 사용자의 계정의 차단을 해제 합니다.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` 객체


.. method:: API.blocks([page])

   인증된 사용자가 차단한 사용자들의 user 객체의 배열을 반환합니다.

   :param page: |page|
   :rtype: :class:`User` 객체의 리스트


.. method:: API.blocks_ids([cursor])

   인증된 사용자가 차단한 사용자들의 ID의 배열을 반환합니다.

   :param cursor: |cursor|
   :rtype: 정수의 리스트


뮤트 메소드
-------------

.. method:: API.create_mute(id/screen_name/user_id)

   인증된 사용자의 계정에서 ID로 특정되는 사용자를 뮤트합니다.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` 객체


.. method:: API.destroy_mute(id/screen_name/user_id)

   인증된 사용자의 계정에서 ID로 특정되는 사용자의 뮤트를 해제합니다.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :rtype: :class:`User` 객체


.. method:: API.mutes([cursor], [include_entities], [skip_status])

   인증된 사용자가 뮤트한 사용자들의 user 객체의 배열을 반환합니다.

   :param cursor: |cursor|
   :param include_entities: |include_entities|
   :param skip_status: |skip_status|
   :rtype: :class:`User` 객체의 리스트


.. method:: API.mutes_ids([cursor])

   인증된 사용자가 뮤트한 사용자들의 ID의 배열을 반환합니다.

   :param cursor: |cursor|
   :rtype: 정수의 배열


스팸 신고 메소드
----------------------

.. method:: API.report_spam(id/screen_name/user_id, [perform_block])

   ID 매개변수로 특정되는 사용자를 인증된 사용자의 계정에서 차단하고, 스팸 계정으로 신고합니다.

   :param id: |uid|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param perform_block: 신고한 계정을 차단할지 여부를 나타내는 논리값. 기본값은 True
   :rtype: :class:`User` 객체


검색어 저장 메소드
----------------------

.. method:: API.saved_searches()

   인증된 사용자 계정에 저장된 검색어 쿼리를 반환합니다.

   :rtype: :class:`SavedSearch` 객체의 리스트


.. method:: API.get_saved_search(id)

   주어진 ID로 특정되는 인증된 사용자의 계정에 저장된 검색어로 데이터를 검색합니다.

   :param id: 검색할 검색어의 ID
   :rtype: :class:`SavedSearch` 객체


.. method:: API.create_saved_search(query)

   인증된 사용자의 계정에 새로운 검색어를 저장합니다.

   :param query: 저장하고 싶은 검색어의 쿼리
   :rtype: :class:`SavedSearch` 객체


.. method:: API.destroy_saved_search(id)

   인증된 사용자의 계정에서 ID로 특정되는 검색어를 삭제합니다. 그 검색어는 인증된 사용자의
   계정에 저장된 검색어여야 합니다.

   :param id: 삭제할 검색어의 ID
   :rtype: :class:`SavedSearch` 객체


편의 기능 메소드
----------------

.. method:: API.search(q, [geocode], [lang], [locale], [result_type], \
                       [count], [until], [since_id], [max_id], \
                       [include_entities])

   지정한 쿼리와 관련된 트윗의 모음을 반환합니다.

   트위터의 검색 서비스와, 더 나아가서 검색 API가 모든 트윗 소스에서 검색을 하는 것은 아니라는 것에
   유의해주세요. 모든 트윗이 검색 인터페이스를 통해 색인화 되어있거나 검색할 수 있게 만들어져 있지는
   않습니다.

   API v1.1에서는, 검색 API의 응답 형식이 REST API나 플랫폼을 통해서 볼 수 있는 객체와 더 비슷한
   트윗 객체를 반환하도록 향상되었습니다. 하지만, perspectival 속성(인증된 사용자에 의존하는 필드)은
   현재 지원하지 않습니다.\ [#]_\ [#]_

   :param q: 연산자를 포함하여 최대 500자의 검색하고자 하는 문자열 쿼리. 쿼리는 추가적으로 복잡도에
      따라 제한될 수 있습니다.
   :param geocode: 주어진 위도, 경도의 주어진 반경 내에 위치한 사용자의 트윗만 반환합니다. 위치는
      우선적으로 위치 정보 삽입 API에서 받아오지만, 트위터 프로필 내의 정보로 대체할 수 있습니다.
      매개변수의 값은 "위도,경도,반경"의 형태로 지정되며, 반경은 "mi"(마일) 또는 "km"(킬로미터)
      단위로 주어져야 합니다. API를 통해 근거리 연산자를 사용하여 임의의 위치를 geocode로 입력할
      수는 없다는 점을 유의해주세요. 다만 이 geocode 매개변수를 통해 근처의 지오코드를 검색할 수는
      있습니다. 반경 수식어를 사용할 경우에는 최대 1,000개의 분명하게 구분되는 "하위 영역"을 고려할
      할 것입니다.
   :param lang: 트윗을 ISO 639-1 코드로 주어진 언어로 제한합니다. 언어 탐지가 적절하게 작동했다고
      전제합니다.
   :param locale: 전송한 쿼리의 언어를 명시하세요.(현재는 ja만 유효합니다.) 이는 언어별 사용자를
      위한 것이며 대부분의 경우엔 기본값이 작동합니다.
   :param result_type: 얻고 싶은 검색 결과의 형식에 대해 명시하세요. 현재 기본값은 "mixed"이며
      유효한 값은 다음과 같습니다.:

      * mixed : 응답에 인기 결과와 실시간 결과 모두를 포함합니다.
      * recent : 응답으로 가장 최근의 결과만을 반환합니다.
      * popular : 응답으로 가장 인기 있는 결과만을 반환합니다.
   :param count: |count|
   :param until: 주어진 날짜 이전에 만들어진 트윗을 반환합니다. 날짜는 YYYY-MM-DD의 형식으로 주어야
      합니다. 검색 색인은 7일동안만 유지됩니다. 다시 말해서 일주일 이상 지난 트윗은 찾을 수 없습니다.
   :param since_id: |since_id| API를 통해서 접근할 수 있는 트윗의 수에는 제한이 있습니다. since_id
      이후로 트윗 수 제한을 초과한다면, since_id는 제한을 초과하지 않는 가장 오래된 ID로 강제 설정됩니다.
   :param max_id: |max_id|
   :param include_entities: |include_entities|
   :rtype: :class:`SearchResults` 객체


List 메소드
------------

.. method:: API.create_list(name, [mode], [description])

   인증된 사용자에 대한 새 목록을 생성합니다.
   계정 당 최대 1000개의 목록을 생성할 수 있음에 유의하세요.

   :param name: 새 목록의 이름.
   :param mode: |list_mode|
   :param description: 생성 중인 목록에 대한 설명.
   :rtype: :class:`List` object


.. method:: API.destroy_list([owner_screen_name/owner_id], list_id/slug)

   지정된 목록을 삭제합니다.
   인증된 사용자는 삭제하기 위해 해당 목록을 소유해야 합니다.

   :param owner_screen_name: |owner_screen_name|
   :param owner_id: |owner_id|
   :param list_id: |list_id|
   :param slug: |slug|
   :rtype: :class:`List` object


.. method:: API.update_list(list_id/slug, [name], [mode], [description], \
                            [owner_screen_name/owner_id])

   지정한 목록을 업데이트합니다.
   인증된 사용자는 업데이트하기 위해 해당 목록을 소유해야 합니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param name: 새 목록의 이름.
   :param mode: |list_mode|
   :param description: 목록에 부여할 설명.
   :param owner_screen_name: |owner_screen_name|
   :param owner_id: |owner_id|
   :rtype: :class:`List` object


.. method:: API.lists_all([screen_name], [user_id], [reverse])

   인증된 사용자 또는 지정된 사용자가 가입한 모든 목록(소유한 목록 포함)을 반환합니다.
   user_id나 screen_name 매개변수를 사용하여 사용자를 지정합니다.
   만약 사용자를 지정하지 않는 경우, 인증된 사용자가 사용됩니다.

   이 호출로 최대 100개의 결과가 반환될 것입니다.
   가입자 목록들이 먼저 반환되고, 이후에 소유한 목록들이 반환됩니다.
   따라서 만약 사용자가 90개의 목록에 가입하고 20개의 목록을 소유한다면,
   메소드는 90개의 가입 목록과 10개의 소유 목록을 반환합니다.
   매개변수가 reverse=true인 반대의 메소드인 경우, 소유 목록을 먼저 반환하므로
   20개의 소유목록과 80개의 가입 목록을 반환합니다.

   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param reverse: 소유 목록을 먼저 반환할지에 대한 참/거짓 여부. 이 매개변수가 어떻게 작동하는지에 대한 정보는 위의 설명을 참조하세요.

   :rtype: list of :class:`List` objects


.. method:: API.lists_memberships([screen_name], [user_id], \
                                  [filter_to_owned_lists], [cursor], [count])

    사용자가 추가된 목록들을 반환합니다.
    user_id 또는 screen_name을 입력하지 않으면 인증된 사용자에 대한 멤버쉽이 반환됩니다.

   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param filter_to_owned_lists: 인증된 사용자 소유의 목록들을 반환할지에 대한 참/거짓 여부. user_id 또는 screen_name으로 표현되는 사용자 또한 같습니다.
   :param cursor: |cursor|
   :param count: |count|

   :rtype: list of :class:`List` objects


.. method:: API.lists_subscriptions([screen_name], [user_id], [cursor], \
                                    [count])

   지정된 사용자가 구독하는 목록들의 모음(기본적으로 페이지 당 20개의 목록)을 얻습니다.
   사용자 자신의 목록은 포함하지 않습니다.

   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param cursor: |cursor|
   :param count: |count|
   :rtype: list of :class:`List` objects


.. method:: API.list_timeline(list_id/slug, [owner_id/owner_screen_name], \
                              [since_id], [max_id], [count], \
                              [include_entities], [include_rts])

   지정된 목록의 구성원이 작성한 트윗들의 타임라인을 반환합니다.
   기본적으로 리트윗이 포함됩니다. 리트윗을 생략하려면 include_rts=false 매개변수를 이용하세요.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :param since_id: |since_id|
   :param max_id: |max_id|
   :param count: |count|
   :param include_entities: |include_entities|
   :param include_rts: 목록 타임라인에 표준 트윗 외의 리트윗(있는 경우)도 포함할지 여부에 대한 참/거짓 여부. 리트윗된 트윗의 출력 형식은 홈 타임라인에서 보는 표현 방식과 동일합니다.

   :rtype: :class:`Status` 객체 리스트


.. method:: API.get_list(list_id/slug, [owner_id/owner_screen_name])

   지정된 목록을 반환합니다.
   private상태의 목록들은 오직 인증된 사용자가 지정된 목록을 소유한 경우에만 보여집니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.add_list_member(list_id/slug, screen_name/user_id, \
                                [owner_id/owner_screen_name])

   목록에 구성원을 추가합니다.
   인증된 사용자는 목록에 구성원을 추가하기 위해 목록을 소유해야 하며, 목록은 최대 5000명으로 제한되어 있습니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.add_list_members(list_id/slug, screen_name/user_id, \
                                 [owner_id/owner_screen_name])

   목록에 최대 100명의 구성원들을 추가합니다.
   인증된 사용자는 목록에 구성원을 추가하기 위해 목록을 소유해야 하며, 목록은 최대 5000명으로 제한되어 있습니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: 콤마로 닉네임 목록을 구분하며, 한 요청 당 100회로 제한됩니다.
   :param user_id: 콤마로 사용자 ID 목록을 구분하며, 한 요청 당 100회로 제한됩니다.
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.remove_list_member(list_id/slug, screen_name/user_id, \
                                   [owner_id/owner_screen_name])

   목록에서 지정된 구성원을 제외합니다.
   인증된 사용자는 목록에 구성원을 제외하기 위해 목록을 소유해야 합니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.remove_list_members(list_id/slug, screen_name/user_id, \
                                    [owner_id/owner_screen_name])

   목록에서 최대 100명의 구성원을 제외합니다.
   인증된 사용자는 목록에 구성원을 제외하기 위해 목록을 소유해야 하며, 목록은 최대 5000명으로 제한되어 있습니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: 콤마로 닉네임 목록을 구분하며, 한 요청 당 100회로 제한됩니다.
   :param user_id: 콤마로 사용자 ID 목록을 구분하며, 한 요청 당 100회로 제한됩니다.
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.list_members(list_id/slug, [owner_id/owner_screen_name], \
                             [cursor])

   지정된 목록의 구성원들을 반환합니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :param cursor: |cursor|
   :rtype: list of :class:`User` 객체


.. method:: API.show_list_member(list_id/slug, screen_name/user_id, \
                                 [owner_id/owner_screen_name])

   지정된 사용자가 지정된 목록의 구성원인지 확인합니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`User` 객체 if user is a member of list


.. method:: API.subscribe_list(list_id/slug, [owner_id/owner_screen_name])

   인증된 사용자를 지정된 목록에 구독시킵니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.unsubscribe_list(list_id/slug, [owner_id/owner_screen_name])

   인증된 사용자를 지정된 목록으로부터 구독 취소시킵니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`List` object


.. method:: API.list_subscribers(list_id/slug, [owner_id/owner_screen_name], \
                                 [cursor], [count], [include_entities], \
                                 [skip_status])

   지정된 목록의 구독자들을 반환합니다.
   private 상태의 목록 구독자들은 인증된 사용자가 지정된 목록을 소유하는 경우에만 표시됩니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :param cursor: |cursor|
   :param count: |count|
   :param include_entities: |include_entities|
   :param skip_status: |skip_status|
   :rtype: list of :class:`User` 객체


.. method:: API.show_list_subscriber(list_id/slug, screen_name/user_id, \
                                     [owner_id/owner_screen_name])

   지정된 사용자가 지정된 목록의 구독자인지 확인합니다.

   :param list_id: |list_id|
   :param slug: |slug|
   :param screen_name: |screen_name|
   :param user_id: |user_id|
   :param owner_id: |owner_id|
   :param owner_screen_name: |owner_screen_name|
   :rtype: :class:`User` 객체 if user is subscribed to list


트렌드 메소드
-------------

.. method:: API.trends_available()

   Twitter가 트렌드 정보를 가진 위치를 반환합니다.
   반환은 WOEID(The Yahoo! Where On Earth ID)를 인코딩한 “location"의 배열과
   정규 명칭 및 위치가 속한 국가같이 인간이 읽을 수 있는 정보로 이루어집니다.

   :rtype: :class:`JSON` object


.. method:: API.trends_place(id, [exclude])

   트렌드 정보를 이용할 수 있는 경우, 특정 WOEID에 대한 상위 50개의 트렌드를 반환합니다.

   반환은 트렌드의 이름을 인코딩한 "trend" 객체 배열, 트위터 검색에서 주제를 검색하는 데
   사용할 수 있는 쿼리 매개변수, 트위터 검색 URL로 이루어집니다.

   이 정보는 5분마다 캐싱됩니다.
   이보다 더 자주 요청하면 더 이상 데이터가 반환되지 않으며, 제한 사용량 비율에 반하여 계산합니다.

   최근 24시간 동안의 tweet_volume도 이용할 수 있다면 많은 트렌드에 맞게 반환됩니다.

   :param id: 트렌드 정보를 반환할 The Yahoo! Where On Earth ID.
              글로벌 정보는 WOEID를 1로 사용하여 이용할 수 있습니다.
   :param exclude: 이것을 해시태그와 동일하게 설정하면 트렌드 목록에서 모든 해시태그를 제거합니다.
   :rtype: :class:`JSON` object


.. method:: API.trends_closest(lat, long)

   Twitter가 지정된 위치로부터 트렌드 정보를 가지고 있는 가장 가까운 위치를 반환합니다.

   반환은 WOEID를 인코딩한 “location"의 배열과 정규 명칭 및 위치가 속한 국가같이
   인간이 읽을 수 있는 정보로 이루어집니다.

   WOEID는 Yahoo! Where On Earth ID를 뜻합니다.

   :param lat: long 매개변수와 함께 제공되면 이용 가능한 트렌드 위치는 거리별로 가장 가까운 위치부터 가장 먼 위치까지 좌표 쌍으로 정렬됩니다. 경도의 유효 범위는 -180.0~+180.0(서쪽은 음수, 동쪽은 양수)입니다.
   :param long: at 매개변수와 함께 제공되면 이용 가능한 트렌드 위치는 거리별로 가장 가까운 위치부터 가장 먼 위치까지 좌표 쌍으로 정렬됩니다. 경도의 유효 범위는 -180.0~+180.0(서쪽은 음수, 동쪽은 양수)입니다.

   :rtype: :class:`JSON` object


위치정보 메소드
---------------

.. method:: API.reverse_geocode([lat], [long], [accuracy], [granularity], \
                                [max_results])

   위도와 경도가 주어진 경우, `update_status()`를 위치의 이름을 나타내기 위해
   호출하여 지정될 수 있는 ID를 가진 장소(도시와 그 인접)를 찾습니다.
   이 호출은 해당 위치에 대한 상세한 반환을 제공하므로, `nearby_places()` 메소드는
   그다지 상세하지 않은 근처 장소의 목록을 얻는 데 사용하는 것이 추천됩니다.

   :param lat: 위치의 위도.
   :param long: 위치의 경도.
   :param accuracy: 숫자로 검색할 “region"을 지정합니다. 이 경우 미터로의 반경이지만, feet 단위로 지정하기 위해 ft와 접해있는 문자열도 사용할 수 있습니다. 입력되지 않으면 0m로 가정합니다.
   :param granularity: 기본적으로 ‘neighborhood’로 가정하지만 'city'일 수도 있습니다.
   :param max_results: 반환할 최대 결과 숫자에 대한 힌트. 이것은 단지 지침일 뿐, 지켜지지 않을 수도 있습니다.


.. method:: API.geo_id(id)

   장소에 대한 ID를 지정하면 장소에 대한 더 자세한 정보를 제공합니다.

   :param id: 위치의 유효한 Twitter ID.


유틸리티 메소드
---------------

.. method:: API.configuration()

   사용자 이름이 아닌 twitter.com 슬러그, 최대 사진 해상도, t.co 단축된 URL 길이 등을 포함한
   Twitter에서 사용하는 현재 구성을 반환합니다. 응용 프로그램이 로드될 때 이 endpoint를
   요청하는 것이 추천되지만, 하루에 1번 이상 요청하지 않는 것이 좋습니다.


미디어 메소드
-------------

.. method:: API.media_upload(filename, [file])

   이 endpoint를 사용하여 Twitter에 이미지를 업로드하세요.

   :param filename: 업로드할 이미지의 파일 이름. ``file``이 자동으로 지정되지 않는 한 자동으로 열리게 됩니다.
   :param file: ``filename``을 여는 대신 사용할 파일 객체. MME 타입 형식 감지 및 POST 데이터에서 양식 필드로 사용하려면 ``filename``도 필요합니다.

   :rtype: :class:`Media` object


.. method:: API.create_media_metadata(media_id, alt_text)

    이 endpoint는 업로드된 media_id에 대한 추가적인 정보를 제공하는데 사용될 수 있습니다.
    이 기능은 현재 이미지와 GIF에서만 지원됩니다.
    image al text와 같은 추가적인 metadata를 연결하려면 이 endpoint를 호출하세요.

   :param media_id: alt text를 추가할 media의 ID
   :param alt_text: 이미지에 추가할 Alt text


:mod:`tweepy.error` --- 예외
=============================

    예외는 ``tweepy`` 모듈에서 직접 이용 가능하며, 이것은 ``tweepy.error`` 자체를 가져올 필요가 없다는 것을 의미합니다.
    예를 들어, ``tweepy.error.TweepError`` 는 ``tweepy.TweepError`` 로 이용 가능합니다.


.. exception:: TweepError

    Tweepy가 사용하는 주요 예외. 많은 이유로 발생합니다.

    Twiiter가 응답한 오류로 인해 ``TweepError`` 가 발생하면, ``TweepError.response.text`` 에서
    에러 코드(API 문서<https://developer.twitter.com/en/docs/basics/response-codes>에서 설명된 대로)에 접근할 수 있습니다.
    단, ``TweepError`` 는 다른 것을 메시지(예: 일반적인 에러 문자열)로 표시하여 발생할 수도 있음에 유의하십시오.


.. exception:: RateLimitError

    API 메소드가 Twitter의 rate-limit에 도달하여 실패할 때 발생합니다.
    rate-limit을 특별히 쉽게 다룰 수 있도록 제작했습니다.

    `TweepError` 로부터 상속받으므로, ``except TweepError`` 또한 ``RateLimitError`` 를 잡을 수 있을겁니다.


.. rubric:: 각주

.. [#] https://web.archive.org/web/20170829051949/https://dev.twitter.com/rest/reference/get/search/tweets
.. [#] https://twittercommunity.com/t/favorited-reports-as-false-even-if-status-is-already-favorited-by-the-user/11145
