# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

from tweepy.error import TweepError


class Model(object):

    def __getstate__(self):
        # pickle
        pickle = {}
        for k, v in self.__dict__.items():
            if k == '_api':
                # do not pickle the api reference
                continue
            pickle[k] = v
        return pickle


class Status(Model):

    def destroy(self):
        return self._api.destroy_status(self.id)

    def retweet(self):
        return self._api.retweet(self.id)

    def retweets(self):
        return self._api.retweets(self.id)

    def favorite(self):
        return self._api.create_favorite(self.id)


class User(Model):

    def timeline(self, **kargs):
        return self._api.user_timeline(user_id=self.id, **kargs)

    def friends(self, **kargs):
        return self._api.friends(user_id=self.id, **kargs)

    def followers(self, **kargs):
        return self._api.followers(user_idself.id, **kargs)

    def follow(self):
        self._api.create_friendship(user_id=self.id)
        self.following = True

    def unfollow(self):
        self._api.destroy_friendship(user_id=self.id)
        self.following = False


class DirectMessage(Model):

    def destroy(self):
        return self._api.destroy_direct_message(self.id)


class Friendship(Model):

    pass


class SavedSearch(Model):

    def destroy(self):
        return self._api.destroy_saved_search(self.id)


class SearchResult(Model):

    pass

class Retweet(Model):

    def destroy(self):
        return self._api.destroy_status(self.id)

class List(Model):

    def destroy(self):
        return self._api.destroy_list(self.slug)

# link up default model implementations.
models = {
    'status': Status,
    'user': User,
    'direct_message': DirectMessage,
    'friendship': Friendship,
    'saved_search': SavedSearch,
    'search_result': SearchResult,
    'retweet': Retweet,
    'list': List,
}

