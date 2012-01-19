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

The current, released version of Boto_ lacks DynamoDB support, so you'll need
to install from their current git master branch::

    pip install --upgrade git+http://github.com/boto/boto.git#egg=boto

This package hasn't made it to PyPi (and won't until Boto's API settles),
so you'll need to install this from git, as well::

    pip install --upgrade git+http://github.com/gtaylor/django-dynamodb-sessions.git#egg=dynamodb_sessions

In your ``settings.py`` file, you'll need something like this::

    SESSION_ENGINE = 'dynamodb_sessions.backends.dynamodb'
    DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID = 'YourKeyIDHere'
    DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY = 'YourSecretHere'

After that, keep an eye on your Amazon Management Console to see if you need
to scale your read/write units up or down.

If you encounter any bugs, have questions, or would like to share an idea,
hit up our `issue tracker`_.

.. _Boto: https://github.com/boto/boto
.. _issue tracker: https://github.com/gtaylor/django-dynamodb-sessions/issues

License
-------

django-dynamodb-sessions is licensed under the `BSD License`_.

.. _BSD License: https://github.com/gtaylor/django-dynamodb-sessions/blob/master/LICENSE