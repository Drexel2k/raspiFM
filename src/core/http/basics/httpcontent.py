from urllib import request
from base64 import b64encode

def get_urlbinary_content(url:str) -> bytes:
    try:
        req = request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
        with request.urlopen(req) as response:
            return response.read()
    except BaseException as e:
        pass #if server refuses request becaus we are a bot, just do nothing, we can live without picture.

def get_urlbinary_contentasb64(url:str) -> str:
    try:
        req = request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
        with request.urlopen(req) as response:
            return b64encode(response.read()).decode("ASCII")
    except BaseException as e:
        pass #if server refuses request becaus we are a bot, just do nothing, we can live without picture.