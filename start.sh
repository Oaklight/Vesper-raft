# start all servers in background. 
# ensure ips.txt has the correct number of address, with "http://" prefix

python Vesper/vesper_server.py 0 Vesper/ips.txt
python Vesper/vesper_server.py 1 Vesper/ips.txt
python Vesper/vesper_server.py 2 Vesper/ips.txt