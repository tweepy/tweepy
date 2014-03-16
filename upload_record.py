import boto
from boto.s3.key import Key
from os import environ as env

conn = boto.connect_s3()
bucket = conn.get_bucket(env['AWS_BUCKET'])
k = bucket.get_key('record', validate=False)
k.set_contents_from_filename('tests/record.json')
k.set_acl('public-read')
k.close(fast=True)
