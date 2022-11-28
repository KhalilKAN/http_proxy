from urllib.parse import urlparse
import os
from dotenv import load_dotenv
from payload import payload_header
load_dotenv()

BUFF_SIZE = int(os.getenv('BUFF_SIZE'))



class HttpRequest:

    """
    The constructor expects that the argument data is valid HTTP
    Headers are determined by "\r\n\r\n"
    Transfer-Encoding: chunked is not supported yet
    """
    def __init__(self, data):        
        self.request_line  = None 
        self.headers       = {}   
        self.body          = None
        
        # split headers from body
        sep = data.index(b'\r\n\r\n')

        headers_blob      = data[0:sep].decode('utf-8')       
        headers           = headers_blob.split("\r\n")
        self.request_line = headers.pop(0)
        self.get_headers_format(headers, False)
        self.get_headers_format(payload_header, True)

        # process body
        index_body_end = self.get_body_length(data[sep+4:])
        self.body = data[sep+4:][:index_body_end] 

        if index_body_end is None:
            self.raw_data      = data[0 : sep+4]    
        else:
            self.raw_data      = data[0 : sep+4+index_body_end] 


    def get_headers_format(self, array, payload):
        for header in array:
            k, v = header.split(": ") if payload else header.split(": ", 1)
            self.headers[k.title()] = v

    def get_headers(self):
        data = ""        
        for k, v in self.headers.items():
            data += "{}: {}\r\n".format(k, v)
        return data
    
    def get_body(self):
        return self.body.decode("utf-8")

    def get_all(self):
        return self.raw_data.decode("utf-8")

    def get_data(self, mode):
        functions = {
            "headers": self.get_headers(),
            "body": self.get_body(),
            "all": self.get_all()
        }

        return functions[mode]

    def request_method(self):
        return self.request_line.split(" ")[0]

    
    def request_path(self):        
        return self.request_line.split(" ")[1]

    #This function return body content length
    def get_body_length(self, data):
        if len(data) == 0:
            return None
        
        req_method = self.request_method()

        if req_method == "GET" or req_method == "HEAD":
            raise Exception("a GET method shouldn't contain data?")

        content_length = self.headers.get("Content-Length", None)
        if content_length is None:
            raise Exception("Transfer Encoding: chunked maybe?")
        
        content_length = int(content_length)
     
        return content_length


    def __len__(self):
        return len(self.raw_data)


    def __str__(self):
        return self.raw_data.decode('utf-8')

    
    def reformat_request_line(self):
        method, target_url, version  = self.request_line.split(" ")        

        parsed_url = urlparse(target_url)
        path       = parsed_url.path + parsed_url.params + parsed_url.query

        res = "{} {} {}".format(method, path, version)
        return res

    def raw_bytes(self):
        data = b""
        
        ## Add req line
        req_line = self.reformat_request_line().encode('utf-8')
        data += req_line + b'\r\n'
        
        ## add headers
        for i, value in enumerate(self.headers.items()):
            if(i == len(self.headers)-1):
                h = "{}: {}".format(value[0], value[1])
            else:
                h = "{}: {}\r\n".format(value[0], value[1])
            data += h.encode('utf-8')

        data += b'\r\n\r\n'

        if self.body:
            data += self.body

        return data



    @classmethod
    def from_sock(cls, sock): #Returns all the requests that arrived        
        data = None
        data_chunk = sock.recv(BUFF_SIZE)
        if len(data_chunk) > 0:
            data = data_chunk
        else:
            raise Exception("No data from client sock?")

        while True:
            try:
                data_chunk = sock.recv(BUFF_SIZE)            
                data += data_chunk
            except:
                break

        result = []
        
        parsed_data = 0
        j = 1
        while parsed_data < len(data):            
            instance = HttpRequest(data[parsed_data:])
            result.append(instance) # add to the result set
            parsed_data += len(instance)
            print(f"\n[i] Parsed {j} requests from data\n")
            print(f"[i] Request ---> {instance.request_line}")
            j += 1
        
        return result
