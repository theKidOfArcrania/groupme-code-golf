#!/usr/bin/python3

import sys, http.client, json, re;
from datetime import datetime
from itertools import chain

class _GroupmeAPI:
    def __init__(self):
        self._conn = http.client.HTTPSConnection('api.groupme.com')
        self._login = False

    def _get_user(self, uid, name):
        if not uid in self._users:
            self._users[uid] = User(uid, name)
        return self._users[uid]


    def _connect(self, req, method='GET', data=None, headers={}):
        hd = self._headers.copy()
        hd.update(headers)
        conn = self._conn
        conn.request(method, req, data, hd)
        data = json.loads(conn.getresponse().read().decode('utf-8'))
        code = data['meta']['code'] // 100
        conn.close()
        print('gmapi: responded with code %d' % data['meta']['code'])
        if code == 4:
            sys.stderr.write('gmapi: Error with reading request: \n')
            for s in data['meta']['errors']:
                sys.stderr.write('  ' + s + '\n')
            return
        elif code == 5:
            sys.stderr.write('gmapi: Internal server error')
            return

        return data['response']

    def auth(self, token):
        self._login = True
        self._headers = {'X-Access-Token': token, 'User-Agent': 'gmapi', 
                    'Accept': '*/*'}
        self._groups = None
        self._bots = None
        self._users = {}

    def init(self, forceInit = False):
        if not self._login:
            raise ValueError('Not logged in!')

        for g in chain(self.bots(forceInit), self.groups(forceInit)):
            pass
        for b in self.bots(forceInit):
            pass

    def bots(self, forceInit = False):
        if not self._login:
            raise ValueError('Not logged in!')

        for g in self.groups():
            pass

        if self._bots != None and not forceInit:
            for b in self._bots.values():
                yield b
            return

        if self._bots == None:
            self._bots = {}

        resp = self._connect('/v3/bots')
        if resp == None:
            return

        for b in map(Bot, resp):
            self._bots[b.id] = b
            yield b

    def groups(self, forceInit = False):
        if not self._login:
            raise ValueError('Not logged in!')

        if self._groups != None and not forceInit:
            for g in self._groups.values():
                yield g
            return
        
        if self._groups == None:
            self._groups = {}

        page = 1
        more = True
        while more:
            resp = self._connect('/v3/groups?page=%d' % page)
            if resp == None:
                return

            if len(resp) == 0:
                more = False
            else:
                for gr in resp:
                    if gr['id'] in self._groups:
                        g = self._groups[gr['id']]
                        g._name = gr['name']
                    else:
                        g = Group(gr['id'], gr['name'])
                        self._groups[g.id] = g
                    yield g
                page += 1

class Group:
    def __init__(self, gid, name):
        self._id = gid
        self._name = name

    def messages(self):
        count = 1
        read = 0
        before = ''
        more = True

        while read < count:
            resp = api._connect('GET', '/v3/groups/%s/messages?limit=100&before_id=%s' %
                (self._gid, before))
            if resp == None:
                return
            msgs = resp['messages']
            count = int(resp['count'])
            for m in msgs:
                yield Message(m)

    def postMessage(self, msg, guid):
        data = json.dumps({'message': {'text': msg, 'source_guid': guid,
            "attachments": []}})
        api._connect('/v3/groups/%s/messages' % self.id, 'POST',
                data, {'content-type': 'application/json'})

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name + ' (' + self.id + ')'

    def __repr__(self):
        return self.__str__()

class Bot:
    def __init__(self, data):
        self._headers = {'User-Agent': 'gmapi-bot', 'Accept': '*/*',
                'content-type': 'application/json'}
        self._conn = http.client.HTTPSConnection('api.groupme.com')
        self._id = data['bot_id']
        if 'group_id' in data:
            self._group = api._groups[data['group_id']]
        else:
            self._group = None
        self._name = data['name']
        self._callback_url = data['callback_url']
        self._dm_notifs = data['dm_notification']
    
    @property
    def id(self):
        return self._id

    @property
    def group(self):
        return self._group

    @property
    def name(self):
        return self._name

    @property
    def callback_url(self):
        return self._callback_url

    @property
    def dm_notifications(self):
        return self._dm_notifs

    def postMessage(self, msg):
        data = json.dumps({'bot_id': self.id, 'text': msg})
        self._conn.request('POST', '/v3/bots/post', data, self._headers)
        self._conn.close()

    def __str__(self):
        return self.name + ' (' + self.id + ')'

    def __repr__(self):
        return self.__str__()

class User:
    #TODO: load individual user from user page
    def __init__(self, uid, name):
        self._uid = uid
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def __str__(self):
        return self.name + ' (' + self.id + ')'

    def __repr__(self):
        return self.__str__()

class Message:
    def __init__(self, msg):
        self._created_at = datetime.utcfromtimestamp(msg['created_at'])
        self._group = api._groups[msg['group_id']]
        self._id = msg['id']
        self._name = msg['name']
        self._sender = api._get_user(msg['sender_id'], msg['name'])
        self._source_guid = msg['source_guid']
        self._system = msg['system']
        self._text = msg['text']
        self._user = api._get_user(msg['user_id'], msg['name'])

    #TODO: attachments, avatar_url, event, favorited_by

    @property
    def created_at(self):
        return self._created_at

    @property
    def group(self):
        return self._group

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def sender(self):
        return self._sender

    @property
    def source_guid(self):
        return self._source_guid

    @property
    def system(self):
        return self._systtem

    @property
    def text(self):
        return self._text

    @property
    def user(self):
        return self._user


api = _GroupmeAPI()


