.. API parameters:

.. |count| replace:: 페이지 당 시도하고 검색할 결과의 수.
.. |cursor| replace:: 결과를 페이지로 나누며, 페이징을 시작하려면 -1 값을 입력해야 합니다. 응답 내용의 next_cursor와 previous_cursor 속성의 반환값을 입력해서 목록의 페이지를 앞뒤로 옮길 수 있습니다.
.. |date| replace:: 리포트 작성을 위한 시작 시간을 지정합니다. 날짜는 YYYY-MM-DD 형식이어야만 합니다.
.. |exclude| replace:: 해시태그와 동일하게 설정하면, 실시간 트렌드 리스트에서 모든 해시태그를 제거할 것입니다.
.. |full_text| replace:: 메시지의 전문을 반환할지 여부를 확인하기 위한 논리값. False라면 140자로 잘린 메시지 내용을 반환하게 됩니다. 기본값은 False입니다.
.. |include_card_uri| replace:: (card_uri 값을 통한 일반 카드 및 광고 카드를 포함하는 트윗이 있다면) 가져온 트윗이 card_uri 값을 포함해야 하는지를 나타내는 boolean 형태의 변수.
.. |include_entities| replace:: False로 설정하면 엔티티 노드를 포함하지 않습니다. 기본값은 True.
.. |include_ext_alt_text| replace:: 미디어 요소에 alt 속성 값이 있으면 ext_alt_text를 반환하는 파라미터. ext_alt_text는 미디어 요소의 상위 레벨 Key 값이 될 것입니다.
.. |include_user_entities| replace:: False로 설정되면 유저 객체 노드가 포함되지 않습니다. 기본값은 True.
.. |list_id| replace:: 목록의 숫자 ID.
.. |list_mode| replace:: 목록의 공개/비공개 여부. 변수는 public 또는 private가 될 수 있습니다. 지정하지 않으면 기본 값으로 public이 지정됩니다.
.. |list_owner| replace:: 리스트 소유자의 screen_name.
.. |max_id| replace:: ID가 지정된 ID보다 더 작은(즉, 더 이전의) 경우에만 반환합니다.
.. |owner_id| replace:: 슬러그에 의해 요청되는 목록을 소유한 사용자의 일련번호.
.. |owner_screen_name| replace:: 슬러그에 의해 요청되는 목록을 소유한 사용자의 계정 이름.
.. |page| replace:: 검색할 페이지를 지정합니더. 참고: 페이지 매김에 제한이 있습니다.
.. |screen_name| replace:: 사용자의 트위터 계정 이름. 유효한 계정 이름과 사용자 일련번호가 같이 있다면 명확하게 하는 데 도움이 됩니다.
.. |sid| replace:: status의 ID.
.. |since_id| replace:: ID가 지정된 ID보다 더 큰(즉, 더 최근의) 경우에만 반환합니다.
.. |skip_status| replace:: 상태가 반환된 유저 객체들에 포함될지에 대한 참/거짓 여부. 기본값은 False.
.. |slug| replace:: 숫자 일련번호를 대신하여 목록을 식별할 수 있습니다. 이것을 사용하기로 결정한 경우, owner_id 또는 owner_screen_name 매개변수를 사용하여 목록 소유자도 지정해야 한다는 점에 유의하세요.
.. |trim_user| replace:: 유저 ID가 반드시 유저 객체 대신 제공되어야 하는지를 나타내는 boolean 형태의 변수. 기본값은 False.
.. |uid| replace:: 사용자 일련번호 또는 계정 이름.
.. |user_id| replace:: 사용자 일련번호. 유효한 계정 이름과 유효한 일련번호가 같이 있다면 명확하게 하는 데 도움이 됩니다.

