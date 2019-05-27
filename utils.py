import random, requests, threading
from config import cfg


def random_timeout():
    return random.randrange(cfg.LOW_TIMEOUT, cfg.HIGH_TIMEOUT) / 1000


def spawn_thread(target, args):
    t = threading.Thread(target=target, args=(args, ))
    t.start()
    return t


def send(addr, route, message):
    # TODO: decide for slash in address or not
    url = addr + '/' + route
    print()
    print(url)
    print(message)
    print(type(message))
    print()
    requests.post(
        url=url,
        json=message,
        # timeout=cfg.REQUESTS_TIMEOUT,
    )
    # requests.post(url=url, json=message)


if __name__ == "__main__":
    pass