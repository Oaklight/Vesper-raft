import random
from config import cfg


def get_timeout():
    return random.randrange(cfg.LOW_TIMEOUT, cfg.HIGH_TIMEOUT)


def create_url(route, attributes=None):
    # given attributes it create a url route
    # some_route?input_file=file.txt&size=30
    url = route + "?"
    div = "&"
    for key, value in attributes.keys():
        url += f"{key}={str(value)}{div}"
    return url[:-1]


# request.remote_addr
if __name__ == "__main__":
    att = {"term": 10, "ip": "127.0.0.1"}
    url = create_url("vote", att)
    print(url)
