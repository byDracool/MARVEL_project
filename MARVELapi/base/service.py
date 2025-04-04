import hashlib
from django.conf import settings


def compute_md5_hash(my_string):
    m = hashlib.md5()
    m.update(my_string.encode('utf-8'))
    return m.hexdigest()


def make_authorization():
    publickey = settings.PUBLIC_KEY
    privatekey = settings.PRIVATE_KEY
    ts = 1
    md5_hash = compute_md5_hash(f'{ts}{privatekey}{publickey}')
    query_params = f'?ts={ts}&apikey={publickey}&hash={md5_hash}'
    return query_params