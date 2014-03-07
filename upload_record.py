import dropbox
from os import environ as env

client = dropbox.client.DropboxClient(env.get('DROPBOX_ACCESS_TOKEN'))
with open('tests/record.json', 'r') as f:
    client.put_file('/path/to/record.json', f)

print "Record.json successfully uploaded to Dropbox!"
