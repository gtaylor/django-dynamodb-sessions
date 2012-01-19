django-dynamodb-sessions
========================

This package contains a simple Django session backend that uses
Amazon's `DynamoDB`_ for data storage.

.. _DynamoDB: http://aws.amazon.com/dynamodb/

Status
------

media-nommer is currently in very early development. At this time, the
software is probably only appropriate for those with a strong grasp on
Python and Amazon AWS.

Installation
-------------

In your ``settings.py`` file, you'll need something like this::

    SESSION_ENGINE = 'dynamodb_sessions.backends.dynamodb'
    DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID = 'YourKeyIDHere'
    DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY = 'YourSecretHere'

License
-------

django-dynamodb-sessions is licensed under the `BSD License`_.

.. _BSD License: https://github.com/gtaylor/django-dynamodb-sessions/blob/master/LICENSE