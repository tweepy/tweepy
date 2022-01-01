# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from email.utils import parsedate_to_datetime

from tweepy.mixins import HashableID


class Model:

    def __init__(self, api=None):
        self._api = api

    def __getstate__(self):
        pickle = self.__dict__.copy()
        pickle.pop('_api', None)
        return pickle

    @classmethod
    def parse(cls, api, json):
        """Parse a JSON object into a model instance."""
        raise NotImplementedError

    @classmethod
    def parse_list(cls, api, json_list):
        """
            Parse a list of JSON objects into
            a result set of model instances.
        """
        results = ResultSet()

        if isinstance(json_list, dict):
            # Handle map parameter for statuses/lookup
            if 'id' in json_list:
                for _id, obj in json_list['id'].items():
                    if obj:
                        results.append(cls.parse(api, obj))
                    else:
                        results.append(cls.parse(api, {'id': int(_id)}))
                return results
            # Handle premium search
            if 'results' in json_list:
                json_list = json_list['results']

        for obj in json_list:
            if obj:
                results.append(cls.parse(api, obj))
        return results

    def __repr__(self):
        state = [f'{k}={v!r}' for (k, v) in vars(self).items()]
        return f'{self.__class__.__name__}({", ".join(state)})'


class ResultSet(list):
    """A list like object that holds results from a Twitter API query."""

    def __init__(self, max_id=None, since_id=None):
        super().__init__()
        self._max_id = max_id
        self._since_id = since_id

    @property
    def max_id(self):
        if self._max_id:
            return self._max_id
        ids = self.ids()
        # Max_id is always set to the *smallest* id, minus one, in the set
        return (min(ids) - 1) if ids else None

    @property
    def since_id(self):
        if self._since_id:
            return self._since_id
        ids = self.ids()
        # Since_id is always set to the *greatest* id in the set
        return max(ids) if ids else None

    def ids(self):
        return [item.id for item in self if hasattr(item, 'id')]


class BoundingBox(Model):

    @classmethod
    def parse(cls, api, json):
        result = cls(api)
        if json is not None:
            for k, v in json.items():
                setattr(result, k, v)
        return result

    def origin(self):
        """
        Return longitude, latitude of southwest (bottom, left) corner of
        bounding box, as a tuple.

        This assumes that bounding box is always a rectangle, which
        appears to be the case at present.
        """
        return tuple(self.coordinates[0][0])

    def corner(self):
        """
        Return longitude, latitude of northeast (top, right) corner of
        bounding box, as a tuple.

        This assumes that bounding box is always a rectangle, which
        appears to be the case at present.
        """
        return tuple(self.coordinates[0][2])


class DirectMessage(Model):

    @classmethod
    def parse(cls, api, json):
        dm = cls(api)
        if "event" in json:
            json = json["event"]
        setattr(dm, '_json', json)
        for k, v in json.items():
            setattr(dm, k, v)
        return dm

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['events']

        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results

    def delete(self):
        return self._api.delete_direct_message(self.id)


class Friendship(Model):

    @classmethod
    def parse(cls, api, json):
        relationship = json['relationship']

        # parse source
        source = cls(api)
        setattr(source, '_json', relationship['source'])
        for k, v in relationship['source'].items():
            setattr(source, k, v)

        # parse target
        target = cls(api)
        setattr(target, '_json', relationship['target'])
        for k, v in relationship['target'].items():
            setattr(target, k, v)

        return source, target


class List(Model):

    @classmethod
    def parse(cls, api, json):
        lst = List(api)
        setattr(lst, '_json', json)
        for k, v in json.items():
            if k == 'user':
                setattr(lst, k, User.parse(api, v))
            elif k == 'created_at':
                setattr(lst, k, parsedate_to_datetime(v))
            else:
                setattr(lst, k, v)
        return lst

    @classmethod
    def parse_list(cls, api, json_list, result_set=None):
        results = ResultSet()
        if isinstance(json_list, dict):
            json_list = json_list['lists']
        for obj in json_list:
            results.append(cls.parse(api, obj))
        return results

    def update(self, **kwargs):
        return self._api.update_list(self.slug, **kwargs)

    def destroy(self):
        return self._api.destroy_list(self.slug)

    def timeline(self, **kwargs):
        return self._api.list_timeline(
            self.user.screen_name, self.slug, **kwargs
        )

    def add_member(self, id):
        return self._api.add_list_member(self.slug, id)

    def remove_member(self, id):
        return self._api.remove_list_member(self.slug, id)

    def members(self, **kwargs):
        return self._api.get_list_members(
            self.user.screen_name, self.slug, **kwargs
        )

    def subscribe(self):
        return self._api.subscribe_list(self.user.screen_name, self.slug)

    def unsubscribe(self):
        return self._api.unsubscribe_list(self.user.screen_name, self.slug)

    def subscribers(self, **kwargs):
        return self._api.get_list_subscribers(
            self.user.screen_name, self.slug, **kwargs
        )


class Media(Model):

    @classmethod
    def parse(cls, api, json):
        media = cls(api)
        for k, v in json.items():
            setattr(media, k, v)
        return media


class Place(Model):

    @classmethod
    def parse(cls, api, json):
        place = cls(api)
        for k, v in json.items():
            if k == 'bounding_box':
                # bounding_box value may be null (None.)
                # Example: "United States" (id=96683cc9126741d1)
                if v is not None:
                    t = BoundingBox.parse(api, v)
                else:
                    t = v
                setattr(place, k, t)
            elif k == 'contained_within':
                # contained_within is a list of Places.
                setattr(place, k, Place.parse_list(api, v))
            else:
                setattr(place, k, v)
        return place

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['result']['places']

        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results


