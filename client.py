import sys, json, requests

IP = "http://127.0.0.1"


def put(addr, key, value):
    server_address = addr + "/value"
    print(server_address)
    payload = {'key': key, 'value': value}
    message = {"type": "put", "payload": payload}
    print(f"Sending: {message}")
    response = requests.put(server_address, json=message)
    print(response)


def get(addr, key):
    server_address = addr + "/value"
    print(server_address)
    payload = {'key': key}
    message = {"type": "get", "payload": payload}
    print(f"Sending: {message}")
    response = requests.get(server_address, json=message)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"{key} not found")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        # addr, key
        # get
        addr = sys.argv[1]
        key = sys.argv[2]
        get(addr, key)

    if len(sys.argv) == 4:
        # addr, key value
        # put
        addr = sys.argv[1]
        key = sys.argv[2]
        val = sys.argv[3]
        put(addr, key, val)
    # else:
    #     print("normal usage: python3 client.py <port0-port1-..> 'key' 'value'")