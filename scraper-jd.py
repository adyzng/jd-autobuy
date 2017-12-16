# -*- coding: utf-8 -*-

"""
JD online shopping helper tool
-----------------------------------------------------

only support to login by QR code,
username / password is not working now.

"""


import argparse
import json
import os
import random
import sys
import time

import bs4
import requests
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()


# from selenium import webdriver


# reload(sys)
# sys.setdefaultencoding('utf-8')

# get function name
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name


def tags_val(tag, key='', index=0):
    '''
    return html tag list attribute @key @index
    if @key is empty, return tag content
    '''
    if len(tag) == 0 or len(tag) <= index:
        return ''
    elif key:
        txt = tag[index].get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag[index].text
        return txt.strip(' \t\r\n') if txt else ''


def tag_val(tag, key=''):
    '''
    return html tag attribute @key
    if @key is empty, return tag content
    '''
    if tag is None:
        return ''
    elif key:
        txt = tag.get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag.text
        return txt.strip(' \t\r\n') if txt else ''


class JDWrapper(object):
    '''
    This class used to simulate login JD
    '''

    def __init__(self, usr_name=None, usr_pwd=None):
        # cookie info
        self.trackid = ''
        self.uuid = ''
        self.eid = ''
        self.fp = ''

        self.usr_name = usr_name
        self.usr_pwd = usr_pwd

        self.interval = 0

        # init url related
        self.home = 'https://passport.jd.com/new/login.aspx'
        self.login = 'https://passport.jd.com/uc/loginService'
        self.imag = 'https://authcode.jd.com/verify/image'
        self.auth = 'https://passport.jd.com/uc/showAuthCode'

        self.sess = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }

        self.cookies = {

        }

        '''
        try:
            self.browser = webdriver.PhantomJS('phantomjs.exe')
        except Exception, e:
            print 'Phantomjs initialize failed :', e
            exit(1)
        '''

    @staticmethod
    def print_json(resp_text):
        '''
        format the response content
        '''
        if resp_text[0] == '(':
            resp_text = resp_text[1:-1]

        for k, v in json.loads(resp_text).items():
            print('{} : {}'.format(k, v))

    @staticmethod
    def response_status(resp):
        if resp.status_code != requests.codes.OK:
            print('Status: {}, Url: {}'.format(resp.status_code, resp.url))
            return False
        return True

    def _need_auth_code(self, usr_name):
        # check if need auth code
        #
        auth_dat = {
            'loginName': usr_name,
        }
        payload = {
            'r': random.random(),
            'version': 2015
        }

        resp = self.sess.post(self.auth, data=auth_dat, params=payload)
        if self.response_status(resp):
            js = json.loads(resp.text[1:-1])
            return js['verifycode']

        print('获取是否需要验证码失败')
        return False

    def _get_auth_code(self, uuid):
        # image save path
        image_file = os.path.join(os.getcwd(), 'authcode.jfif')  # '/Users/blm/authcode.jfif'

        payload = {
            'a': 1,
            'acid': uuid,
            'uid': uuid,
            'yys': str(int(time.time() * 1000)),
        }

        # get auth code
        r = self.sess.get(self.imag, params=payload)
        if not self.response_status(r):
            print('获取验证码失败')
            return False

        with open(image_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

            f.close()

        os.system('start ' + image_file)
        return str(input('Auth Code: '))

    def _login_once(self, login_data):
        # url parameter
        payload = {
            'r': random.random(),
            'uuid': login_data['uuid'],
            'version': 2015,
        }

        resp = self.sess.post(self.login, data=login_data, params=payload)
        if self.response_status(resp):
            js = json.loads(resp.text[1:-1])
            # self.print_json(resp.text)

            if not js.get('success'):
                print(js.get('emptyAuthcode'))
                return False
            else:
                return True

        return False

    def _login_try(self):
        """ login by username and password, but not working now.
        .. deprecated::
            Use `login_by_QR`
        """
        # get login page
        # resp = self.sess.get(self.home)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('{0} > 登陆'.format(time.ctime()))

        try:
            # 2016/09/17 PhantomJS can't login anymore
            self.browser.get(self.home)
            soup = bs4.BeautifulSoup(self.browser.page_source, "html.parser")

            # set cookies from PhantomJS
            for cookie in self.browser.get_cookies():
                self.sess.cookies[cookie['name']] = str(cookie['value'])

            # for (k, v) in self.sess.cookies.items():
            #    print '%s: %s' % (k, v)

            # response data hidden input == 9 ??. Changed
            inputs = soup.select('form#formlogin input[type=hidden]')
            rand_name = inputs[-1]['name']
            rand_data = inputs[-1]['value']
            token = ''

            for idx in range(len(inputs) - 1):
                id = inputs[idx]['id']
                va = inputs[idx]['value']
                if id == 'token':
                    token = va
                elif id == 'uuid':
                    self.uuid = va
                elif id == 'eid':
                    self.eid = va
                elif id == 'sessionId':
                    self.fp = va

            auth_code = ''
            if self.need_auth_code(self.usr_name):
                auth_code = self.get_auth_code(self.uuid)
            else:
                print('无验证码登陆')

            login_data = {
                '_t': token,
                'authcode': auth_code,
                'chkRememberMe': 'on',
                'loginType': 'f',
                'uuid': self.uuid,
                'eid': self.eid,
                'fp': self.fp,
                'nloginpwd': self.usr_pwd,
                'loginname': self.usr_name,
                'loginpwd': self.usr_pwd,
                rand_name: rand_data,
            }

            login_succeed = self.login_once(login_data)
            if login_succeed:
                self.trackid = self.sess.cookies['TrackID']
                print('登陆成功 %s' % self.usr_name)
            else:
                print('登陆失败 %s' % self.usr_name)

            return login_succeed

        except Exception as e:
            print('Exception:', e.message)
            raise
        finally:
            self.browser.quit()

        return False

    def login_by_QR(self):
        # jd login by QR code
        try:
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

            urls = (
                'https://passport.jd.com/new/login.aspx',
                'https://qr.m.jd.com/show',
                'https://qr.m.jd.com/check',
                'https://passport.jd.com/uc/qrCodeTicketValidation'
            )

            # step 1: open login page
            resp = self.sess.get(
                urls[0],
                headers=self.headers
            )
            if resp.status_code != requests.codes.OK:
                print('获取登录页失败: %u' % resp.status_code)
                return False

            # save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            # step 2: get QR image
            resp = self.sess.get(
                urls[1],
                headers=self.headers,
                cookies=self.cookies,
                params={
                    'appid': 133,
                    'size': 147,
                    't': (time.time() * 1000)
                }
            )
            if resp.status_code != requests.codes.OK:
                print('获取二维码失败: %u' % resp.status_code)
                return False

            # save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            # save QR code
            image_file = 'qr.png'
            with open(image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
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

            # step 3: check scan result
            # mush have
            self.headers['Host'] = 'qr.m.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 100
            while retry_times:
                retry_times -= 1
                resp = self.sess.get(
                    urls[2],
                    headers=self.headers,
                    cookies=self.cookies,
                    params={
                        'callback': 'jQuery%u' % random.randint(100000, 999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': (time.time() * 1000)
                    }
                )

                if resp.status_code != requests.codes.OK:
                    continue

                n1 = resp.text.find('(')
                n2 = resp.text.find(')')
                rs = json.loads(resp.text[n1 + 1:n2])

                if rs['code'] == 200:
                    print('{} : {}'.format(rs['code'], rs['ticket']))
                    qr_ticket = rs['ticket']
                    break
                else:
                    print('{} : {}'.format(rs['code'], rs['msg']))
                    time.sleep(3)

            if not qr_ticket:
                print('二维码登陆失败')
                return False

            # step 4: validate scan result
            # must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
            resp = self.sess.get(
                urls[3],
                headers=self.headers,
                cookies=self.cookies,
                params={'t': qr_ticket},
            )
            if resp.status_code != requests.codes.OK:
                print('二维码登陆校验失败: %u' % resp.status_code)
                return False

            # 京东有时候会认为当前登录有危险，需要手动验证
            # url: https://safe.jd.com/dangerousVerify/index.action?username=...
            res = json.loads(resp.text)
            if not resp.headers.get('P3P'):
                if 'url' in res:
                    print('需要手动安全验证: {0}'.format(res['url']))
                    return False
                else:
                    self.print_json(res)
                    print('登陆失败!!')
                    return False

            # login succeed
            self.headers['P3P'] = resp.headers.get('P3P')
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            print('登陆成功')
            return True

        except Exception as e:
            print('Exp:', e)
            raise

        return False

    def good_stock(self, stock_id, good_count=1, area_id=None):
        '''
        33 : on sale,
        34 : out of stock
        '''
        # http://ss.jd.com/ss/areaStockState/mget?app=cart_pc&ch=1&skuNum=3180350,1&area=1,72,2799,0
        #   response: {"3180350":{"a":"34","b":"1","c":"-1"}}
        # stock_url = 'http://ss.jd.com/ss/areaStockState/mget'

        # http://c0.3.cn/stocks?callback=jQuery2289454&type=getstocks&skuIds=3133811&area=1_72_2799_0&_=1490694504044
        #   jQuery2289454({"3133811":{"StockState":33,"freshEdi":null,"skuState":1,"PopType":0,"sidDely":"40","channel":1,"StockStateName":"现货","rid":null,"rfg":0,"ArrivalDate":"","IsPurchase":true,"rn":-1}})
        # jsonp or json both work
        stock_url = 'https://c0.3.cn/stocks'

        payload = {
            'type': 'getstocks',
            'skuIds': str(stock_id),
            'area': area_id or '1_72_2799_0',  # area change as needed
        }

        try:
            # get stock state
            resp = self.sess.get(stock_url, params=payload)
            if not self.response_status(resp):
                print('获取商品库存失败')
                return (0, '')

            # return json
            resp.encoding = 'gbk'
            stock_info = json.loads(resp.text)
            stock_stat = int(stock_info[stock_id]['StockState'])
            stock_stat_name = stock_info[stock_id]['StockStateName']

            # 33 : on sale, 34 : out of stock, 36: presell
            return stock_stat, stock_stat_name

        except Exception as e:
            print('Stocks Exception:', e)
            time.sleep(5)

        return (0, '')

    def good_detail(self, stock_id, area_id=None):
        # return good detail
        good_data = {
            'id': stock_id,
            'name': '',
            'link': '',
            'price': '',
            'stock': '',
            'stockName': '',
        }

        try:
            # shop page
            stock_link = 'http://item.jd.com/{0}.html'.format(stock_id)
            resp = self.sess.get(stock_link)

            # good page
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            # good name
            tags = soup.select('div#name h1')
            if len(tags) == 0:
                tags = soup.select('div.sku-name')
            good_data['name'] = tags_val(tags).strip(' \t\r\n')

            # cart link
            tags = soup.select('a#InitCartUrl')
            link = tags_val(tags, key='href')

            if link[:2] == '//':
                link = 'http:' + link
            good_data['link'] = link

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        # good price
        good_data['price'] = self.good_price(stock_id)

        # good stock
        good_data['stock'], good_data['stockName'] = self.good_stock(stock_id=stock_id, area_id=area_id)
        # stock_str = u'有货' if good_data['stock'] == 33 else u'无货'

        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('{0} > 商品详情'.format(time.ctime()))
        print('编号：{0}'.format(good_data['id']))
        print('库存：{0}'.format(good_data['stockName']))
        print('价格：{0}'.format(good_data['price']))
        print('名称：{0}'.format(good_data['name']))
        # print u'链接：{0}'.format(good_data['link'])

        return good_data

    def good_price(self, stock_id):
        # get good price
        url = 'http://p.3.cn/prices/mgets'
        payload = {
            'type': 1,
            'pduid': int(time.time() * 1000),
            'skuIds': 'J_' + stock_id,
        }

        price = '?'
        try:
            resp = self.sess.get(url, params=payload)
            resp_txt = resp.text.strip()
            # print resp_txt

            js = json.loads(resp_txt[1:-1])
            # print u'价格', 'P: {0}, M: {1}'.format(js['p'], js['m'])
            price = js.get('p')

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        return price

    def buy(self, options):
        # stock detail
        good_data = self.good_detail(options.good)

        # retry until stock not empty
        if good_data['stock'] != 33:
            # flush stock state
            while good_data['stock'] != 33 and options.flush:
                print('<%s> <%s>' % (good_data['stockName'], good_data['name']))
                time.sleep(options.wait / 1000.0)
                good_data['stock'], good_data['stockName'] = self.good_stock(stock_id=options.good, area_id=options.area)

            # retry detail
            # good_data = self.good_detail(options.good)

        # failed
        link = good_data['link']
        if good_data['stock'] != 33 or link == '':
            # print u'stock {0}, link {1}'.format(good_data['stock'], link)
            return False

        try:
            # change buy count
            if options.count != 1:
                link = link.replace('pcount=1', 'pcount={0}'.format(options.count))

            # add to cart
            resp = self.sess.get(link, cookies=self.cookies)
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            # tag if add to cart succeed
            tag = soup.select('h3.ftx-02')
            if tag is None:
                tag = soup.select('div.p-name a')

            if tag is None or len(tag) == 0:
                print('添加到购物车失败')
                return False

            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('{0} > 购买详情'.format(time.ctime()))
            print('链接：{0}'.format(link))
            print('结果：{0}'.format(tags_val(tag)))

            # change count after add to shopping cart
            # self.buy_good_count(options.good, options.count)

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))
        else:
            self.cart_detail()
            return self.order_info(options.submit)

        return False

    def buy_good_count(self, good_id, count):
        url = 'http://cart.jd.com/changeNum.action'

        payload = {
            'venderId': '8888',
            'pid': good_id,
            'pcount': count,
            'ptype': '1',
            'targetId': '0',
            'promoID': '0',
            'outSkus': '',
            'random': random.random(),
            'locationId': '1-72-2799-0',  # need changed to your area location id
        }

        try:
            rs = self.sess.post(url, params=payload, cookies=self.cookies)
            if rs.status_code == 200:
                js = json.loads(rs.text)
                if js.get('pcount'):
                    print('数量：%s @ %s' % (js['pcount'], js['pid']))
                    return True
            else:
                print('购买 %d 失败' % count)

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        return False

    def cart_detail(self):
        # list all goods detail in cart
        cart_url = 'https://cart.jd.com/cart.action'
        cart_header = u'购买    数量    价格        总价        商品'
        cart_format = u'{0:8}{1:8}{2:12}{3:12}{4}'

        try:
            resp = self.sess.get(cart_url, cookies=self.cookies)
            resp.encoding = 'utf-8'
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('{0} > 购物车明细'.format(time.ctime()))
            print(cart_header)

            for item in soup.select('div.item-form'):
                check = tags_val(item.select('div.cart-checkbox input'), key='checked')
                check = ' + ' if check else ' - '
                count = tags_val(item.select('div.quantity-form input'), key='value')
                price = tags_val(item.select('div.p-price strong'))
                sums = tags_val(item.select('div.p-sum strong'))
                gname = tags_val(item.select('div.p-name a'))
                #: ￥字符解析出错, 输出忽略￥
                print(cart_format.format(check, count, price[1:], sums[1:], gname))

            t_count = tags_val(soup.select('div.amount-sum em'))
            t_value = tags_val(soup.select('span.sumPrice em'))
            print('总数: {0}'.format(t_count))
            print('总额: {0}'.format(t_value[1:]))

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

    def order_info(self, submit=False):
        # get order info detail, and submit order
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('{0} > 订单详情'.format(time.ctime()))

        try:
            order_url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
            payload = {
                'rid': str(int(time.time() * 1000)),
            }

            # get preorder page
            rs = self.sess.get(order_url, params=payload, cookies=self.cookies)
            soup = bs4.BeautifulSoup(rs.text, "html.parser")

            # order summary
            payment = tag_val(soup.find(id='sumPayPriceId'))
            detail = soup.find(class_='fc-consignee-info')

            if detail:
                snd_usr = tag_val(detail.find(id='sendMobile'))
                snd_add = tag_val(detail.find(id='sendAddr'))

                print('应付款：{0}'.format(payment))
                print(snd_usr)
                print(snd_add)

            # just test, not real order
            if not submit:
                return False

            # order info
            payload = {
                'overseaPurchaseCookies': '',
                'submitOrderParam.btSupport': '1',
                'submitOrderParam.ignorePriceChange': '0',
                'submitOrderParam.sopNotPutInvoice': 'false',
                'submitOrderParam.trackID': self.trackid,
                'submitOrderParam.eid': self.eid,
                'submitOrderParam.fp': self.fp,
            }

            order_url = 'http://trade.jd.com/shopping/order/submitOrder.action'
            rp = self.sess.post(order_url, params=payload, cookies=self.cookies)

            if rp.status_code == 200:
                js = json.loads(rp.text)
                if js['success'] is True:
                    print('下单成功！订单号：{0}'.format(js['orderId']))
                    print('请前往东京官方商城付款')
                    return True
                else:
                    print('下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                    if js['resultCode'] == '60017':
                        # 60017: 您多次提交过快，请稍后再试
                        time.sleep(1)
            else:
                print('请求失败. StatusCode:', rp.status_code)

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        return False


def main(options):
    #
    jd = JDWrapper()
    if not jd.login_by_QR():
        return

    while not jd.buy(options) and options.flush:
        time.sleep(options.wait / 1000.0)


if __name__ == '__main__':
    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and buy sepecified good')
    # parser.add_argument('-u', '--username',
    #                    help='Jing Dong login user name', default='')
    # parser.add_argument('-p', '--password',
    #                    help='Jing Dong login user password', default='')
    parser.add_argument('-a', '--area',
                        help='Area string, like: 1_72_2799_0 for Beijing', default='1_72_2799_0')
    parser.add_argument('-g', '--good',
                        help='Jing Dong good ID', default='')
    parser.add_argument('-c', '--count', type=int,
                        help='The count to buy', default=1)
    parser.add_argument('-w', '--wait',
                        type=int, default=500,
                        help='Flush time interval, unit MS')
    parser.add_argument('-f', '--flush',
                        action='store_true',
                        help='Continue flash if good out of stock')
    parser.add_argument('-s', '--submit',
                        action='store_true',
                        help='Submit the order to Jing Dong')

    # example goods
    hw_watch = '2567304'
    iphone_7 = '3133851'

    options = parser.parse_args()
    print(options)

    # for test
    if options.good == '':
        options.good = iphone_7

    '''
    if options.password == '' or options.username == '':
        print u'请输入用户名密码'
        exit(1)
    '''
    main(options)
