import socket
import sys
import threading
from proxy_conn import proxy_connection
import os
from dotenv import load_dotenv
load_dotenv()

LISTENING_PORT  = int(os.getenv('LISTENING_PORT'))
BACKLOG         = int(os.getenv('BACKLOG'))


def main():

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', LISTENING_PORT))
        s.listen(BACKLOG)
        print("[*] Server started successfully [{}]" .format(LISTENING_PORT))
    except Exception as e:
        print(e)
        sys.exit(2)

    while True:
        try:
            client_sock, addr = s.accept()            
            threading.Thread(target=proxy_connection, args=(client_sock, addr)).start()
        except KeyboardInterrupt:        
            print("\n[*] Shutting down...")                    
            s.close()
            sys.exit(1)

    
if __name__ == "__main__":
    main()