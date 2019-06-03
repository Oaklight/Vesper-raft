import random
import requests
from config import cfg


def random_timeout():
    return random.randrange(cfg.LOW_TIMEOUT, cfg.HIGH_TIMEOUT) / 1000


def send(addr, route, message):
    url = addr + '/' + route
    try:
        reply = requests.post(
            url=url,
            json=message,
            timeout=cfg.REQUESTS_TIMEOUT / 1000,
        )
    # failed to send request
    except Exception as e:
        # print(e)
        return None

    if reply.status_code == 200:
        return reply
    else:
        return None
