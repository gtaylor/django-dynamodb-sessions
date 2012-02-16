django-dynamodb-sessions
========================

:Info: This package contains a simple Django session backend that uses
       Amazon's `DynamoDB`_ for data storage.
:Author: Greg Taylor

.. _DynamoDB: http://aws.amazon.com/dynamodb/

Status
------

django-dynamodb-sessions has seen some use on small test environments within
EC2. While it should be ready for prime time, it hasn't been heavily battle
tested just yet. Other notes:

* There is currently no management command to remove expired sessions. We
  can't re-use the Django cleanup command, so we'll have to write our own.
  This will be added in the next release, we're already setting expiration
  attributes to drive the cleanup.

Set up your DynamoDB Table
--------------------------

Before you can use this module, you'll need to visit your `DynamoDB tab`_
in the AWS Management Console. Then:

* Hit the *Create Table* button.
* Enter ``sessions`` as your table name. This can be something else, you'll
  just need to adjust the ``settings.DYNAMODB_SESSIONS_TABLE_NAME`` value
  accordingly.
* Select Primary Key Type = ``Hash``.
* Select a ``String`` hash attribute type.
* Enter ``session_key`` for *Hash Attribute Name*.
* Hit the *Continue* button.
* Decide on throughput. The free tier is 10 read capacity units, 5 write.
* Finish the rest of the steps

After your table is created, you're ready to install the module on your
Django app.

.. _DynamoDB tab: https://console.aws.amazon.com/dynamodb/home

Installation
-------------

Install django-dynamodb-sessions using ``pip`` or ``easy_install``::

    pip install django-dynamodb-sessions

In your ``settings.py`` file, you'll need something like this::

    DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID = 'YourKeyIDHere'
    DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY = 'YourSecretHere'

If you'd like to add a caching layer between your application and DynamoDB
to reduce queries (like Django's cached_db backend), set your session
backend to::

    SESSION_ENGINE = 'dynamodb_sessions.backends.cached_dynamodb'

Otherwise, go straight to DynamoDB::

    SESSION_ENGINE = 'dynamodb_sessions.backends.dynamodb'

After that, fire her up and keep an eye on your Amazon Management Console
to see if you need to scale your read/write units up or down.

If you encounter any bugs, have questions, or would like to share an idea,
hit up our `issue tracker`_.

.. _Boto: https://github.com/boto/boto
.. _issue tracker: https://github.com/gtaylor/django-dynamodb-sessions/issues

Configuration
-------------

The following settings may be used in your ``settings.py``:

:DYNAMODB_SESSIONS_TABLE_NAME: The table name to use for session data storage.
                               Defaults to ``sessions``.
:DYNAMODB_SESSIONS_TABLE_HASH_ATTRIB_NAME: The hash attribute name on your
                                           session table. Defaults
                                           to ``session_key``
:DYNAMODB_SESSIONS_ALWAYS_CONSISTENT: If you're not using this session backend
                                      behind a cache, you may want to force all
                                      reads from DynamoDB to be consistent.
                                      This may lead to slightly slower queries,
                                      but you'll never miss object
                                      creation/edits. Defaults to ``True``.
:DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID: The access key for the AWS account
                                      to use for DynamoDB.
:DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY: The secret for the AWS account
                                          to use for DynamoDB.

Changes
-------

0.3
^^^

* Re-packaging with setuptools instead of distutils.

0.2
^^^

* Correcting an issue with the cached_dynamodb backend.

0.1
^^^

* Initial release.

License
-------

django-dynamodb-sessions is licensed under the `BSD License`_.

.. _BSD License: https://github.com/gtaylor/django-dynamodb-sessions/blob/master/LICENSE