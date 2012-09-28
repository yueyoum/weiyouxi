from WeiyouxiClient import WeiyouxiClient

source = 'XXXXX'        # your app source
secret = 'XXXXX'        # your app secret

# params are get from HTTP GET parameters
params = {
    'wyx_user_id': 'XXXXX',
    'wyx_session_key': 'XXXXX',
    'wyx_create': 'XXXXX',
    'wyx_expire': 'XXXXX',
    'wyx_signature': 'XXXXX',
}

def display_dict(d):
    if not isinstance(d, dict):
        print d
        return
    
    _d = zip(d.keys(), d.values())
    _d.sort(key=lambda a: a[0])
    for i in _d:
        print '%s : %s' % (i[0], i[1])


w = WeiyouxiClient(source, secret, params)

print w.userId
display_dict(w.session)

display_dict(w.get('user/show'))
print w.httpCode

x = w.get('user/show_batch', {'uids': '2173672264L, 2168043424L, 1146143517'})
display_dict(x)

x = w.get('user/are_friends', {'uid1': '2168043424L', 'uid2': '2173672264L'})
display_dict(x)

display_dict(w.get('application/rate_limit_status'))
#x = w.get('tags/tags_batch', {'uids': '2168043424L,2173672264L'})
#display_dict(x)

print 'Done'
