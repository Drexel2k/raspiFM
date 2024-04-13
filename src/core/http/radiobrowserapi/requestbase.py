import socket
from urllib import request
import random
from core.json.JsonSerializer import JsonSerializer

version:str

def get_random_radiobrowser_base_url() -> str:
    hosts = []
    # get all hosts from DNS
    ips = socket.getaddrinfo("all.api.radio-browser.info",
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
    servers = list(map(lambda x: "https://" + x, hosts))
    random.shuffle(servers)
    return servers[0]

def get_radiobrowser_post_request_data(endpoint:str, params:dict) -> bytes:
    paramsencoded = None
    if not params is None:
        paramsencoded = JsonSerializer().serialize_restparams(params)

    req = request.Request(get_random_radiobrowser_base_url() + endpoint, paramsencoded)

    req.add_header("User-Agent", f'raspiFM/{version}')
    req.add_header("Content-Type", "application/json")
    response = request.urlopen(req)
    data = response.read()

    response.close()
    return data

def radiobrowser_get_request(endpoint:str, params:dict):
    if not params is None:
        paramsencoded = "/".join(key + "/" + value for key, value in params.items())

    str = get_random_radiobrowser_base_url() + endpoint + "/" + paramsencoded
    try:
        req = request.Request(get_random_radiobrowser_base_url() + endpoint + "/" + paramsencoded)

        req.add_header("User-Agent", "raspiFM/0.5.0")
        req.add_header("Content-Type", "application/json")
        response = request.urlopen(req)
        #data = response.read()
        response.close()
    except BaseException as e:
        pass #if lick fails don't care.

