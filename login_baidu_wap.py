# -*-coding:utf-8 -*-
"""
模拟登录baidu wap端
这里提供两种方式：
一种是是指定为手机模式进行请求；
另一种是先打开浏览器，然后打开新窗口
author @boole
date 2019-04-27
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from load_conf import read_conf


class LoginBaiduWap(object):
    def __init__(self, username, password):
        """
        基础参数构造
        :param username:
        :param password:
        """
        # 设置成手机模式
        # mobile_emulation = {"deviceName": "iPhone 6"}
        # options = webdriver.ChromeOptions()
        # options.add_experimental_option("mobileEmulation", mobile_emulation)
        # options.add_argument('disable-infobars')
        # self.browser = webdriver.Chrome('chromedriver', chrome_options=options)

        # 在运行之前需要运行下面命令（使用Google Chrome，指定端口为9222，user-data-dir为selenium配置地址）
        # "Google Chrome" --remote-debugging-port=9222 --user-data-dir="seleium_dir"
        # 在打开的浏览器中新开窗口
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(chrome_options=options)

        self.url = 'https://wappass.baidu.com/passport/login'
        self.username = username
        self.password = password
        self.retry = 3

    def login(self):
        """
        输入信息并登录
        :return:
        """
        try:
            username = self.browser.find_element_by_id("login-username")
            username.clear()
            username.send_keys(self.username)
            time.sleep(3)
            password = self.browser.find_element_by_id("login-password")
            password.clear()
            password.send_keys(self.password)
            time.sleep(3)
            el = self.browser.find_element_by_id('login-submit')
            # 回车
            el.send_keys(Keys.ENTER)
            return 0
        except Exception as e:
            print(str(e))
            return 1

    def main(self):
        """
        主控制函数
        :return:
        """
        print('开始登录')
        self.browser.get(self.url)
        for i in range(self.retry):
            self.browser.implicitly_wait(10)  # 隐性等待10s
            if self.browser.current_url == self.url:
                touchLogin_typ = self.login()
                if touchLogin_typ != 0:
                    print("第 %d 次登录失败(共尝试%s次)" % (i + 1, self.retry))
                    sys.exit("touchLogin error")
                time.sleep(5)
            else:
                print("登录成功")
                break


if __name__ == '__main__':
    name = read_conf("baidu_info", "username")
    passwd = read_conf("baidu_info", "password")
    LBW = LoginBaiduWap(name, passwd)
    LBW.main()

