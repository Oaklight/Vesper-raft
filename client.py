import sys, json, requests

IP = "http://127.0.0.1"


def put(addr, key, value):
    server_address = addr + "/value"
    print(server_address)
    payload = {'key': key, 'value': value}
    message = {"type": "put", "payload": payload}
    # print(f"Sending: {message}")
    while True:
        print(server_address, message)
        response = requests.put(server_address, json=message)
        # print(response.json())
        if response.status_code == 200 and "payload" in response.json():
            payload = response.json()["payload"]
            if "message" in payload:
                print("get message", payload["message"])
                server_address = payload["message"] + "/value"
            else:
                print(response)
                break
        else:
            break


def get(addr, key):
    server_address = addr + "/value"
    print(server_address)
    payload = {'key': key}
    message = {"type": "get", "payload": payload}
    print(f"Sending: {message}")

    while True:
        response = requests.get(server_address, json=message)
        if response.status_code == 200 and "payload" in response.json():
            payload = response.json()["payload"]
            if "message" in payload:
                print("get message", payload["message"])
                server_address = payload["message"] + "/value"
            else:
                print(response.json())
                break
        else:
            break


def old_get(addr, key):
    server_address = addr + "/value"
    print(server_address)
    payload = {'key': key}
    message = {"type": "get", "payload": payload}
    print(f"Sending: {message}")
    response = requests.get(server_address, json=message)
    if response.status_code == 200:
        print(response.json())


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