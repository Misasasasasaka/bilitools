from sys import argv
from bilibili_api import sync,user,dynamic,Credential
import requests
import qrcode
import time


def print_qr(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.print_ascii(invert=True)


def login():
    qr_url = 'http://passport.bilibili.com/qrcode/getLoginUrl'
    qr = requests.get(qr_url).json()
    print_qr(qr['data']['url'])
    print('等待扫描二维码')
    params = {'oauthKey':qr['data']['oauthKey']}
    post_url = 'http://passport.bilibili.com/qrcode/getLoginInfo'

    for i in range(180):
        login_info = requests.post(post_url,data=params)
        if login_info.json()['status'] == True:
            print('登录成功')
            cookies = login_info
            break
        time.sleep(1)
    return cookies
        

def get_dy(uid, credential):
    u = user.User(int(uid),credential=credential)

    dy_list = []
    i = 0
    while True:
        while True:
            try:
                info = sync(u.get_dynamics(offset=i))
                break
            except:
                pass
        if info['has_more'] == 0:
            print('动态获取完毕')
            break
        for i in info['cards']:
            dy_list.append(i['desc']['dynamic_id_str'])
        i = info['next_offset']
    return dy_list
    

def make_cre(cookies):
    return Credential(sessdata=cookies.get('SESSDATA'),bili_jct=cookies.get('bili_jct'))


def like(dy_id,credential):
    dy = dynamic.Dynamic(dynamic_id=int(dy_id),credential=credential)
    sync(dy.set_like(status=True))
    print(f'{dy_id}已点赞')


if __name__ == '__main__':

    _, uid = argv
    cookies = login()
    cre = make_cre(cookies.cookies)
    L = get_dy(uid,cre)
    for i in L:
        while True:
            try:
                like(i,cre)
                break
            except:
                print('操作太过频繁!')
