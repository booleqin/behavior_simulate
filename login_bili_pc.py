# -*-coding:utf-8 -*-
"""
模拟登录 bilibili pc端
author @boole
date 2019-04-27
"""

import time
import re
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import PIL.Image as image
from urllib.request import urlretrieve
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


def judge_pixel(img1, img2, x, y):
    """
    判断像素是否相同
    :param img1:
    :param img2:
    :param x:
    :param y:
    :return: 像素是否相同
    """
    # 取两个图片的像素点
    pix1 = img1.load()[x, y]
    pix2 = img2.load()[x, y]
    threshold = 10
    if (abs(pix1[0] - pix2[0] < threshold) and
            abs(pix1[1] - pix2[1] < threshold) and
            abs(pix1[2] - pix2[2] < threshold)):
        return True
    else:
        return False


def merge_img(filename, location_list):
    """
    根据位置对图片进行合并
    :param filename:
    :param location_list:
    :return:
    """
    im = image.open(filename)
    im_list_upper = []
    im_list_down = []

    for location in location_list:
        if location['y'] == -58:
            im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
        if location['y'] == 0:
            im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

    new_im = image.new('RGB', (260, 116))
    x_offset = 0
    for im in im_list_upper:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    x_offset = 0
    for im in im_list_down:
        new_im.paste(im, (x_offset, 58))
        x_offset += im.size[0]
    new_im.save(filename)
    return new_im


def get_gap(img1, img2):
    """
    获取缺口偏移量
    :param img1: 不带缺口图片
    :param img2: 带缺口图片
    :return:
    """
    left = 0
    for i in range(left, img1.size[0]):
        for j in range(img1.size[1]):
            if not judge_pixel(img1, img2, i, j):
                left = i
                return left
    return left


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


class LoginBiliPc(object):
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
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('disable-infobars')
        self.browser = webdriver.Chrome('chromedriver', chrome_options=options)

        self.url = 'https://passport.bilibili.com/login'
        self.wait = WebDriverWait(self.browser, 100)
        self.BORDER = 6
        self.password = password
        self.username = username

    def input_info(self):
        """
        打开浏览器,并输入必要信息
        :return:
        """
        self.browser.get(self.url)
        user_name = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        user_name.clear()
        user_name.send_keys(self.username)
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        password.clear()
        password.send_keys(self.username)
        # bowton.click()

    def get_images(self, bg_filename='bg.jpg', gap_filename='gap.jpg'):
        """
        获取验证码图片，图片是很多图片合成的，需要自己合成
        :param bg_filename: 背景图片
        :param gap_filename: 缺口图片
        :return:
        """
        bg = []
        gap = []
        while bg == [] and gap == []:
            bf = BeautifulSoup(self.browser.page_source, 'lxml')
            bg = bf.find_all('div', class_='gt_cut_bg_slice')
            gap = bf.find_all('div', class_='gt_cut_fullbg_slice')

        bg_location_list = []
        gap_location_list = []
        loc1, loc2 = {}, {}
        for each_bg in bg:
            loc1['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][0])
            loc1['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][1])
            bg_location_list.append(loc1)
        for each_gap in gap:
            loc2['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_gap.get('style'))[0][0])
            loc2['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_gap.get('style'))[0][1])
            gap_location_list.append(loc2)

        # 保存图片
        bg_url = re.findall('url\(\"(.*)\"\);', bg[0].get('style'))[0].replace('webp', 'jpg')
        gap_url = re.findall('url\(\"(.*)\"\);', gap[0].get('style'))[0].replace('webp', 'jpg')
        urlretrieve(url=bg_url, filename=bg_filename)
        urlretrieve(url=gap_url, filename=gap_filename)

        return bg_location_list, gap_location_list

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
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
        print('开始登录')
        self.browser.get(self.url)
        self.input_info()
        bg_filename = './data/bilibg.jpg'
        gap_filename = './data/biligap.jpg'

        bg_location_list, gap_location_list = self.get_images(bg_filename, gap_filename)

        bg_img = merge_img(bg_filename, bg_location_list)
        gap_img = merge_img(gap_filename, gap_location_list)

        gap = get_gap(bg_img, gap_img)
        # print('缺口位置', gap)

        track = get_track(gap-self.BORDER)
        print('滑动滑块')
        # print("track", track)

        slider = self.get_slider()
        self.move_to_gap(slider, track)

        if self.browser.current_url == self.url:
            print("登录失败")
        else:
            print("登录成功")


if __name__ == '__main__':
    name = read_conf("bili_info", "username")
    passwd = read_conf("bili_info", "password")
    LBP = LoginBiliPc(name, passwd)
    LBP.main()


