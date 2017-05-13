# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import os
import time
import json
import requests
from requests_oauthlib import OAuth1

__all__ = ["monitor"]


# Twitter API settings.
e = os.environ
url = "https://stream.twitter.com/1.1/statuses/sample.json"
client_key = e["TW_CLIENT_KEY"]
client_secret = e["TW_CLIENT_SECRET"]
user_key = e["TW_USER_KEY"]
user_secret = e["TW_USER_SECRET"]


def monitor():
    wait = 0
    auth = OAuth1(client_key, client_secret, user_key, user_secret)
    while 1:
        try:
            try:
                r = requests.get(url, auth=auth, stream=True, timeout=90)

            except requests.exceptions.ConnectionError:
                print("request failed.")
                wait = min(wait + 0.25, 16)

            else:
                code = r.status_code
                print("{0} returned: {1}".format(url, code))
                if code == 200:
                    wait = 0
                    try:
                        for line in r.iter_lines():
                            if line:
                                yield json.loads(line.decode("utf-8"))

                    except requests.exceptions.Timeout:
                        print("request timed out.")

                    except Exception as e:
                        print("failed with: {0}".format(e))

                elif code == 420:
                    if wait == 0:
                        wait = 60

                    else:
                        wait *= 2

                elif code in [401, 403, 404, 500]:
                    if wait == 0:
                        wait = 5

                    else:
                        wait = min(wait * 2, 320)

                else:
                    r.raise_for_status()

        except KeyboardInterrupt:
            print("Exiting.")
            break

        time.sleep(wait)


if __name__ == "__main__":
    for o in monitor():
        print(o)
        break
