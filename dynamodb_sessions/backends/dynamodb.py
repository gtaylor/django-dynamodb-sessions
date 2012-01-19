import boto
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError

TABLE_NAME = getattr(settings, 'DYNAMODB_SESSIONS_TABLE_NAME', 'sessions')
SESSION_KEY = getattr(settings, 'DYNAMODB_SESSIONS_TABLE_PRIMARY_KEY', 'session_key')

AWS_ACCESS_KEY_ID = getattr(settings, 'DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID', False)
if not AWS_ACCESS_KEY_ID:
    AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')

AWS_SECRET_ACCESS_KEY = getattr(settings, 'DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY', False)
if not AWS_SECRET_ACCESS_KEY:
    AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')

class SessionStore(SessionBase):
    """
    Implements DynamoDB session store.
    """
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)

        print "Creating a connection."
        layer = boto.connect_dynamodb(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.table = layer.get_table(TABLE_NAME)

    def load(self):
        """
        Loads session data from DynamoDB, runs it through the session
        data de-coder (base64->dict), sets ``self.session``.

        :rtype: dict
        :returns: The de-coded session data, as a dict.
        """
        print "LOADING SESSION", self.session_key
        try:
            item = self.table.get_item(self.session_key)
        except KeyError:
            self.create()
            return {}

        session_data = item.attrs['data']
        return self.decode(session_data)

    def exists(self, session_key):
        """
        Checks to see if a session currently exists in DynamoDB.

        :rtype: bool
        :returns: ``True`` if a session with the given key exists in the DB,
            ``False`` if not.
        """
        print "SESSION EXISTS?", session_key
        try:
            # TODO: Update this once Layer2 has has_key.
            self.table.get_item(
                session_key,
                attributes_to_get=[SESSION_KEY],
            )
        except KeyError:
            return False

        return True

    def create(self):
        """
        Creates a new entry in DynamoDB. This may or may not actually
        have anything in it.
        """
        print "CREATING SESSION"
        while True:
            self.session_key = self._get_new_session_key()
            print "  GENERATED KEY:", self.session_key
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        """
        Saves the current session data to the database.

        :keyword bool must_create: If ``True``, a ``CreateError`` exception will
            be  raised if the saving operation doesn't create a *new* entry
            (as opposed to possibly updating an existing entry).
        :raises: ``CreateError`` if ``must_create`` is ``True`` and a session
            with the current session key already exists.
        """
        session_key = self._get_or_create_session_key()
        print "SAVING SESSION", session_key
        if must_create:
            try:
                self.table.get_item(session_key)
                # There's already an item with this key.
                raise CreateError
            except KeyError:
                # There's already an item with this key. We're golden.
                pass

        # This base64 encodes session data.
        data = self.encode(self._get_session(no_load=must_create))
        item = self.table.new_item(
            session_key,
            # Stuff the base64 encoded stuff into the 'data' attrib.
            attrs={'data': data}
        )
        item.put()

    def delete(self, session_key=None):
        """
        Deletes the current session, or the one specified in ``session_key``.

        :keyword str session_key: Optionally, override the session key
            to delete.
        """
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key

        print "DELETING SESSION", session_key
        try:
            item = self.table.get_item(session_key)
        except KeyError:
            # The item is already gone. Fail silently.
            return

        item.delete()
