.. API parameters:

.. |count| replace:: 페이지 당 시도하고 검색할 결과의 수.
.. |cursor| replace:: 결과를 페이지로 나눕니다. 페이징을 시작하려면 -1 값을 입력하세요. 응답 내용의 next_cursor와 previous_cursor 속성의 반환값을 입력해서 목록의 페이지를 앞뒤로 옮기세요.
.. |date| replace:: Permits specifying a start date for the report. The date should be formatted YYYY-MM-DD.
.. |exclude| replace:: Setting this equal to hashtags will remove all hashtags from the trends list.
.. |full_text| replace:: 메시지의 전문을 반환할지 여부를 확인하기 위한 논리값. False라면 140자로 잘린 메시지 내용을 반환하게 됩니다. 기본값은 False입니다.
.. |include_card_uri| replace:: A boolean indicating if the retrieved Tweet should include a card_uri attribute when there is an ads card attached to the Tweet and when that card was attached using the card_uri value.
.. |include_entities| replace:: false로 설정하면 엔티티 노드를 포함하지 않습니다. 기본값은 true.
.. |include_ext_alt_text| replace:: If alt text has been added to any attached media entities, this parameter will return an ext_alt_text value in the top-level key for the media entity.
.. |include_user_entities| replace:: The user object entities node will not be included when set to false. Defaults to true.
.. |list_id| replace:: 목록의 숫자ID.
.. |list_mode| replace:: 목록의 공개/비공개 여부. 변수는 public 또는 private가 될 수 있습니다. 지정하지 않으면 기본 값으로 public이 지정됩니다.
.. |list_owner| replace:: the screen name of the owner of the list
.. |max_id| replace:: ID가 지정된 ID보다 더 작은(즉, 더 이전의) 경우에만 반환합니다.
.. |owner_id| replace:: 슬러그에 의해 요청되는 목록을 소유한 사용자의 ID.
.. |owner_screen_name| replace:: 슬러그에 의해 요청되는 목록을 소유한 사용자의 닉네임.
.. |page| replace:: 검색할 페이지를 지정합니더. 참고: 페이지 매김에 제한이 있습니다.
.. |screen_name| replace:: 사용자의 닉네임을 지정하세요. 유효한 닉네임과 사용자 ID가 같이 있다면 명확하게 하는 데 도움이 됩니다.
.. |sid| replace:: status의 ID.
.. |since_id| replace:: ID가 지정된 ID보다 더 큰(즉, 더 최근의) 경우에만 반환합니다.
.. |skip_status| replace:: 상태가 반환된 유저 객체들에 포함될지에 대한 참/거짓 여부. 기본값은 false.
.. |slug| replace:: 숫자ID를 대신하여 목록을 식별할 수 있습니다. 이것을 사용하기로 결정한 경우, owner_id 또는 owner_screen_name 매개변수를 사용하여 목록 소유자도 지정해야 한다는 점에 유의하세요.
.. |trim_user| replace:: A boolean indicating if user IDs should be provided, instead of complete user objects. Defaults to False.
.. |uid| replace:: 사용자의 ID 또는 screen name을 명시하세요.
.. |user_id| replace:: 사용자의 ID를 지정하세요. 유효한 사용자 ID와 유효한 닉네임이 같이 있다면 명확하게 하는 데 도움이 됩니다.

