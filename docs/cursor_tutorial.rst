.. _cursor_tutorial:

***************
커서 지침
***************

이 지침은 커서 객체를 이용한 페이징에 대한 세부 사항을 설명합니다.

들어가며
============

트위터 API 개발에서 페이징은 타임라인 반복, 사용자 목록, 쪽지, 그 외 여러 곳에서 자주 사용됩니다.
페이징을 수행하기 위해선 요청마다 페이지/커서 매개변수를 전달해야 합니다.
여기서 문제는 페이징 루프를 관리하기 위해선 많은 표준 코드를 필요로 한다는 점입니다.
트위피는 페이징을 더 쉽고 적은 코드로 돕기 위해 커서 객체를 가지고 있습니다.

구식 방법 vs 커서 방법
======================

먼저 인증된 사용자의 타임라인 내에서 status를 반복하는 방법을 구현해봅시다.
커서 객체가 도입되기 전에 사용하던 “구식 방법”은 다음과 같습니다::

   page = 1
   while True:
       statuses = api.user_timeline(page=page)
       if statuses:
           for status in statuses:
               # process status here
               process_status(status)
       else:
           # All done
           break
       page += 1  # next page

보시다시피, 페이징 루프마다 "page" 매개변수를 수동으로 관리해야 합니다.
다음은 커서 객체를 사용하는 코드 버전입니다::

   for status in tweepy.Cursor(api.user_timeline).items():
       # process status here
       process_status(status)

훨씬 좋아보입니다! 커서가 씬 뒤에서 모든 페이징 작업을 처리하므로, 결과 처리를 위한 코드에만 집중 할 수 있습니다.

API 메소드로 매개변수 전달하기
======================================

API 메소드로 매개변수를 전달해야 한다면 어떻게 하시겠습니까?

.. code-block :: python

   api.user_timeline(id="twitter")

커서를 호출 가능으로 전달했기 때문에, 메소드에 직접적으로 매개변수를 전달 할 수 없습니다.
대신 커서 생성자 메소드로 매개변수를 전달합니다::

   tweepy.Cursor(api.user_timeline, id="twitter")

이제 커서는 요청만 하면 매개변수를 전달해 줄 것입니다.

항목과 페이지
==============

지금까지 항목당 페이징을 반복하는 방법을 구현해보았습니다.
페이지별로 결과를 처리하려면 어떻게 하시겠습니까?
pages() 메소드를 사용해보세요::

   for page in tweepy.Cursor(api.user_timeline).pages():
       # 페이지는 status의 목록임
       process_page(page)


한계값
======

n개의 항목이나 페이지만 반환하기를 원한다면 어떻게 하시겠습니까?
items()나 pages() 메소드를 통해 원하는 한계값을 전달 할 수 있습니다.

.. code-block :: python

   # 처음에서 200개의 status만 반복시킴
   for status in tweepy.Cursor(api.user_timeline).items(200):
       process_status(status)

   # 처음에서 3페이지 까지만 반복시킴
   for page in tweepy.Cursor(api.user_timeline).pages(3):
       process_page(page)
