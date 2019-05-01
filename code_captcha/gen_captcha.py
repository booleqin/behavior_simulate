# -*-coding:utf-8 -*-
"""
生成文字验证码(限英文)
author @boole
date 2019-04-27
"""

import random
import numpy as np
from PIL import Image
from captcha.image import ImageCaptcha
import matplotlib.pyplot as plt

code_dir = './codeimg/'
num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
char_low = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
char_up = list(map(lambda x: x.upper(), char_low))
library_text = num
n = 50000  # 生成验证码数量

IMAGE_HEIGHT = 120
IMAGE_WIDTH = 270
MAX_CAPTCHA = 4


class GenerateCaptcha(object):
    """
    生成验证码
    """
    def __init__(self, lib_text):
        """
        基础属性
        :param lib_text: 验证码文本库
        """
        self.lib_text = lib_text
        self.captcha_size = MAX_CAPTCHA
        self.width = IMAGE_WIDTH  # 验证码宽度 (尺寸配合字体大小可调整难度)
        self.height = IMAGE_HEIGHT  # 验证码高度

    def random_text(self):
        """
        生成随机文本
        :return: 验证码文本
        """
        captcha_text = []
        for _ in range(self.captcha_size):
            c = random.choice(self.lib_text)
            captcha_text.append(c)
        return ''.join(captcha_text)

    def gen_captcha_image(self, save=True):
        """
        生成验证码图片
        :return: 验证码标签 图片
        """
        Im = ImageCaptcha(width=self.width, height=self.height)
        captcha_text = self.random_text()
        captcha = Im.generate(captcha_text)
        if save:
            Im.write(captcha_text, code_dir + captcha_text + '.png')  # 写到文件
        captcha_image = Image.open(captcha)
        captcha_image = np.array(captcha_image)
        return captcha_text, captcha_image


if __name__ == '__main__':
    # 为了提高训练速度，这里使用纯数字
    GC = GenerateCaptcha(num)
    for i in range(n):
        text, img = GC.gen_captcha_image(save=True)

    """
    可视化
    print(text)
    f = plt.figure()
    ax = f.add_subplot(111)
    # ax.text(0.1, 0.9, text, ha='center', va='center', transform=ax.transAxes)
    plt.imshow(img)
    plt.show()
    """
