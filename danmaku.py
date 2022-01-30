import requests
import re

import crc2uid


def vid2cid(videoid):
    url = "http://api.bilibili.com/x/player/pagelist"
    if videoid[:2].lower() == "av":
        vtype = "aid"
        videoid = int(videoid[2:])
    elif videoid[:2] == "BV":
        vtype = "bvid"
    else:
        print("请输入正确的av/bv号")
        raise Exception("aid or bvid ERROR!")
    params = {
        vtype: videoid
    }
    info = requests.get(url,params=params).json()
    if not info["code"] == 0:
        print("视频信息获取失败")
        raise Exception(info["message"])
    return [cid["cid"]  for cid in info["data"]]


def danmaku_info(cid):
    url = "http://api.bilibili.com/x/v1/dm/list.so"
    xml = requests.get(url,params={"oid":cid})
    xml.encoding = "utf-8"
    data_info = re.findall(r'<d p="(.+?)">.+?</d>',xml.text)
    data_text = re.findall(r'<d p=".+?">(.+?)</d>',xml.text)
    dataName = ["time", "type", "size", "RGB", "sendtime", "pooltype", "midHASH", "dmid"]
    data = []
    for i in range(len(data_info)):
        a = data_info[i].split(",")
        data_p = {}
        data_p["text"] = data_text[i]
        a.pop()
        for j in range(len(a)):
            data_p[dataName[j]] = a[j]
        data.append(data_p)
    return data
    
def getuid(crc):
    return crc2uid.getuid(crc)
            