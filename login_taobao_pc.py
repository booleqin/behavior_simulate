# -*-coding:utf-8 -*-
"""
模拟登录taobao pc端
author @boole
date 2019-04-27
"""

import time
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from load_conf import read_conf


def get_track(distance):
    """
    根据偏移量获取移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    track = []
    current = 0
    mid = distance * 4 / 5
    t = 0.3
    v = 0

    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        track.append(round(move))
    return track


class LoginTaobaoPc(object):
    def __init__(self, username, password):
        """
        基础参数构造
        :param phone:
        """
        # 在运行之前需要运行下面命令（使用Google Chrome，指定端口为9222，user-data-dir为selenium配置地址）
        # "Google Chrome" --remote-debugging-port=9222 --user-data-dir="seleium_dir"
        # 在打开的浏览器中新开窗口
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(chrome_options=options)

        self.url = 'https://login.taobao.com/member/login.jhtml?spm=1.7156474.1997563269.1.' \
                   'TD7BlX&f=top&redirectURL=http%3A%2F%2Ferr.taobao.com%2Ferror2.html'
        self.wait = WebDriverWait(self.browser, 100)
        self.BORDER = 6
        self.username = username
        self.password = password

    def choose_username(self):
        """
        判断是否是账号密码登录，如果不是，则选择帐号密码登录
        :return:
        """
        username_btn = self.browser.find_element_by_css_selector("[class='forget-pwd J_Quick2Static']")
        anchor = username_btn.get_attribute('data-spm-anchor-id')
        if anchor is None:
            username_btn.click()

    def input_data(self):
        """
        输入指定内容
        """
        user_name = self.browser.find_element_by_id('TPL_username_1')
        user_name.clear()
        user_name.send_keys(self.username)
        password = self.browser.find_element_by_id('TPL_password_1')
        password.clear()
        password.send_keys(self.password)
        # bowton.click()

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_id("nc_1_n1z")
                break
            except Exception as e:
                print(str(e))
                time.sleep(0.5)
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处，使用ActionChains模拟鼠标键盘
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for t in track:
            ActionChains(self.browser).move_by_offset(xoffset=t, yoffset=0).perform()
        else:
            ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
            ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def main(self):
        """
        主函数
        :return:
        """
        print("开始登录")
        # 打开浏览器
        self.browser.get(self.url)
        # 选择密码登录
        self.choose_username()
        # 输入注册数据
        self.input_data()
        # 获取滑块
        slider = self.get_slider()
        # 构造轨迹
        track = get_track(300-self.BORDER)
        # # 拖动滑块到右侧（300px）
        self.move_to_gap(slider, track)
        if self.browser.current_url == self.url:
            print("注册失败")
        else:
            print("注册成功")


if __name__ == '__main__':
    name = read_conf("taobao_info", "username")
    passwd = read_conf("taobao_info", "password")
    LTP = LoginTaobaoPc(name, passwd)
    LTP.main()


