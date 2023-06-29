try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from unittest import SkipTest
    raise SkipTest("Skipping AsyncClient tests for Python 3.7")

from config import (
    access_token, access_token_secret, bearer_token, consumer_key,
    consumer_secret, tape, user_id
)
from tweepy.asynchronous import AsyncClient


class TweepyAsyncClientTests(IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = AsyncClient(
            bearer_token, consumer_key, consumer_secret,
            access_token or user_id, access_token_secret
        )

    @tape.use_cassette("test_asyncclient_bookmarks.yaml")
    async def test_bookmarks(self):
        tweet_id = 1507070437557096461
        # @TwitterDev Tweet announcing API v2 Bookmarks endpoints
        await self.client.bookmark(tweet_id)
        await self.client.get_bookmarks()
        await self.client.remove_bookmark(tweet_id)

    @tape.use_cassette("test_asyncclient_hide_and_unhide_reply.yaml")
    async def test_hide_and_unhide_reply(self):
        reply_id = 1344794616005066752  # Test Tweet for reply hide/unhide
        await self.client.hide_reply(reply_id)
        await self.client.unhide_reply(reply_id)

    @tape.use_cassette("test_asyncclient_like_and_unlike.yaml")
    async def test_like_and_unlike(self):
        tweet_id = 1293593516040269825  # @TwitterDev Tweet announcing API v2
        await self.client.like(tweet_id)
        await self.client.unlike(tweet_id)

    @tape.use_cassette("test_asyncclient_get_liking_users.yaml")
    async def test_get_liking_users(self):
        tweet_id = 1293593516040269825  # @TwitterDev Tweet announcing API v2
        await self.client.get_liking_users(tweet_id)

    @tape.use_cassette("test_asyncclient_get_liked_tweets.yaml")
    async def test_get_liked_tweets(self):
        user_id = 783214  # User ID for @Twitter
        await self.client.get_liked_tweets(user_id)

    @tape.use_cassette("test_asyncclient_create_and_delete_tweet.yaml")
    async def test_create_and_delete_tweet(self):
        response = await self.client.create_tweet(text="Test Tweet")
        tweet_id = response.data["id"]
        await self.client.delete_tweet(tweet_id)

    @tape.use_cassette("test_asyncclient_get_quote_tweets.yaml")
    async def test_get_quote_tweets(self):
        tweet_id = 1293593516040269825  # @TwitterDev Tweet announcing API v2
        await self.client.get_quote_tweets(tweet_id)

    @tape.use_cassette("test_asyncclient_retweet_and_unretweet.yaml")
    async def test_retweet_and_unretweet(self):
        tweet_id = 1415348607813832708
        # @TwitterDev Tweet announcing API v2 Retweet endpoints
        await self.client.retweet(tweet_id)
        await self.client.unretweet(tweet_id)

    @tape.use_cassette("test_asyncclient_get_retweeters.yaml")
    async def test_get_retweeters(self):
        tweet_id = 1415348607813832708
        # @TwitterDev Tweet announcing API v2 Retweet endpoints
        await self.client.get_retweeters(tweet_id)

    @tape.use_cassette("test_asyncclient_search_all_tweets.yaml")
    async def test_search_all_tweets(self):
        await self.client.search_all_tweets("Tweepy")

    @tape.use_cassette("test_asyncclient_search_recent_tweets.yaml")
    async def test_search_recent_tweets(self):
        await self.client.search_recent_tweets("Tweepy")

    @tape.use_cassette("test_asyncclient_get_users_mentions.yaml")
    async def test_get_users_mentions(self):
        user_id = 783214  # User ID for @Twitter
        await self.client.get_users_mentions(user_id)

    @tape.use_cassette("test_asyncclient_get_home_timeline.yaml")
    async def test_get_home_timeline(self):
        await self.client.get_home_timeline()

    @tape.use_cassette("test_asyncclient_get_users_tweets.yaml")
    async def test_get_users_tweets(self):
        user_id = 783214  # User ID for @Twitter
        await self.client.get_users_tweets(user_id)

    @tape.use_cassette("test_asyncclient_get_all_tweets_count.yaml")
    async def test_get_all_tweets_count(self):
        await self.client.get_all_tweets_count("Tweepy")

    @tape.use_cassette("test_asyncclient_get_recent_tweets_count.yaml")
    async def test_get_recent_tweets_count(self):
        await self.client.get_recent_tweets_count("Tweepy")

    @tape.use_cassette("test_asyncclient_get_tweet.yaml")
    async def test_get_tweet(self):
        tweet_id = 1293593516040269825  # @TwitterDev Tweet announcing API v2
        await self.client.get_tweet(tweet_id)

    @tape.use_cassette("test_asyncclient_get_tweets.yaml")
    async def test_get_tweets(self):
        tweet_ids = [1293593516040269825, 1293595870563381249]
        # @TwitterDev and @TwitterAPI Tweets announcing API v2
        await self.client.get_tweets(tweet_ids)

    # TODO: Test AsyncClient.get_blocked

    @tape.use_cassette("test_asyncclient_follow_and_unfollow_user.yaml")
    async def test_follow_and_unfollow_user(self):
        user_id = 17874544  # User ID for @TwitterSupport
        await self.client.follow_user(user_id)
        await self.client.unfollow_user(user_id)

    @tape.use_cassette("test_asyncclient_get_users_followers.yaml")
    async def test_get_users_followers(self):
        user_id = 783214  # User ID for @Twitter
        await self.client.get_users_followers(user_id)

    @tape.use_cassette("test_asyncclient_get_users_following.yaml")
    async def test_get_users_following(self):
        user_id = 2244994945  # User ID for @TwitterDev
        await self.client.get_users_following(user_id)

    @tape.use_cassette("test_asyncclient_mute_get_muted_and_unmute.yaml")
    async def test_mute_get_muted_and_unmute(self):
        user_id = 17874544  # User ID for @TwitterSupport
        await self.client.mute(user_id)
        await self.client.get_muted()
        await self.client.unmute(user_id)

    @tape.use_cassette("test_asyncclient_get_user.yaml")
    async def test_get_user(self):
        await self.client.get_user(username="Twitter")

    @tape.use_cassette("test_asyncclient_get_users.yaml")
    async def test_get_users(self):
        await self.client.get_users(usernames=["Twitter", "TwitterDev"])

    @tape.use_cassette("test_asyncclient_get_me.yaml")
    async def test_get_me(self):
        await self.client.get_me()

    @tape.use_cassette("test_asyncclient_search_spaces.yaml")
    async def test_search_spaces(self):
        await self.client.search_spaces("Twitter")

    @tape.use_cassette("test_asyncclient_get_spaces.yaml")
    async def test_get_spaces(self):
        space_ids = ["1ynKOZVRyOwxR", "1mrGmanRNNkGy"]
        # Space ID for @TwitterSpaces Spaces community gathering + Q&A
        # https://twitter.com/TwitterSpaces/status/1512506527025926150
        # Space ID for @TwitterMktg Twitter Trends ‘22: Finance Goes Social
        # https://twitter.com/TwitterMktg/status/1522634733867487234
        user_ids = [357750891, 1517225601463205888]
        # User IDs for @TwitterMktg and @TwitterVoices
        await self.client.get_spaces(ids=space_ids)
        await self.client.get_spaces(user_ids=user_ids)

    @tape.use_cassette("test_asyncclient_get_space.yaml")
    async def test_get_space(self):
        space_id = "1ynKOZVRyOwxR"
        # Space ID for @TwitterSpaces Spaces community gathering + Q&A
        # https://twitter.com/TwitterSpaces/status/1512506527025926150
        await self.client.get_space(space_id)

    # TODO: Test AsyncClient.get_space_buyers

    # TODO: Test AsyncClient.get_space_tweets

    @tape.use_cassette(
        "test_asyncclient_manage_and_lookup_direct_messages.yaml"
    )
    async def test_manage_and_lookup_direct_messages(self):
        user_ids = [145336962, 750362064426721281]
        # User IDs for @Harmon758 and @Harmon758Public
        response = await self.client.create_direct_message(
            participant_id=user_ids[1],
            text="Testing 1"
        )
        dm_conversation_id = response.data["dm_conversation_id"]
        await self.client.create_direct_message(
            dm_conversation_id=dm_conversation_id,
            text="Testing 2"
        )
        await self.client.create_direct_message_conversation(
            text="Testing",
            participant_ids=user_ids
        )
        await self.client.get_dm_events()
        await self.client.get_dm_events(dm_conversation_id=dm_conversation_id)
        await self.client.get_dm_events(participant_id=user_ids[1])

    @tape.use_cassette("test_asyncclient_get_list_tweets.yaml")
    async def test_get_list_tweets(self):
        list_id = 84839422  # List ID for Official Twitter Accounts (@Twitter)
        await self.client.get_list_tweets(list_id)

    @tape.use_cassette("test_asyncclient_follow_and_unfollow_list.yaml")
    async def test_follow_and_unfollow_list(self):
        list_id = 84839422  # List ID for Official Twitter Accounts (@Twitter)
        await self.client.follow_list(list_id)
        await self.client.unfollow_list(list_id)

    @tape.use_cassette("test_asyncclient_get_list_followers.yaml")
    async def test_get_list_followers(self):
        list_id = 84839422  # List ID for Official Twitter Accounts (@Twitter)
        await self.client.get_list_followers(list_id)

    @tape.use_cassette("test_asyncclient_get_followed_lists.yaml")
    async def test_get_followed_lists(self):
        user_id = 3015271772  # User ID for @TwitterFood
        await self.client.get_followed_lists(user_id)

    @tape.use_cassette("test_asyncclient_get_list.yaml")
    async def test_get_list(self):
        list_id = 84839422  # List ID for Official Twitter Accounts (@Twitter)
        await self.client.get_list(list_id)

    @tape.use_cassette("test_asyncclient_get_owned_lists.yaml")
    async def test_get_owned_lists(self):
        user_id = 783214  # User ID for @Twitter
        await self.client.get_owned_lists(user_id)

    @tape.use_cassette("test_asyncclient_get_list_members.yaml")
    async def test_get_list_members(self):
        list_id = 84839422  # List ID for Official Twitter Accounts (@Twitter)
        await self.client.get_list_members(list_id)

    @tape.use_cassette("test_asyncclient_get_list_memberships.yaml")
    async def test_get_list_memberships(self):
        user_id = 783214  # User ID for @Twitter
        await self.client.get_list_memberships(user_id)

    @tape.use_cassette("test_asyncclient_manage_and_get_pinned_lists.yaml")
    async def test_manage_and_get_pinned_lists(self):
        response = await self.client.create_list("Test List", private=True)
        list_id = response.data["id"]
        user_id = 783214  # User ID for @Twitter
        await self.client.add_list_member(list_id, user_id)
        await self.client.pin_list(list_id)
        await self.client.get_pinned_lists()
        await self.client.remove_list_member(list_id, user_id)
        await self.client.unpin_list(list_id)
        await self.client.update_list(
            list_id, description="Test List Description"
        )
        await self.client.delete_list(list_id)

    @tape.use_cassette(
        "test_asyncclient_create_and_get_compliance_job_and_jobs.yaml"
    )
    async def test_create_and_get_compliance_job_and_jobs(self):
        response = await self.client.create_compliance_job("tweets")
        job_id = response.data["id"]
        await self.client.get_compliance_job(job_id)
        await self.client.get_compliance_jobs("tweets")
