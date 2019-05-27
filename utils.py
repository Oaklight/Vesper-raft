import random, requests, threading
from config import cfg


def random_timeout():
    return random.randrange(cfg.LOW_TIMEOUT, cfg.HIGH_TIMEOUT) / 1000


def spawn_thread(follower):
    t = threading.Thread(heartbeat, (follower, ))
    t.start()
    return t


def send(addr, route, message=None):
    # TODO: decide for slash in address or not
    url = addr + route
    requests.get(
        url=url,
        params=message,
        timeout=cfg.REQUESTS_TIMEOUT,
    )
    # requests.post(url=url, json=message)


if __name__ == "__main__":
    print(get_timeout())
