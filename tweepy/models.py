# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

from . error import TweepError


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

    @staticmethod
    def _validate(model, attributes):
        missing = []
        for attr in attributes:
            if not hasattr(model, attr):
                missing.append(attr)
        if len(missing) > 0:
            raise TweepError('Missing required attribute(s) %s' % \
                                str(missing).strip('[]'))

    def validate(self):
        return


class Status(Model):

    @staticmethod
    def _validate(status):
        Model._validate(status, [
          'created_at', 'id', 'text', 'source', 'truncated', 'in_reply_to_status_id',
          'in_reply_to_user_id', 'favorited', 'in_reply_to_screen_name'
        ])
        if hasattr(status, 'user'):
            User._validate(status.user)

    def validate(self):
        Status._validate(self)

    def destroy(self):
        return self._api.destroy_status(id=self.id)


class User(Model):

    @staticmethod
    def _validate(user):
        Model._validate(user, [
            'id', 'name', 'screen_name', 'location', 'description', 'profile_image_url',
            'url', 'protected', 'followers_count', 'profile_background_color',
            'profile_text_color', 'profile_sidebar_fill_color',
            'profile_sidebar_border_color', 'friends_count', 'created_at',
            'favourites_count', 'utc_offset', 'time_zone',
            'profile_background_image_url', 'statuses_count',
            'notifications', 'following', 'verified'
        ])
        if hasattr(user, 'status'):
            Status._validate(user.status)

    def validate(self):
        User._validate(self)

    def timeline(self, **kargs):
        return self._api.user_timeline(**kargs)

    def mentions(self, **kargs):
        return self._api.mentions(**kargs)

    def friends(self, **kargs):
        return self._api.friends(id=self.id, **kargs)

    def followers(self, **kargs):
        return self._api.followers(id=self.id, **kargs)

    def follow(self):
        self._api.create_friendship(user_id=self.id)
        self.following = True

    def unfollow(self):
        self._api.destroy_friendship(user_id=self.id)
        self.following = False


class DirectMessage(Model):

    def destroy(self):
        return self._api.destroy_direct_message(id=self.id)


class Friendship(Model):

    pass


class SavedSearch(Model):

    pass


class SearchResult(Model):

    pass

# link up default model implementations.
models = {
    'status': Status,
    'user': User,
    'direct_message': DirectMessage,
    'friendship': Friendship,
    'saved_search': SavedSearch,
    'search_result': SearchResult
}

