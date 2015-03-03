from django.contrib.sessions.tests import SessionTestsMixin
from django.test import TestCase

from .backends.dynamodb import SessionStore as DynamoDBSession
from .backends.cached_dynamodb import SessionStore as CachedDynamoDBSession


class DynamoDBTestCase(SessionTestsMixin, TestCase):
    
    backend = DynamoDBSession
    

class CachedDynamoDBTestCase(SessionTestsMixin, TestCase):
    
    backend = CachedDynamoDBSession
