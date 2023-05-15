#    Copyright 2012 Kjell Braden <afflux@pentabarf.de>
#
#    This file is part of the python-potr library.
#
#    python-potr is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    any later version.
#
#    python-potr is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this library.  If not, see <http://www.gnu.org/licenses/>.


from Cryptodome import Cipher
from Cryptodome.Hash import HMAC as _HMAC
from Cryptodome.Hash import SHA256 as _SHA256
from Cryptodome.Hash import SHA as _SHA1
from Cryptodome.PublicKey import DSA
from Cryptodome.Random import random
from Cryptodome.Signature import DSS
from Cryptodome.Util import Counter

try:
  import Crypto
except ImportError:
  import crypto as Crypto

from Crypto import Cipher

from numbers import Number

from potr.compatcrypto import common
from potr.utils import read_mpi, bytes_to_long, long_to_bytes

def SHA256(data):
    return _SHA256.new(data).digest()

def SHA1(data):
    return _SHA1.new(data).digest()

def SHA1HMAC(key, data):
    return _HMAC.new(key, msg=data, digestmod=_SHA1).digest()

def SHA256HMAC(key, data):
    return _HMAC.new(key, msg=data, digestmod=_SHA256).digest()

def AESCTR(key, counter=0):
    if isinstance(counter, Number):
        counter = Counter.new(nbits=64, prefix=long_to_bytes(counter, 8), initial_value=0)
    # in pycrypto Counter used to be an object,
    # in pycryptodome it's now only a dict.
    # This tries to validate its "type" so we don't feed anything as a counter
    if set(counter) != set(Counter.new(64)):
        raise TypeError
    return Cipher.AES.new(key, Cipher.AES.MODE_CTR, counter=counter)

@common.registerkeytype
class DSAKey(common.PK):
    keyType = 0x0000

    def __init__(self, key=None, private=False):
        self.priv = self.pub = None

        if not isinstance(key, tuple):
            raise TypeError('4/5-tuple required for key')

        if len(key) == 5 and private:
            self.priv = DSA.construct(key)
            self.pub = self.priv.publickey()
        elif len(key) == 4 and not private:
            self.pub = DSA.construct(key)
        else:
            raise TypeError('wrong number of arguments for ' \
                    'private={0!r}: got {1} '
                    .format(private, len(key)))

    def getPublicPayload(self):
        return (self.pub.p, self.pub.q, self.pub.g, self.pub.y)

    def getPrivatePayload(self):
        return (self.priv.p, self.priv.q, self.priv.g, self.priv.y, self.priv.x)

    def fingerprint(self):
        return SHA1(self.getSerializedPublicPayload())

    def sign(self, data):
        # 2 <= K <= q
        K = randrange(2, self.priv.q)
        M = bytes_to_long(data)
        r, s = self.priv._sign(M, K)
        return long_to_bytes(r, 20) + long_to_bytes(s, 20)

    def verify(self, data, sig):
        r, s = bytes_to_long(sig[:20]), bytes_to_long(sig[20:])
        M = bytes_to_long(data)
        return self.pub._verify(M, (r, s))

    def __hash__(self):
        return bytes_to_long(self.fingerprint())

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.fingerprint() == other.fingerprint()

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def generate(cls):
        privkey = DSA.generate(1024)
        return cls((privkey.y, privkey.g, privkey.p, privkey.q,
                privkey.x), private=True)

    @classmethod
    def parsePayload(cls, data, private=False):
        p, data = read_mpi(data)
        q, data = read_mpi(data)
        g, data = read_mpi(data)
        y, data = read_mpi(data)
        if private:
            x, data = read_mpi(data)
            return cls((y, g, p, q, x), private=True), data
        return cls((y, g, p, q), private=False), data

def getrandbits(k):
    return random.getrandbits(k)

def randrange(start, stop):
    return random.randrange(start, stop)
