import socket
from urllib.parse import urlparse
from http_request import HttpRequest
import os
from dotenv import load_dotenv
load_dotenv()

BUFF_SIZE = int(os.getenv('BUFF_SIZE'))
MODE = os.getenv('MODE')

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
    print(f"[+] New connection {client_sock} from {addr}")
    
    client_sock.settimeout(2)

    http_requests = HttpRequest.from_sock(client_sock)
    for req in http_requests:
        print(req.get_data(MODE))
        target_host, target_port = get_destination_data(req)
        print(f"\n[i] Opening connection to {target_host}:{target_port}\n")

        # ------- PUNTO 1 -------
        sock = socket.socket()        
        sock.connect((socket.gethostbyname(target_host), target_port))
        sock.sendall(req.raw_bytes())        
        sock.settimeout(2)
        
        # ------- PUNTO 2 -------
        recv_data = b''
        while True:
            try:
                data_chunk = sock.recv(BUFF_SIZE)            
                recv_data += data_chunk
            except TimeoutError:
                break
        
        client_sock.sendall(recv_data)
        response = HttpRequest(recv_data)
        print(f"[i] Response ---> {response.request_line}")
        print(response.get_data(MODE))
        sock.close()

    client_sock.close()
    
  