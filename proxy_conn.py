import socket
from urllib.parse import urlparse
from HttpRequest import HttpRequest
import os
from dotenv import load_dotenv
load_dotenv()

BUFF_SIZE = int(os.getenv('BUFF_SIZE'))

def get_destination_data(req):
    # Extract destination
    target_url = req.request_path()        
    parsed_url = urlparse(target_url)

    if (parsed_url.scheme != "http"):
        raise Exception("WHAT?")

    if ":" in parsed_url.netloc:            
        target_host, target_port = parsed_url.netloc.split(":")
        target_port = int(target_port)
    else:
        target_host = parsed_url.netloc
        target_port = 80

    return [target_host, target_port]

def proxy_connection(client_sock, addr):
    print(f"+ new connection {client_sock} from {addr}")
    
    client_sock.settimeout(1)

    http_requests = HttpRequest.from_sock(client_sock)
    for req in http_requests:
        print(req)
        target_host, target_port = get_destination_data(req)
        print(f"opening connection to {target_host}:{target_port}")

        sock = socket.socket()        
        sock.connect((socket.gethostbyname(target_host), target_port))
        sock.sendall(req.raw_bytes())        
        sock.settimeout(1)

        recv_data = b''
        while True:
            try:
                data_chunk = sock.recv(BUFF_SIZE)            
                recv_data += data_chunk
            except TimeoutError:
                break

        sock.close()
        client_sock.sendall(recv_data)

        print(recv_data)

    client_sock.close()
    
  