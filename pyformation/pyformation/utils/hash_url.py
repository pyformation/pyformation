import hashlib
import json
import os
from pyformation import settings

def hash_file(project_name, stack):
    try:
        f = open(os.path.join(settings.PROJECT_DIR,
                              project_name, 'build', '{}.json'.format(stack.lower())), 'r')
        jsonfile = f.read().encode('utf-8')
    except Exception as e:
        print(e)
        print('failed to reading in stack Jsob')
        raise e
    res = hashlib.md5(jsonfile)
    return '{}-{}-{}.json'.format(project_name.lower(),stack.lower(), res.hexdigest())


def hash_url(project_name, stack):
    bucket = os.getenv('ARTIFACT_BUCKET', 'no-bucket')
    filename = hash_file(project_name, stack)
    url = 'https://s3.amazonaws.com/{}/{}'.format(bucket, filename)
    return url