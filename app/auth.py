from __main__ import VK

# STARTING
print('AUTH')

# AUTH
USER = VK.account.getProfileInfo()
if USER.get('response'):
    print('hello, %s %s' % (USER['response']['first_name'], USER['response']['last_name']))
elif USER.get('error'):
    raise Exception(USER['error']['error_msg'])