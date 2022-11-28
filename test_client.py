import requests


http_proxy  = "http://127.0.0.1:31337"
https_proxy = "https://127.0.0.1:31337"
ftp_proxy   = "ftp://127.0.0.1:31337"

proxies = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }

target_url = "http://eu.httpbin.org/"

# r = requests.post(target_url, proxies=proxies, data={"anda":"hola"})
r = requests.get(target_url, proxies=proxies)
print(r.text)

