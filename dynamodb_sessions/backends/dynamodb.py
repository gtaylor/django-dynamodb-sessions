import time
import logging

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.core.exceptions import SuspiciousOperation

from boto.dynamodb import connect_to_region
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError


TABLE_NAME = getattr(
    settings, 'DYNAMODB_SESSIONS_TABLE_NAME', 'sessions')
HASH_ATTRIB_NAME = getattr(
    settings, 'DYNAMODB_SESSIONS_TABLE_HASH_ATTRIB_NAME', 'session_key')
ALWAYS_CONSISTENT = getattr(
    settings, 'DYNAMODB_SESSIONS_ALWAYS_CONSISTENT', True)

AWS_ACCESS_KEY_ID = getattr(
    settings, 'DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID', False)
if not AWS_ACCESS_KEY_ID:
    AWS_ACCESS_KEY_ID = getattr(
        settings, 'AWS_ACCESS_KEY_ID')

AWS_SECRET_ACCESS_KEY = getattr(
    settings, 'DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY', False)
if not AWS_SECRET_ACCESS_KEY:
    AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')

AWS_REGION_NAME = getattr(settings, 'DYNAMODB_SESSIONS_AWS_REGION_NAME', False)
if not AWS_REGION_NAME:
    AWS_REGION_NAME = getattr(settings, 'AWS_REGION_NAME', 'us-east-1')

# We'll find some better way to do this.
_DYNAMODB_CONN = None

logger = logging.getLogger(__name__)


def dynamodb_connection_factory():
    """
    Since SessionStore is called for every single page view, we'd be
    establishing new connections so frequently that performance would be
    hugely impacted. We'll lazy-load this here on a per-worker basis. Since
    boto.dynamodb.layer2.Layer2 objects are state-less (aside from security
    tokens), we're not too concerned about thread safety issues.
    """

    global _DYNAMODB_CONN
    if not _DYNAMODB_CONN:
        logger.debug("Creating a DynamoDB connection.")
        _DYNAMODB_CONN = connect_to_region(
            AWS_REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    return _DYNAMODB_CONN


class SessionStore(SessionBase):
    """
    Implements DynamoDB session store.
    """

    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        self.table = dynamodb_connection_factory().get_table(TABLE_NAME)

    def load(self):
        """
        Loads session data from DynamoDB, runs it through the session
        data de-coder (base64->dict), sets ``self.session``.

        :rtype: dict
        :returns: The de-coded session data, as a dict.
        """

        try:
            item = self.table.get_item(
                self.session_key, consistent_read=ALWAYS_CONSISTENT)
        except (DynamoDBKeyNotFoundError, SuspiciousOperation):
            self.create()
            return {}

        session_data = item['data']
        return self.decode(session_data)

    def exists(self, session_key):
        """
        Checks to see if a session currently exists in DynamoDB.

        :rtype: bool
        :returns: ``True`` if a session with the given key exists in the DB,
            ``False`` if not.
        """

        key_already_exists = self.table.has_item(
            session_key,
            consistent_read=ALWAYS_CONSISTENT,
        )
        if key_already_exists:
            return True
        else:
            return False

    def create(self):
        """
        Creates a new entry in DynamoDB. This may or may not actually
        have anything in it.
        """

        while True:
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
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

        # If the save method is called with must_create equal to True, I'm
        # setting self._session_key equal to None and when
        # self.get_or_create_session_key is called the new
        # session_key will be created.
        if must_create:
            self._session_key = None

        self._get_or_create_session_key()
        item = self.table.new_item(self.session_key)
        # Queue up a PUT operation for UpdateItem, which preserves the
        # existing 'created' attribute.
        item.put_attribute('data', self.encode(self._get_session(no_load=must_create)))

        if must_create:

            item.put_attribute('created', int(time.time()))
            # We expect the data value to be False because we are creating a
            # new session
            item.put(expected_value={'data': False})
        else:
            # Commits the PUT UpdateItem for the 'data' attrib, meanwhile
            # leaving the 'created' attrib un-touched.
            item.save()

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

        key = self.table.layer2.build_key_from_values(
            self.table.schema,
            session_key,
            range_key=None
        )
        self.table.layer2.layer1.delete_item(self.table.name, key)
