import requests

class VK_API:
    def __init__(self, *args, **kwargs):
        self.token = kwargs.get('token')
        self.method = ''
    
    def API(self, *args, **kwargs):
        """ VK API REQUEST """
        METHOD = self.method; self.method = ''
        PARAMS = "&".join([ '%s=%s' % (i, kwargs.get(i)) for i in kwargs])
        URL = 'https://api.vk.com/method/%s?%s&access_token=%s&v=5.60' % (METHOD, PARAMS, self.token)
        r = requests.get(URL)
        return r.json()

    def __getattribute__(self, attr, *args, **kwargs):
        if attr in ('account',):
            self.method = attr
            return self
        else:
            try:
                return super().__getattribute__(attr, *args, **kwargs)
            except:
                self.method = '%s.%s' % (self.method, attr) if self.method else attr
                return self.API