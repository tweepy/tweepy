# Extensions to Tweepy for the Account Activity API      
# Licence as LICENSE file.
# Simon Lucy (bpluly) 

import tweepy

from tweepy.binder import bind_api
from tweepy.error import TweepError
from tweepy.parsers import JSONParser, Parser
from tweepy.api import API



  
class ActivityAPI(API):
      pass
      

      def enable_activity(self, *args, **kwargs):
          """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium
              :allowed_param:'url', 'env'
          """
          post_data = {}
          env = kwargs.pop('env')
          if env is not None:
            apiPath = '/account_activity/all/'+env+'/webhooks.json'
          else:
            apiPath = '/account_activity/all/webhooks.json'
          
          self.cache=None
          self.use_cache=False
          self.parser=JSONParser()
          return bind_api(
              api=self,
              path=apiPath,
              method='POST',
              payload_type='status',
              allowed_param=['url'],
              require_auth=True,
              use_cache=False,
          )(post_data=post_data, *args, **kwargs)        
      
      def subscribe_activity(self, *args, **kwargs):
          """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium
              :allowed_param:'url', 'env'
          """
          post_data = {}
          env = kwargs.pop("env")
          apiPath = '/account_activity/all/'+env+'/subscriptions.json'

          return bind_api(
              api=self,
              path=apiPath,
              method='POST',
              payload_type='status',
              require_auth=True
          )(post_data=post_data, *args, **kwargs)        
          
      def subscription(self, *args, **kwargs):
          """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium
              :allowed_param:'url', 'env'
          """
          post_data = {}
          env = kwargs.pop('env')
          if env is not None:
            apiPath = '/account_activity/all/'+env+'/subscriptions.json'
          else:
            apiPath = '/account_activity/all/subscriptions.json'

          return bind_api(api=self, path=apiPath, method='GET', payload_type='status', require_auth=True, use_cache=False)()
                                      
      
      def getWebID(self, *args, **kwargs):
          """:reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium
              :allowed_param:'env'. 
              :returns: an array of JSON. The Twitter documentation is out of date the current format is
              [{"id":"9999999999999999","url":"https://api.blah-blah/webhook","valid":true,"created_timestamp":"2019-09-16 16:47:16 +0000"}] 
          """
          post_data = {}
          env = kwargs.pop('env')
          if env is not None:
            apiPath = '/account_activity/all/'+env+'/webhooks.json'
          else:
            apiPath = '/account_activity/all/webhooks.json'

          return bind_api(api=self, path=apiPath, method='GET', payload_type='json', require_auth=True, use_cache=False)()

      def putWebID(self, *args, **kwargs):
          """:reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium
              :allowed_param:'env'. 
              :returns: an array of JSON. The Twitter documentation is out of date the current format is
              [{"id":"9999999999999999","url":"https://api.blah-blah/webhook_id","valid":true,"created_timestamp":"2019-09-16 16:47:16 +0000"}] 
          """
          post_data = {}
          env = kwargs.pop('env')
          if env is not None:
            apiPath = '/account_activity/all/'+env+'/webhook_id.json'
          else:
            apiPath = '/account_activity/all/webhook_id.json'

          return bind_api(api=self, path=apiPath, method='PUT', payload_type='json', require_auth=True, use_cache=False)()
                    
      def getSubsUsers(self, *args, **kwargs):
          """:reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium
              :allowed_param:'env'. 
              :returns: an array of JSON. 
          """
          post_data = {}
          env = kwargs.pop('env')
          if env is not None:
            apiPath = '/account_activity/all/'+env+'/subscriptions/list.json'
          else:
            apiPath = '/account_activity/all/subscriptions/list.json'

          return bind_api(api=self, path=apiPath, method='GET', payload_type='json', require_auth=True, use_cache=False)()
 
      def getSubsCount(self, *args, **kwargs):
          """:reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium
              :allowed_param:'env'. 
              :returns: an array of JSON. 
          """
          post_data = {}
          env = kwargs.pop('env')
          if env is not None:
            apiPath = '/account_activity/all/subscriptions/count.json'
          else:
            apiPath = '/account_activity/all/subscriptions/count.json'

          return bind_api(api=self, path=apiPath, method='GET', payload_type='json', require_auth=True, use_cache=False)()
                              
      def replay(self, *args, **kwargs):
          """ :reference: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/replay-api
              :allowed_param:'fromDate', 'toDate'. 'env', format is fromDate=yyyymmddhhmm toDate=yyyymmddhhmm
          """
          post_data = {}
          webhookid = kwargs.pop('webhookid')

          apiPath = '/account_activity/replay/webhooks/'+webhookid+'/subscriptions/all.json'
          
          self.cache=None
          self.use_cache=False
          self.parser=JSONParser()
          return bind_api(
              api=self,
              path=apiPath,
              method='POST',
              payload_type='status',
              allowed_param=['fromDate', 'toDate'],
              require_auth=True,
              use_cache=False,
          )(post_data=post_data, *args, **kwargs)                                  
