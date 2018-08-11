try:
    from settings import APIKEY, GROUPID
except:
    raise Exception("YOU NEED TO ADD `app/settings.py` FILE. CHECK README.md")

from api import VK_API

VK = VK_API( token = APIKEY )

import auth

if __name__ == '__main__':
    # START
    print('STARTING...')