import socket
from urllib import request
import random
from base64 import b64encode
from ..json.JsonSerializer import JsonSerializer

def get_radiobrowser_base_urls():
    hosts = []
    # get all hosts from DNS
    ips = socket.getaddrinfo('all.api.radio-browser.info',
                             80, 0, 0, socket.IPPROTO_TCP)
    for ip_tupple in ips:
        ip = ip_tupple[4][0]

        # do a reverse lookup on every one of the ips to have a nice name for it
        host_addr = socket.gethostbyaddr(ip)
        # add the name to a list if not already in there
        if host_addr[0] not in hosts:
            hosts.append(host_addr[0])

    # sort list of names
    hosts.sort()
    # add "https://" in front to make it an url
    return list(map(lambda x: "https://" + x, hosts))

def do_radiobrowser_post_request_get_data(uri, params) -> bytes:
    paramsEncoded = None
    if params:
        paramsEncoded = JsonSerializer().serialize_restparams(params)

    req = request.Request(uri, paramsEncoded)

    req.add_header('User-Agent', 'raspiFM/0.0.1')
    req.add_header('Content-Type', 'application/json')
    response = request.urlopen(req)
    data = response.read()

    response.close()
    return data

def get_radiobrowser_post_request_data(endpoint: str, param: dict) -> bytes:
    servers = get_radiobrowser_base_urls()
    random.shuffle(servers)

    for server_base in servers:
        uri = server_base + endpoint
        return do_radiobrowser_post_request_get_data(uri, param)
    
    return b""

def get_urlbinary_contentasb64(url:str) -> str:
    try:
        req = request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
        with request.urlopen(req) as response:
            return b64encode(response.read()).decode("ASCII")
    except BaseException as e:
        pass #if server refuses request becaus we are a bot, just do nothing, we can live without picture.
    
