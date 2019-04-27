# 浏览器行为模拟
## 主要环境

Python: 3.6.5

selenium: 3.14.0

Pillow: 5.1.0

## 行为模拟

使用selenium进行浏览器行为模拟，主要原理如下：
1. 模拟浏览器环境
- 打开浏览器访问指定url
- 跳转到要操作的页面
- 定位目标元素
- 操作目标元素

## 运行

登录所用的信息在conf/global.conf下，每个文件可以单独运行，如

python login_baidu_pc.py

## 其他

很多爬虫是基于真实cookie的，一旦cookie的使用超过频控就需要更新cookie，成本稍高，如果直接登录，能节约大量成本。

模拟浏览器行为本身难度不大，主要是如何绕过网站的人机识别。


