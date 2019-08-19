
Skip to content
Pull requests
Issues
Marketplace
Explore
@zstu-lly

2
14

    7

zstu-lly/JD_Robot
Code
Issues 0
Pull requests 0
Projects 0
Wiki
Security
Insights
Settings
JD_Robot/spider.py
Fetching contributors…
559 lines (482 sloc) 20.9 KB
import argparse
import os
import pickle
import random
import sys
import time
import json
import requests
import re
import logging
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

logging.basicConfig(
    format="%(asctime)s - %(threadName)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s",
    level=logging.INFO
)


class JDSpider:

    def __init__(self):

        # init url related
        self.home = 'https://passport.jd.com/new/login.aspx'
        self.login = 'https://passport.jd.com/uc/loginService'
        self.imag = 'https://authcode.jd.com/verify/image'
        self.auth = 'https://passport.jd.com/uc/showAuthCode'

        self.sess = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }

        self.cookies = {

        }

        self.eid = 'DHPVSQRUFPP6GFJ7WPOFDKYQUGQSREWJLJ5QJPDOSJ2BYF55IZHP5XX3K2BKW36H5IU3S4R6GPU7X3YOGRJGW7XCF4'
        self.fp = 'b450f02af7d98727ef061e8806361c67'

    def checkLogin(self):
        # 恢复之前保存的cookie
        checkUrl = 'https://passport.jd.com/uc/qrCodeTicketValidation'
        try:
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(f'{time.ctime()} > 自动登录中... ')
            with open('cookie', 'rb') as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
                response = requests.get(checkUrl, cookies=cookies)
                if response.status_code != requests.codes.OK:
                    print('登录过期, 请重新登录!')
                    return False
                else:
                    print('登录成功!')
                    self.cookies.update(dict(cookies))
                    return True

        except Exception as e:
            logging.error(e)
            return False

    def login_by_QR(self):
        # jd login by QR code
        try:
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(f'{time.ctime()} > 请打开京东手机客户端，准备扫码登录:')
            urls = (
                'https://passport.jd.com/new/login.aspx',
                'https://qr.m.jd.com/show',
                'https://qr.m.jd.com/check',
                'https://passport.jd.com/uc/qrCodeTicketValidation'
            )
            # step 1: open login page
            response = self.sess.get(
                urls[0],
                headers=self.headers
            )
            if response.status_code != requests.codes.OK:
                print(f"获取登录页失败:{response.status_code}")
                return False
            # update cookies
            self.cookies.update(response.cookies)

            # step 2: get QR image
            response = self.sess.get(
                urls[1],
                headers=self.headers,
                cookies=self.cookies,
                params={
                    'appid': 133,
                    'size': 147,
                    't': int(time.time() * 1000),
                }
            )
            if response.status_code != requests.codes.OK:
                print(f"获取二维码失败:{response.status_code}")
                return False

            # update cookies
            self.cookies.update(response.cookies)

            # save QR code
            image_file = 'qr.png'
            with open(image_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

            # scan QR code with phone
            if os.name == "nt":
                # for windows
                os.system('start ' + image_file)
            else:
                if os.uname()[0] == "Linux":
                    # for linux platform
                    os.system("eog " + image_file)
                else:
                    # for Mac platform
                    os.system("open " + image_file)

            # step 3: check scan result    京东上也是不断去发送check请求来判断是否扫码的
            self.headers['Host'] = 'qr.m.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 100    # 尝试100次
            while retry_times:
                retry_times -= 1
                response = self.sess.get(
                    urls[2],
                    headers=self.headers,
                    cookies=self.cookies,
                    params={
                        'callback': 'jQuery%d' % random.randint(1000000, 9999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': int(time.time() * 1000)
                    }
                )
                if response.status_code != requests.codes.OK:
                    continue
                rs = json.loads(re.search(r'{.*?}', response.text, re.S).group())
                if rs['code'] == 200:
                    print(f"{rs['code']} : {rs['ticket']}")
                    qr_ticket = rs['ticket']
                    break
                else:
                    print(f"{rs['code']} : {rs['msg']}")
                    time.sleep(3)

            if not qr_ticket:
                print("二维码登录失败")
                return False

            # step 4: validate scan result
            # must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'
            response = requests.get(
                urls[3],
                headers=self.headers,
                cookies=self.cookies,
                params={'t': qr_ticket},
            )
            if response.status_code != requests.codes.OK:
                print(f"二维码登录校验失败:{response.status_code}")
                return False

            # 京东有时候会认为当前登录有危险，需要手动验证
            # url: https://safe.jd.com/dangerousVerify/index.action?username=...
            res = json.loads(response.text)
            if not response.headers.get('p3p'):
                if 'url' in res:
                    print(f"需要手动安全验证: {res['url']}")
                    return False
                else:
                    print(res)
                    print('登录失败!!')
                    return False

            # login succeed
            self.headers['P3P'] = response.headers.get('P3P')
            self.cookies.update(response.cookies)

            # 保存cookie
            with open('cookie', 'wb') as f:
                pickle.dump(self.cookies, f)

            print("登录成功")
            return True

        except Exception as e:
            print(e)
            raise

    def good_stock(self, skuId, area_id):
        """
        监控库存
        :return:
        """
        url = "https://c0.3.cn/stocks"

        params = {
            "skuIds": skuId,
            "area": area_id,    # 收货地址id
            "type": "getstocks",
            "_": int(time.time()*1000)
        }

        headers = {"Referer": f"https://item.jd.com/{skuId}.html",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/75.0.3770.142 Safari/537.36",
                   }
        try:
            response = requests.get(url, params=params, headers=headers)
            # print(response.text)    # 33: 现货    34: 无货     40: 可配货
            json_dict = json.loads(response.text)
            stock_state = json_dict[skuId]['StockState']
            stock_state_name = json_dict[skuId]['StockStateName']
            return stock_state, stock_state_name
        except Exception as e:
            logging.error(e)

        return 0, ''

    def good_detail(self, skuId, area_id):
        # return good detail
        good_data = {
            'id': skuId,
            'name': '',
            'cart_link': '',
            'price': '',
            'stock': '',
            'stockName': '',
        }
        try:
            # 商品详情页
            detail_link = f"https://item.jd.com/{skuId}.html"
            response = requests.get(detail_link)
            soup = BeautifulSoup(response.text, "lxml")
            # 产品名称
            name = soup.find('div', class_="sku-name").text.strip()
            good_data['name'] = name
            # 购物车链接
            cart_link = soup.find("a", id="InitCartUrl")['href']
            if cart_link[:2] == '//':  # '//cart.jd.com/gate.action?pid=5504364&pcount=1&ptype=1'
                cart_link = 'http:' + cart_link
            good_data['cart_link'] = cart_link

        except Exception as e:
            logging.error(e)

        good_data['price'] = self.good_price(skuId)
        good_data['stock'], good_data['stockName'] = self.good_stock(skuId, area_id)
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f'{time.ctime()} > 商品详情')
        print(f"编号：{good_data['id']}")
        print(f"库存：{good_data['stockName']}")
        print(f"价格：{good_data['price']}")
        print(f"名称：{good_data['name']}")
        print(f"加入购物车链接：{good_data['cart_link']}")
        return good_data

    def good_price(self, skuId):
        # get good price
        url = 'http://p.3.cn/prices/mgets'
        payload = {
            'type': 1,
            'skuIds': 'J_' + skuId,
        }
        price = '?'
        try:
            response = requests.get(url, params=payload)
            resp_txt = response.text.strip()
            json_dict = json.loads(resp_txt[1:-1])  # 去掉首尾的[]
            price = json_dict['p']
        except Exception as e:
            logging.error(e)
        return price

    def buy(self, options):
        # good detail
        good_data = self.good_detail(options.good, options.area)
        if good_data['stock'] != 33:    # 如果没有现货
            # flush stock state
            while good_data['stock'] != 33 and options.flush:
                print(good_data['stock'], good_data['name'])
                time.sleep(options.wait / 1000.0)
                good_data['stock'], good_data['stockName'] = self.good_stock(skuId=options.good,
                                                                             area_id=options.area)

        cart_link = good_data['cart_link']
        if cart_link == '':    # 如果有货, 但是没有购物车链接
            print("没有购物车链接")
            return False

        # 先取消全部 然后再改
        self.cancelAllItem(options.area)
        try:
            # change buy count
            cart_info_dict = self.cart_detail()    # 先获取购物车的信息
            if options.good in cart_info_dict.keys():    # 如果之前添加过购物车了
                self.change_num(options.count,
                                cart_info_dict[options.good]['verderid'],
                                options.good,
                                options.area)

            else:    # 如果没有添加过购物车
                if options.count != 1:
                    cart_link = cart_link.replace('pcount=1', 'pcount={0}'.format(options.count))
                response = self.sess.get(cart_link, cookies=self.cookies)
                soup = BeautifulSoup(response.text, "lxml")
                tag = soup.find("h3", class_='ftx-02')
                if tag:
                    print(tag.text)    # 商品已成功加入购物车！
                else:
                    print('添加到购物车失败')
                    return False

        except Exception as e:
            logging.error(e)
            return False
        else:
            return self.order_info(options.submit)

    def cart_detail(self):
        # get info of cart
        cart_url = 'https://cart.jd.com/cart.action'

        response = self.sess.get(cart_url, cookies=self.cookies)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "lxml")

        cart_info_dict = dict()

        for item in soup.find_all(class_='item-item'):
            skuid = item['skuid']    # 商品sku
            count = int(item['num'])  # 数量
            venderid = item['venderid']    # 商家id
            good_name = item.find('img')['alt']    # 商品名称

            cart_info_dict[skuid] = {'count': count, 'verderid': venderid, 'good_name': good_name}

        return cart_info_dict

    def order_info(self, submit=False):
        """
        下单
        :param submit: 是否提交订单
        :return: 是否下单成功
        """
        # get order info detail, and submit order
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(f'{time.ctime()} > 订单详情')

        try:
            order_url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
            payload = {
                'rid': str(int(time.time() * 1000)),
            }

            # 获取预下单页面
            rs = self.sess.get(order_url, params=payload, cookies=self.cookies)
            soup = BeautifulSoup(rs.text, "lxml")

            # order summary
            payment = soup.find(id='sumPayPriceId').text    # TODO
            detail = soup.find(class_='fc-consignee-info')

            if detail:
                snd_usr = detail.find(id='sendMobile').text    # 收货人
                snd_add = detail.find(id='sendAddr').text      # 收货地址

                print('应付款：{0}'.format(payment))
                print(snd_usr)
                print(snd_add)

            # just test, not real order
            if not submit:
                return False

            # order info
            sopNotPutInvoice = soup.find(id='sopNotPutInvoice')['value']

            btSupport = get_btSupport(soup)
            ignorePriceChange = soup.find(id='ignorePriceChange')['value']
            riskControl = soup.find(id='riskControl')['value']
            jxj = get_jxj(soup)

            data = {
                'overseaPurchaseCookies': '',
                'vendorRemarks': [],    # 貌似是订单备注    [{"venderId":"632952","remark":""}]
                'submitOrderParam.sopNotPutInvoice': sopNotPutInvoice,    # 货票分离开关值  false or true
                'submitOrderParam.trackID': 'TestTrackId',    # 写死
                'submitOrderParam.get_ignorePriceChange': ignorePriceChange,
                'submitOrderParam.btSupport': btSupport,    # 是否支持白条
                'submitOrderParam.eid': self.eid,    # 设备id
                'submitOrderParam.fp': self.fp,      # ?
                'riskControl': riskControl,
                'submitOrderParam.jxj': jxj,
                'submitOrderParam.trackId': 'cc46bf84f6274988c7cde62fce0cc11a',
            }
            # print(data)
            order_url = 'http://trade.jd.com/shopping/order/submitOrder.action'
            rp = self.sess.post(order_url, data=data, cookies=self.cookies, headers={
                'Referer': 'https://trade.jd.com/shopping/order/getOrderInfo.action?rid='+payload['rid'],
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            })
            print(rp.text)

            if rp.status_code == 200:
                js = json.loads(rp.text)
                if js['success']:
                    print('下单成功！订单号：{0}'.format(js['orderId']))
                    print('请前往京东官方商城付款')
                    # send_email('下单成功', f'应付款：{payment}, 请前往京东官方商城付款')
                    return True
                else:
                    print('下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                    if js['resultCode'] == '60017':
                        # 60017: 您多次提交过快，请稍后再试
                        time.sleep(1)
            else:
                print('请求失败. StatusCode:', rp.status_code)

        except Exception as e:
            logging.error(e)

        return False

    # 改变购物车商品的数量
    def change_num(self, num, venderId, pid, locationId):
        """
        :param num: 目标数量
        :param venderId: 商家id
        :param pid: 商品id
        :param locationId: 收货地址id
        :return:
        """

        url = "https://cart.jd.com/changeNum.action"
        data = {
            't': 0,
            'venderId': venderId,
            'pid': pid,
            'pcount': num,
            'ptype': '1',
            'targetId':    '0',
            'promoID':    '0',
            'outSkus': '',
                'random':    random.random(),
                'locationId':   locationId,
        }
        res = self.sess.post(url, data=data, cookies=self.cookies)
        assert res.status_code == 200

    def cancelAllItem(self, locationId):
        url = "https://cart.jd.com/cancelAllItem.action"
        data = {
            't': 0,
            'outSkus': '',
            'random': random.random(),
            'locationId': locationId,
        }
        res = self.sess.post(url, data=data, cookies=self.cookies)
        assert res.status_code == 200


def get_btSupport(soup):
    if len(soup.find_all(class_='payment-item', attrs={'onlinepaytype': '1'})) == 0:
        if "payment-item-disabled" in str(soup.find_all(class_='payment-item', attrs={'onlinepaytype': '1'})):
            return '0'
    else:
        return '1'


def get_jxj(soup):
    # //惊喜金 我也不知道是个啥玩意
    return '1'


def send_email(subject, message):
    try:
        my_sender = ''  # 邮件发送者
        my_pass = ''  # 邮件发送者邮箱密码
        my_user = ''
        msg = MIMEText(message, 'html', 'utf-8')
        msg['From'] = formataddr(["来自京东自动下单机器人", my_sender])
        msg['To'] = formataddr(["由我的网易邮箱接收", my_user])
        msg['Subject'] = subject

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(my_sender, my_pass)
        server.sendmail(my_sender, [my_user, ], msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(e)
        try:
            my_sender = ''  # 邮件发送者
            my_pass = ''  # 邮件发送者邮箱密码
            my_user = ''
            msg = MIMEText(message, 'html', 'utf-8')
            msg['From'] = formataddr(["来自京东自动下单机器人", my_sender])
            msg['To'] = formataddr(["由我的网易邮箱接收", my_user])
            msg['Subject'] = subject

            server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            server.login(my_sender, my_pass)
            server.sendmail(my_sender, [my_user, ], msg.as_string())
            server.quit()
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':

    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and buy sepecified good')
    parser.add_argument('-a', '--area',
                        help='Area string, like: 1_72_2799_0 for Beijing', default='')
    parser.add_argument('-g', '--good',
                        help='Jing Dong good ID', default='')
    parser.add_argument('-c', '--count', type=int,
                        help='The count to buy', default=1)
    parser.add_argument('-w', '--wait',
                        type=int, default=1000,
                        help='Flush time interval, unit MS')
    parser.add_argument('-f', '--flush',
                        action='store_true',
                        help='Continue flash if good out of stock',
                        default=True)
    parser.add_argument('-s', '--submit',
                        action='store_true',
                        help='Submit the order to Jing Dong',
                        default=True)

    options = parser.parse_args()
    # for test
    options.count = 3
    options.good = '49272463149'
    options.area = '15_1290_22049_22142'

    spider = JDSpider()
    if not spider.checkLogin():
        if not spider.login_by_QR():
            sys.exit(-1)

    while not spider.buy(options) and options.flush:
        time.sleep(options.wait / 1000.0)

    © 2019 GitHub, Inc.
    Terms
    Privacy
    Security
    Status
    Help

    Contact GitHub
    Pricing
    API
    Training
    Blog
    About

