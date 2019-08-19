# JD_Robot

## 京东抢购
Python爬虫，扫码登录京东网站，查询商品库存，价格，显示购物车详情等。<br/>
可以指定抢购商品，自动购买下单，然后手动去京东付款就行。


## 版本历史
+ 2017-03-30 [Python2版实现二维码扫码登陆](https://github.com/Adyzng/jd-autobuy)
+ 2017-06-27 [Golang版JD_AutoBuy](https://github.com/Adyzng/go-jd)
+ 2019-07-26 重新实现自动购买下单，下单成功发送邮件提醒
+ 2019-08-08 1.修复了重复添加购物车的bug  2.修复了和别的商品一起提交订单的bug


## 运行环境
Python 3


## 第三方库
- [requests][1]: 简单好用，功能强大的Http请求库
- [bs4][2]: 从HTML或XML文件中提取数据的Python库
- [lxml][2]: lxml is a Pythonic, mature binding for the libxml2 and libxslt libraries



## 环境配置
``` Python
pip install requests
pip install bs4
pip install xlml
```


## 使用帮助
``` cmd
> python spider.py -h
usage: spider.py [-h] [-g GOOD] [-c COUNT]
                     [-w WAIT] [-f] [-s]

Simulate to login Jing Dong, and buy sepecified good

optional arguments:
  -h, --help            show this help message and exit
  -g GOOD, --good GOOD  Jing Dong good ID
  -c COUNT, --count COUNT
                        The count to buy
  -w WAIT, --wait WAIT  Flush time interval, unit MS
  -f, --flush           Continue flash if good out of stock
  -s, --submit          Submit the order to Jing Dong
```

## 实例输出
``` python3 spider.py
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
[ERROR] checkLogin: [Errno 2] No such file or directory: 'cookie'
Fri Jul 26 10:32:25 2019 > 自动登录中... 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Fri Jul 26 10:32:25 2019 > 请打开京东手机客户端，准备扫码登录:
201 : 二维码未扫描，请扫描二维码
201 : 二维码未扫描，请扫描二维码
201 : 二维码未扫描，请扫描二维码
201 : 二维码未扫描，请扫描二维码
201 : 二维码未扫描，请扫描二维码
201 : 二维码未扫描，请扫描二维码
200 : AAEAMJO13YdPif0VLnrBInm9aLcfcVYeGu2_TEBgU0wTmLpTB3s_0a4s3Xw4YmsVCBYBDQ
登录成功
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Fri Jul 26 10:32:50 2019 > 商品详情
编号：5173441
库存：�ֻ�
价格：4477.00
名称：Apple iPad Pro 平板电脑 10.5 英寸（64G WLAN+Cellular版/A10X MQFF2CH/A）玫瑰金色
加入购物车链接：http://cart.jd.com/gate.action?pid=5173441&pcount=1&ptype=1
商品已成功加入购物车！
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Fri Jul 26 10:32:52 2019 > 购物车明细
购买    数量     价格        总价        商品
 +      1       ¥4477.00    ¥4477.00    Apple iPad Pro 平板电脑 10.5 英寸（64G WLAN+Cellular版/A10X MQFF2CH/A）玫瑰金色
总数: 1
总额: 4477.00
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
Fri Jul 26 10:32:52 2019 > 订单详情
应付款：￥4477.00
收货人：李** 137****3886
寄送至： 浙江 台州市 温岭市 **镇
下单成功！订单号：100442880794
请前往京东官方商城付款
```

## 注
代码仅供学习之用，京东网页不断变化，代码并不一定总是能正常运行。<br/>
如果您发现有Bug，Welcome to Pull Request.


[1]: http://docs.python-requests.org
[2]: https://www.crummy.com/software/BeautifulSoup

