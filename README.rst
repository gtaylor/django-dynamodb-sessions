django-dynamodb-sessions
========================

:Info: This package contains a simple Django session backend that uses
       Amazon's `DynamoDB`_ for data storage.
:Author: Greg Taylor

.. _DynamoDB: http://aws.amazon.com/dynamodb/

Status
------

media-nommer is currently in very early development. At this time, the
software is probably only appropriate for those with a strong grasp on
Python and Amazon AWS.

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
* Decide on throughput. The free tier is 5 read capacity units, 10 write.
* Finish the rest of the steps

After your table is created, you're ready to install the module on your
Django app.

.. _DynamoDB tab: https://console.aws.amazon.com/dynamodb/home

Installation
-------------

The current, released version of Boto_ lacks DynamoDB support, so you'll need
to install from their current git master branch::

    pip install --upgrade git+http://github.com/boto/boto.git#egg=boto

This package hasn't made it to PyPi (and won't until Boto's API settles),
so you'll need to install this from git, as well::

    pip install --upgrade git+http://github.com/gtaylor/django-dynamodb-sessions.git#egg=dynamodb_sessions

In your ``settings.py`` file, you'll need something like this::

    DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID = 'YourKeyIDHere'
    DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY = 'YourSecretHere'

If you'd like to add a caching layer between your application and DynamoDB
to reduce queries (like Django's cached_db backend), set your session
backend to::

    SESSION_ENGINE = 'dynamodb_sessions.backends.cached_dynamodb'

Otherwise, go straight to DynamoDB::

    SESSION_ENGINE = 'dynamodb_sessions.backends.dynamodb'
    DYNAMODB_SESSIONS_ALWAYS_CONSISTENT = True

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
                                      creation/edits.
:DYNAMODB_SESSIONS_AWS_ACCESS_KEY_ID: The access key for the AWS account
                                      to use for DynamoDB.
:DYNAMODB_SESSIONS_AWS_SECRET_ACCESS_KEY: The secret for the AWS account
                                          to use for DynamoDB.

License
-------

django-dynamodb-sessions is licensed under the `BSD License`_.

.. _BSD License: https://github.com/gtaylor/django-dynamodb-sessions/blob/master/LICENSE