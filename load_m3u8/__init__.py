# _*_coding:utf-8_*_

import traceback

import requests
import os
from urllib.parse import urljoin

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
headers = {'User-Agent': user_agent}

failed_ts = []


def load_ts_done(feature):
    if feature.exception() is not None:
        print('load_ts_exception: ', feature.exception())
    else:
        msg, result, index, exp = feature.result()
        if not result:
            print('load_ts failed: ', msg)



def load_ts(data):
    index, url, encryptKey, ts_name = data
    try:
        print("fetch", url, ts_name)
        if os.path.exists(ts_name):
            print("exists", ts_name)
            return
        res = requests.get(url, headers=headers, timeout=(30,300))
        if res is None or res.content is None:
            return 'exception end'
        with open(ts_name+".tmp", 'wb') as fp:
            if encryptKey is None:
                fp.write(res.content)
            else:
                aesKey = encryptKey
                fp.write(decrypt(res.content, aesKey))
        os.rename(ts_name+".tmp", ts_name)
    except Exception as e:
        print(traceback.format_exc())
        failed_ts.append(data)
        return f'{ts_name} exception: {str(e)}', False, index, e
    return f'{ts_name} succeed', True, index, None


def decrypt(content, key):
    '''
    M3U8 has the same AES-IV and key
    :param content: Encrypted content
    :param key: AES key
    :param iv: IV vector (Ignore)
    :return: Decrypt content
    '''
    try:
        from Crypto.Cipher import AES
        cryptos = AES.new(key, AES.MODE_CBC, key)
        return cryptos.decrypt(content)
    except Exception as e:
        print('Decryption failed: ', traceback.format_exc())
        return content

def load_key(encryptKey, base_uri):
    if encryptKey is None:
        return None
    print("download", urljoin(base_uri, encryptKey.uri))
    aesKey = requests.get(urljoin(base_uri, encryptKey.uri)).content
    return aesKey
