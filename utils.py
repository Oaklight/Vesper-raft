import random
from config import cfg


def get_timeout():
    return random.randrange(cfg.LOW_TIMEOUT, cfg.HIGH_TIMEOUT)


if __name__ == "__main__":
    print(get_timeout())
