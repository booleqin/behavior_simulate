# -*-coding:utf-8 -*-
"""
模拟登录baidu pc端
author @boole
date 2019-04-27
"""

import sys
import time
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from PIL import Image
from load_conf import read_conf


"""
伪造ip
IP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
伪造ua
from fake_useragent import UserAgent
UA = UserAgent().random
"""
# 伪造屏幕信息
WIDTH = 1080
HEIGHT = 800
PIXEL_RATIO = 3.0
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/72.0.3626.121 Safari/537.36'


class LoginBaiduPc(object):
    def __init__(self, username, password):
        """
        基础参数构造
        :param username:
        :param password:
        """
        pc_emulation = {"deviceMetrics": {"width": WIDTH, "height": HEIGHT,
                                          "pixelRatio": PIXEL_RATIO}, "userAgent": UA}
        options = webdriver.ChromeOptions()
        options.add_experimental_option('mobileEmulation', pc_emulation)
        options.add_argument('disable-infobars')

        self.browser = webdriver.Chrome('chromedriver', chrome_options=options)
        self.url = 'https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F&sms=5'
        self.wait = WebDriverWait(self.browser, 100)
        self.username = username
        self.password = password
        self.retry = 3

    def input_info(self):
        """
        使用用户名登录
        :return:
        """
        # while True:
        try:
            s = "no"
            style_txt = self.browser.find_element_by_id('login').get_attribute('style')
            style_l = re.split(";|:", style_txt.replace(" ", ""))
            if style_l[1] == "block":
                s = "username"
            elif style_l[1] == "none":
                s = "code"
            else:
                print("登录页面不正确")

            if s == "code":
                time.sleep(1)
                username_btn = self.browser.find_element_by_id('TANGRAM__PSP_3__footerULoginBtn')
                username_btn.click()
            return 0
        except Exception as e:
            print(str(e))
            return 1

    def login(self):
        """
        登录百度pc端
        :return:
        """
        # 输入用户名密码
        try:
            user_name = self.wait.until(EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_3__userName')))
            user_name.clear()
            user_name.send_keys(self.username)
            time.sleep(3)
            password = self.wait.until(EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_3__password')))
            password.clear()
            password.send_keys(self.password)
            time.sleep(3)
        except Exception as e:
            print(str(e))
            return 1
        # 如果出验证码需要跳验证码
        try:
            src = self.wait.until(EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_3__verifyCodeImg'))) \
                .get_attribute('src')
            if "genimage" in src:
                # 截图保存
                # 如果截图出现问题，可以考虑先设置好窗口大小
                # browser.set_window_size(1080, 800)
                print(self.browser.get_window_size())
                window_w = self.browser.get_window_size()["width"]
                window_h = self.browser.get_window_size()["height"]
                self.browser.save_screenshot('./CrawlResult/baidupc.png')
                element = self.browser.find_element_by_id('TANGRAM__PSP_3__verifyCodeImg')
                left = element.location['x']
                top = element.location['y']
                right = element.location['x'] + element.size['width']
                bottom = element.location['y'] + element.size['height']
                # 截图
                im = Image.open('./CrawlResult/baidupc.png')
                # print(im.size)
                left = left * im.size[0] / window_w
                top = top * im.size[1] / window_h
                right = right * im.size[0] / window_w
                bottom = bottom * im.size[1] / window_h

                bim = im.crop((left, top, right, bottom))
                bim.save('./CrawlResult/baidupc_code.png')
                # 这里接验证码识别的程序

        except Exception as e:
            print(str(e))
            return 1
        # 登录
        try:
            member = self.browser.find_element_by_id('TANGRAM__PSP_3__memberPass')
            member.click()
            time.sleep(2)
            login_submit = self.browser.find_element_by_id('TANGRAM__PSP_3__submit')
            login_submit.click()
            return 0
        except Exception as e:
            print(str(e))
            return 1

    def main(self):
        """
        主函数
        :return:
        """
        print("开始登录")
        # 打开浏览器
        self.browser.get(self.url)
        for i in range(self.retry):
            if self.browser.current_url == self.url:
                # 用户名登录
                input_info_typ = self.input_info()
                if input_info_typ != 0:
                    print("第 %d 次登录失败(共尝试%s次)" % (i + 1, self.retry))
                    sys.exit("input_info error")
                # 输入信息并登录
                login_typ = self.login()
                if login_typ != 0:
                    print("第 %d 次登录失败(共尝试%s次)" % (i + 1, self.retry))
                    sys.exit("login error")
                time.sleep(5)
            else:
                print("登录成功")
                break


if __name__ == '__main__':
    name = read_conf("baidu_info", "username")
    passwd = read_conf("baidu_info", "password")
    LBP = LoginBaiduPc(name, passwd)
    LBP.main()

