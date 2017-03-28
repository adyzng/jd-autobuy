# JD_AutoBuy

## 京东抢购
Python爬虫，自动登录京东网站，查询商品库存，价格，显示购物车详情等。<br/>
可以指定抢购商品，自动购买下单，然后手动去京东付款就行。

2017-03-28： 实现二维码扫码登陆，不在依赖PhantomJs.


## 运行环境
Python 2.7


## 第三方库
- [Requests][3]: 简单好用，功能强大的Http请求库。唯一的一个非转基因的Python HTTP库，人类可以安全享用。
- [selenium][4]: 一个浏览器自动化测试工具。本例主要用来执行PhantomJS，模拟登陆用。
- [beautifulsoup4][5]: HTML文档格式化及便签选择器

Requests库只能爬静态页面，京东登录有时需验证码，有时不需要，而且证码验证码是靠JS动态生成，比较复杂尚未研究清楚。
所以需要一个能执行JS的容器，来模拟登陆，登陆之后的其他请求使用Requests库来操作。<br/>
有两个选择：
- [PhantomJS][1]: 一个基于WebKit的无UI模拟浏览器，它全面支持web而不需浏览器支持。
- [dryscrape][2]: 一个轻量级的Python开源爬虫库。可惜Windows平台不支持，在Linux下倒是一个很好的选择。


## 环境配置
``` Python
pip install requests
pip install selenium
pip install beautifulsoup4
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

## 实例输出
``` cmd
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 23:51:30 2016 > 登陆
无验证码登陆
登陆成功 ****
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 23:51:36 2016 > 商品详情
编号：2567304
库存：有货
价格：2188.00
名称：华为 HUAWEI WATCH 经典系列 智能手表（不锈钢三珠表带） 手表蓝牙通话 星河银
链接：http://cart.jd.com/gate.action?pid=2567304&pcount=1&ptype=1
商品已成功加入购物车！
购买数量：2567304 > 2
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 23:51:38 2016 > 购物车明细
购买    数量    价格        总价        商品
 Y      2       2188.00     4376.00     华为 HUAWEI WATCH 经典系列 智能手表（不锈钢三珠表带） 手表蓝牙通话 星河银
 -      1       169.00      169.00      【活动商品】小米（MI）小米手环2 心率监测 来电提醒
 -      1       199.00      199.00      小米（MI）小米手环2 心率监测 来电提醒
 -      1       69.00       69.00       LAMY凌美50MLT52黑色墨水
总数: 2
总额: 4376.00
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Thu Aug 11 23:51:38 2016 > 订单详情
应付款：￥4376.00
收货人：*** 18*********
寄送至： 北京*******************
下单成功！订单号：212****1442
请前往东京官方商城付款
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
```

## 注
代码仅供学习之用，京东网页不断变化，代码并不一定总是能正常运行。<br/>
如果您发现有Bug，Welcome to Pull Request.


[1]: http://phantomjs.org
[2]: https://github.com/niklasb/dryscrape
[3]: http://docs.python-requests.org
[4]: http://docs.seleniumhq.org
[5]: https://www.crummy.com/software/BeautifulSoup