class Relationship(Model):
    @classmethod
    def parse(cls, api, json):
        result = cls(api)
        for k, v in json.items():
            if k == 'connections':
                setattr(result, 'is_following', 'following' in v)
                setattr(result, 'is_followed_by', 'followed_by' in v)
                setattr(result, 'is_muted', 'muting' in v)
                setattr(result, 'is_blocked', 'blocking' in v)
                setattr(result, 'is_following_requested', 'following_requested' in v)
                setattr(result, 'no_relationship', 'none' in v)
            else:
                setattr(result, k, v)
        return result


class SavedSearch(Model):

    @classmethod
    def parse(cls, api, json):
        ss = cls(api)
        for k, v in json.items():
            if k == 'created_at':
                setattr(ss, k, parsedate_to_datetime(v))
            else:
                setattr(ss, k, v)
        return ss

    def destroy(self):
        return self._api.destroy_saved_search(self.id)


class SearchResults(ResultSet):

    @classmethod
    def parse(cls, api, json):
        metadata = json['search_metadata']
        results = SearchResults()
        results.refresh_url = metadata.get('refresh_url')
        results.completed_in = metadata.get('completed_in')
        results.query = metadata.get('query')
        results.count = metadata.get('count')
        results.next_results = metadata.get('next_results')

        try:
            status_model = api.parser.model_factory.status
        except AttributeError:
            status_model = Status

        for status in json['statuses']:
            results.append(status_model.parse(api, status))
        return results


class Status(Model, HashableID):

    @classmethod
    def parse(cls, api, json):
        status = cls(api)
        setattr(status, '_json', json)
        for k, v in json.items():
            if k == 'user':
                try:
                    user = api.parser.model_factory.user.parse(api, v)
                except AttributeError:
                    user = User.parse(api, v)
                setattr(status, 'author', user)
                setattr(status, 'user', user)  # DEPRECIATED
            elif k == 'created_at':
                setattr(status, k, parsedate_to_datetime(v))
            elif k == 'source':
                if '<' in v:
                    # At this point, v should be of the format:
                    # <a href="{source_url}" rel="nofollow">{source}</a>
                    setattr(status, k, v[v.find('>') + 1:v.rfind('<')])
                    start = v.find('"') + 1
                    end = v.find('"', start)
                    setattr(status, 'source_url', v[start:end])
                else:
                    setattr(status, k, v)
                    setattr(status, 'source_url', None)
            elif k == 'retweeted_status':
                setattr(status, k, Status.parse(api, v))
            elif k == 'quoted_status':
                setattr(status, k, Status.parse(api, v))
            elif k == 'place':
                if v is not None:
                    setattr(status, k, Place.parse(api, v))
                else:
                    setattr(status, k, None)
            else:
                setattr(status, k, v)
        return status

    def destroy(self):
        return self._api.destroy_status(self.id)

    def retweet(self):
        return self._api.retweet(self.id)

    def retweets(self):
        return self._api.get_retweets(self.id)

    def favorite(self):
        return self._api.create_favorite(self.id)


class User(Model, HashableID):

    @classmethod
    def parse(cls, api, json):
        user = cls(api)
        setattr(user, '_json', json)
        for k, v in json.items():
            if k == 'created_at':
                setattr(user, k, parsedate_to_datetime(v))
            elif k == 'status':
                setattr(user, k, Status.parse(api, v))
            elif k == 'following':
                # twitter sets this to null if it is false
                if v is True:
                    setattr(user, k, True)
                else:
                    setattr(user, k, False)
            else:
                setattr(user, k, v)
        return user

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['users']

        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results

    def timeline(self, **kwargs):
        return self._api.user_timeline(user_id=self.id, **kwargs)

    def friends(self, **kwargs):
        return self._api.get_friends(user_id=self.id, **kwargs)

    def followers(self, **kwargs):
        return self._api.get_followers(user_id=self.id, **kwargs)

    def follow(self):
        self._api.create_friendship(user_id=self.id)
        self.following = True

    def unfollow(self):
        self._api.destroy_friendship(user_id=self.id)
        self.following = False

    def list_memberships(self, *args, **kwargs):
        return self._api.get_list_memberships(user_id=self.id, *args, **kwargs)

    def list_ownerships(self, *args, **kwargs):
        return self._api.get_list_ownerships(user_id=self.id, *args, **kwargs)

    def list_subscriptions(self, *args, **kwargs):
        return self._api.get_list_subscriptions(
            user_id=self.id, *args, **kwargs
        )

    def lists(self, *args, **kwargs):
        return self._api.get_lists(user_id=self.id, *args, **kwargs)

    def follower_ids(self, *args, **kwargs):
        return self._api.get_follower_ids(user_id=self.id, *args, **kwargs)


class IDModel(Model):

    @classmethod
    def parse(cls, api, json):
        if isinstance(json, list):
            return json
        else:
            return json['ids']


class JSONModel(Model):

    @classmethod
    def parse(cls, api, json):
        return json


class ModelFactory:
    """
    Used by parsers for creating instances
    of models. You may subclass this factory
    to add your own extended models.
    """

    bounding_box = BoundingBox
    direct_message = DirectMessage
    friendship = Friendship
    list = List
    media = Media
    place = Place
    relationship = Relationship
    saved_search = SavedSearch
    search_results = SearchResults
    status = Status
    user = User

    ids = IDModel
    json = JSONModel
