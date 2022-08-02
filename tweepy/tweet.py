# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


class Tweet(HashableID, DataMapping):
    """Tweets are the basic building block of all things Twitter. The Tweet
    object has a long list of ‘root-level’ fields, such as ``id``, ``text``,
    and ``created_at``. Tweet objects are also the ‘parent’ object to several
    child objects including ``user``, ``media``, ``poll``, and ``place``. Use
    the field parameter ``tweet.fields`` when requesting these root-level
    fields on the Tweet object.

    The Tweet object that can be found and expanded in the user resource.
    Additional Tweets related to the requested Tweet can also be found and
    expanded in the Tweet resource. The object is available for expansion with
    ``?expansions=pinned_tweet_id`` in the user resource or
    ``?expansions=referenced_tweets.id`` in the Tweet resource to get the
    object with only default fields. Use the expansion with the field
    parameter: ``tweet.fields`` when requesting additional fields to complete
    the object.

    .. versionadded:: 4.0

    Attributes
    ----------
    data : dict
        The JSON data representing the Tweet.
    id : int
        The unique identifier of the requested Tweet.
    text : str
        The actual UTF-8 text of the Tweet. See `twitter-text`_ for details on
        what characters are currently considered valid.
    attachments : dict | None
        Specifies the type of attachments (if any) present in this Tweet.
    author_id : int | None
        The unique identifier of the User who posted this Tweet.
    context_annotations : list
        Contains context annotations for the Tweet.
    conversation_id : int | None
        The Tweet ID of the original Tweet of the conversation (which includes
        direct replies, replies of replies).
    created_at : datetime.datetime | None
        Creation time of the Tweet.
    entities : dict | None
        Entities which have been parsed out of the text of the Tweet.
        Additionally see entities in Twitter Objects.
    geo : dict | None
        Contains details about the location tagged by the user in this Tweet,
        if they specified one.
    in_reply_to_user_id : int | None
        If the represented Tweet is a reply, this field will contain the
        original Tweet’s author ID. This will not necessarily always be the
        user directly mentioned in the Tweet.
    lang : str | None
        Language of the Tweet, if detected by Twitter. Returned as a BCP47
        language tag.
    non_public_metrics : dict | None
        Non-public engagement metrics for the Tweet at the time of the request. 

        Requires user context authentication.
    organic_metrics : dict | None
        Engagement metrics, tracked in an organic context, for the Tweet at the
        time of the request.

        Requires user context authentication.
    possibly_sensitive : bool | None
        This field only surfaces when a Tweet contains a link. The meaning of
        the field doesn’t pertain to the Tweet content itself, but instead it
        is an indicator that the URL contained in the Tweet may contain content
        or media identified as sensitive content. 
    promoted_metrics : dict | None
        Engagement metrics, tracked in a promoted context, for the Tweet at the
        time of the request.

        Requires user context authentication.
    public_metrics : dict | None
        Public engagement metrics for the Tweet at the time of the request.
    referenced_tweets : list[ReferencedTweet] | None
        A list of Tweets this Tweet refers to. For example, if the parent Tweet
        is a Retweet, a Retweet with comment (also known as Quoted Tweet) or a
        Reply, it will include the related Tweet referenced to by its parent.
    reply_settings : str | None
        Shows you who can reply to a given Tweet. Fields returned are
        "everyone", "mentioned_users", and "followers".
    source : str | None
        The name of the app the user Tweeted from.
    withheld : dict | None
        When present, contains withholding details for `withheld content`_.

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet

    .. _twitter-text: https://github.com/twitter/twitter-text/
    .. _withheld content: https://help.twitter.com/en/rules-and-policies/tweet-withheld-by-country
    """

    __slots__ = (
        "data", "id", "text", "attachments", "author_id",
        "context_annotations", "conversation_id", "created_at", "entities",
        "geo", "in_reply_to_user_id", "lang", "non_public_metrics",
        "organic_metrics", "possibly_sensitive", "promoted_metrics",
        "public_metrics", "referenced_tweets", "reply_settings", "source",
        "withheld"
    )

    def __init__(self, data):
        self.data = data
        self.id = int(data["id"])
        self.text = data["text"]

        self.attachments = data.get("attachments")

        self.author_id = data.get("author_id")
        if self.author_id is not None:
            self.author_id = int(self.author_id)

        self.context_annotations = data.get("context_annotations", [])

        self.conversation_id = data.get("conversation_id")
        if self.conversation_id is not None:
            self.conversation_id = int(self.conversation_id)

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = parse_datetime(self.created_at)

        self.entities = data.get("entities")
        self.geo = data.get("geo")

        self.in_reply_to_user_id = data.get("in_reply_to_user_id")
        if self.in_reply_to_user_id is not None:
            self.in_reply_to_user_id = int(self.in_reply_to_user_id)

        self.lang = data.get("lang")
        self.non_public_metrics = data.get("non_public_metrics")
        self.organic_metrics = data.get("organic_metrics")
        self.possibly_sensitive = data.get("possibly_sensitive")
        self.promoted_metrics = data.get("promoted_metrics")
        self.public_metrics = data.get("public_metrics")

        self.referenced_tweets = data.get("referenced_tweets")
        if self.referenced_tweets is not None:
            self.referenced_tweets = [
                ReferencedTweet(referenced_tweet)
                for referenced_tweet in self.referenced_tweets
            ]

        self.reply_settings = data.get("reply_settings")
        self.source = data.get("source")
        self.withheld = data.get("withheld")

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return f"<Tweet id={self.id} text={repr(self.text)}>"

    def __str__(self):
        return self.text


class ReferencedTweet(HashableID, DataMapping):
    """.. versionadded:: 4.0

    Attributes
    ----------
    data : dict
        The JSON data representing the referenced Tweet.
    id : int
        The unique identifier of the referenced Tweet.
    type : str

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
    """

    __slots__ = ("data", "id", "type")

    def __init__(self, data):
        self.data = data
        self.id = int(data["id"])
        self.type = data["type"]

    def __repr__(self):
        return f"<ReferencedTweet id={self.id} type={self.type}"
