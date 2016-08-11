# JD_AutoBuy

## 京东抢购
Python爬虫，自动登录京东网站，查询商品库存，价格，显示购物车详情等。
可以指定抢购商品，自动购买下单，然后手动去京东付款就行。


## 运行环境
Python 2.7


## 第三方库
- [Requests](http://docs.python-requests.org): 简单好用，功能强大的Http请求库。唯一的一个非转基因的Python HTTP库，人类可以安全享用。
- [selenium](http://docs.seleniumhq.org): 一个浏览器自动化测试工具。本例主要用来执行PhantomJS，模拟登陆用。

Requests库只能爬静态页面，京东登录有时需验证码，有时不需要，而且证码验证码是靠JS动态生成，比较复杂尚未研究清楚。
所以需要一个能执行JS的容器，来模拟登陆，登陆之后的其他请求使用Requests库来操作。<br/>
有两个选择：
- [PhantomJS](http://phantomjs.org): 一个基于WebKit的无UI模拟浏览器，它全面支持web而不需浏览器支持。
- [dryscrape](https://github.com/niklasb/dryscrape): 一个轻量级的Python开源爬虫库。可惜Windows平台不支持，在Linux下倒是一个很好的选择。


## 环境配置
``` Python
pip install requests
pip install selenium
```

PhantomJS是一个可执行文件，下载下来解压到%PATH%目录下，或者跟python.exe同级也行。
``` Python
try:
	self.browser = webdriver.PhantomJS('phantomjs.exe')
except Exception, e:
	pass
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
  -s, --submit          Submit the order to Jing Dong
```

实例输出
``` cmd
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 14:36:21 2016 > 登陆
无验证码登陆
登陆成功 Adyzng
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 14:36:27 2016 > 商品详情
编号：3180350
库存：有货
价格：169.00
名称：【活动商品】小米（MI）小米手环2 心率监测 来电提醒
链接：http://cart.jd.com/gate.action?pid=3180350&pcount=1&ptype=1
商品已成功加入购物车！
购买数量：3180350 > 1
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 14:36:40 2016 > 购物车明细
购买    数量    价格        总价        商品
 Y      1       169.00      169.00      【活动商品】小米（MI）小米手环2 心率监测 来电提醒
 -      1       69.00       69.00       LAMY凌美50MLT52黑色墨水
 -      1       2188.00     2188.00     华为 HUAWEI WATCH 经典系列 智能手表（不锈钢三珠表带） 手表蓝牙通话 星河银
总数: 1
总额: ￥169.00
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 14:36:40 2016 > 订单详情
应付款：￥169.00
收货人：张* 188******
寄送至： 北京 *******************
下单失败！<600158: 【活动商品】小米（MI）小米手环2 心率监测 来电提醒商品无货>
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
```

