from django.contrib.auth.hashers import BasePasswordHasher
from collections import OrderedDict
import hashlib
import base64
from django.utils.crypto import (
    constant_time_compare, get_random_string, pbkdf2,
)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import mask_hash



class SHA1PasswordHasher(BasePasswordHasher):
    """
    The SHA1 password hashing algorithm (not recommended)
    """
    algorithm = "sha1"

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        hash = hashlib.sha1(password.encode() + base64.b64decode(salt)).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        pass
