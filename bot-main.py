#!/usr/bin/python3

from urllib.parse import urlparse
from gmapi import api
import gmapi, shlex, sys, http.client, http.server

def fetchPastebin(fileId):
    conn = http.client.HTTPSConnection('pastebin.com')
    conn.request('GET', '/raw/%s' % fileID, None, {'User-agent': 'gmapi',
        'Accept': '*/*'})
    resp = conn.getresponse()
    if resp.code != 200:
        raise ValueError('Invalid pastebin url')

    data = resp.read()
    conn.close()
    return data

def fetchGist(user, fileId, rev = ''):
    if rev:
        rev = '/' + rev

    conn = http.client.HTTPSConnection('gist.github.com')
    conn.request('GET', '/%s/%s/raw%s' % (user, fileId, rev), None, {'User-agent': 'gmapi',
        'Accept': '*/*'})
    resp = conn.getresponse()
    if resp.code != 200:
        raise ValueError('Invalid gist url')

    data = resp.read()
    conn.close()
    return data

def fetchCode(url):
    o = urlparse(url)
    if not o.scheme:
        url = 'http://' + url
        o = urlparse(url)
    
    valid = False
    if o.netloc == 'pastebin.com':
        parts = o.path.split('/')
        if len(parts) == 1:
            return fetchPastebin(parts[0])
        elif len(parts) == 2:
            validCmds = {'raw', 'edit', 'print'}
            if parts[0] in validCmds:
                return fetchPastebin(parts[1])
        raise ValueError('Invalid pastebin url')
    elif o.netloc == 'gist.github.com':
        parts = o.path.split('/')
        if len(parts) == 2 or (len(parts) == 3 and parts[2] == 'raw'):
            return fetchGist(parts[0],  parts[1])
        elif len(parts) == 4 and parts[2] == 'raw':
            return fetchGist(parts[0], parts[1], parts[3])
        else:
            raise ValueError('Invalid gist url')
    else:
        raise ValueError('Please specify a valid github gist or pastebin url')

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        msg = gmapi.Message(json.loads(self.rfile.read()))
        print(msg)
        #msgParser.parseMessage(msg.text)

def run(host, port, api):
    httpd = http.server.HTTPServer((host, port), CallbackHandler)
    httpd.serve_forever()

host = '0.0.0.0'
port = 8080

sys.stdout.write('Input access token: ')
token = input()

print('Loading...\n')
api.auth(token)
api.init()

bots = [b for b in api.bots()]

print('You have the following bots:')
for i in range(len(bots)):
    b = bots[i]
    print(' %d. %s' % (i + 1, b))
    print('    Listens to: %s' % (b.group, 'dm notifications') \
            [b.dm_notifications])
sys.stdout.write('Select the bot as output (input the index): ')

bot = bots[int(input()) - 1]
#msgParser = cmd.CmdParser(bot.postMessage)




