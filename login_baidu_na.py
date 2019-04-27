# -*-coding:utf-8 -*-
"""
模拟登录baidu na端
author @boole
date 2019-04-27
"""

import time
from selenium import webdriver
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from load_conf import read_conf


class LoginBaiduNa(object):
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

        self.url = 'https://wappass.baidu.com/passport/login?clientfrom=native'
        self.username = username
        self.password = password
        self.retry = 3
        self.slide_retry = 2

    def choose_username(self):
        """
        判断是否是账号密码登录，如果不是，则选择帐号密码登录
        :return:
        """
        cla = self.browser.find_element_by_id('login').get_attribute('class')
        if "history_login" in cla:
            time.sleep(3)
            other_login = self.browser.find_element_by_id('login-otherLogin')
            TouchActions(self.browser).tap(other_login).perform()

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
            # 模拟回车
            el.send_keys(Keys.ENTER)
            return 0
        except Exception as e:
            print(str(e))
            return 1

    def modCode(self):
        """
        判断是否触发验证码
        :return:
        """
        try:
            pm = self.browser.find_element_by_class_name("mod-vcode-body")
            # print(pm)
            return pm
        except Exception as e:
            print(str(e))
            return 0

    def slide_code(self):
        """
        如果触发滑块验证拖动滑块
        :return:
        """
        pm = self.modCode()
        if pm != 0:
            # 起始位置
            pm_button = self.browser.find_element_by_class_name("vcode-slide-button")
            # print(pm_button.location, pm_button.size)
            start_x = int(pm_button.location['x'] + pm_button.size['width'] / 2)
            start_y = int(pm_button.location['y'] + pm_button.size['height'] / 2)

            # 目标位置
            slide_site = self.browser.find_element_by_class_name("vcode-slide-bottom")
            # print(slide_site.location, slide_site.size)
            left = slide_site.location['x']
            top = slide_site.location['y']
            right = left + slide_site.size['width']
            bottom = top + slide_site.size['height']
            end_x = int(right)
            end_y = int((top + bottom) / 2)
            # print(start_x, start_y, end_x, end_y)
            # 拖动滑块
            TouchActions(self.browser).flick_element(pm_button, end_x - start_x, end_y - start_y, 500).perform()

    def main(self):
        """
        main
        :return:
        """
        print('开始登录')
        self.browser.get(self.url)
        self.choose_username()
        for i in range(self.retry):
            self.browser.implicitly_wait(10)  # 隐性等待10s
            if self.browser.current_url == self.url:
                touchLogin_typ = self.login()
                time.sleep(3)
                if touchLogin_typ != 0:
                    print("第 %d 次登录失败(共尝试%s次)" % (i + 1, self.retry))
                    # sys.exit("touchLogin error")
                for j in range(self.slide_retry):
                    if self.browser.current_url == self.url:
                        self.slide_code()
                        time.sleep(5)
                    else:
                        break
                time.sleep(5)
            else:
                print("登录成功")
                break


if __name__ == '__main__':
    name = read_conf("baidu_info", "username")
    passwd = read_conf("baidu_info", "password")
    LBN = LoginBaiduNa(name, passwd)
    LBN.main()
