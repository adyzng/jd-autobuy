# JD_AutoBuy

## 京东抢购
Python爬虫，自动登录京东网站，查询商品库存，价格，显示购物车详情等。<br/>
可以指定购买或者抢购预约过的商品，自动购买下单，然后手动去京东付款就行。


## chang log
+ 2017-03-30 实现二维码扫码登陆
+ 2017-06-27 [Golang版JD_AutoBuy](https://github.com/Adyzng/go-jd)
+ 2017-11-01 增加预约抢购的模式，区别普通的购买模式



## 运行环境
Python 2.7


## 第三方库
- [Requests][1]: 简单好用，功能强大的Http请求库
- [beautifulsoup4][2]: HTML文档格式化及便签选择器
- pyinstaller: 用于打包可执行文件（可以不安装）



## 环境配置
``` Python
pip install requests
pip install beautifulsoup4
```


## 使用帮助
``` cmd
> python scraper-jd.py -h
usage: scraper-jd.py [-h] [-u USERNAME] [-p PASSWORD] [-g GOOD] [-c COUNT]
                     [-w WAIT] [-f] [-s]

Simulate to login Jing Dong, and buy sepecified good

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Jing Dong login user name
  -p PASSWORD, --password PASSWORD
                        Jing Dong login user password
  -g GOOD, --good GOOD  Jing Dong good ID
  -c COUNT, --count COUNT
                        The count to buy
  -w WAIT, --wait WAIT  Flush time interval, unit MS
  -f, --flush           Continue flash if good out of stock
  -m, --mode            Purchashe mode, normal or qianggou', default='qianggou'
  -s, --submit          Submit the order to Jing Dong
```

## 实例输出
``` cmd
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Mar 30 17:10:01 2017 > 请打开京东手机客户端，准备扫码登陆:
201 : 二维码未扫描 ，请扫描二维码
201 : 二维码未扫描 ，请扫描二维码
201 : 二维码未扫描 ，请扫描二维码
201 : 二维码未扫描 ，请扫描二维码
202 : 请手机客户端确认登录
200 : BADACIFYhf6fakfHvjiYTlwGzSp4EjFATN3Xw1ePR1hITtw0
登陆成功
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Mar 30 17:10:28 2017 > 商品详情
编号：3133857
库存：现货
价格：6399.00
名称：Apple iPhone 7 Plus (A1661) 128G 黑色 移动联通电信4G手机
链接：http://cart.jd.com/gate.action?pid=3133857&pcount=1&ptype=1
商品已成功加入购物车！
购买数量：3133857 > 1
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Mar 30 17:10:30 2017 > 购物车明细
购买    数量    价格        总价        商品
 Y      1       6399.00     6399.00     Apple iPhone 7 Plus (A1661) 128G 黑色 移动联通电信4G手机
总数: 1
总额: 6399.00
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Mar 30 17:10:30 2017 > 订单详情
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
...
```

## 注
代码仅供学习之用，京东网页不断变化，代码并不一定总是能正常运行。<br/>
如果您发现有Bug，Welcome to Pull Request.


[1]: http://docs.python-requests.org
[2]: https://www.crummy.com/software/BeautifulSoup
