## Python SDK For Sina Weiyouxi


usage

```python
from WeiyouClient import WeiyouClient 

try:
    w = WeiyouClient(source, secret, params)
except Exception, e:
    print e
else:
    user_info = w.get('user/show', {'uid': 123456789})
    print user_info


# source: your app key
# secret: your app secret
# params: HTTP GET parameters
```
