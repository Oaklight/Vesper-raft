import sys, json, requests

IP = "http://127.0.0.1"

def send_key_value(port,key,value):
    server_address = IP + ':' + port + "/put"
    print (server_address)
    packet = {
        'key':key,
        'value':value
    }
    print(f"Sending: {packet}")
    response = requests.post(server_address, json=packet)
    print (response)

def get(port,key):
    server_address = IP + ':' + port + "/get"
    print (server_address)
    packet = {
        'key':key,
    }
    print(f"Sending: {packet}")
    response = requests.get(server_address, json=packet)
    if response.status_code == 200:
        print (response.json())
    else:
        print(f"{key} not found")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        # normal mode
        ports = [port for port in sys.argv[1].split('-')]
        key = sys.argv[2]
        value = sys.argv[3]
        send_key_value(ports[0],key,value)
        key = "aaaaa"
        get(ports[0],key)

    else:
        print("normal usage: python3 client.py <port0-port1-..> 'key' 'value'")