# -*-coding:utf-8 -*-
"""
验证码与向量互相转换
author @boole
date 2019-04-27
"""

import os
import random
import numpy as np
from PIL import Image
from gen_captcha import code_dir
from gen_captcha import library_text as LIB_TEXT
from gen_captcha import IMAGE_HEIGHT, IMAGE_WIDTH, MAX_CAPTCHA


def get_name_img():
    """
    获取图片和标签
    :return: 标签 图片
    """
    all_image = os.listdir(code_dir)
    random_file = random.randint(0, len(all_image))
    base = os.path.basename(code_dir + all_image[random_file])
    name = os.path.splitext(base)[0]
    image = Image.open(code_dir + all_image[random_file])
    image = np.array(image)
    return name, image


def convert2gray(img):
    """
    灰度处理
    :param img: 图片
    :return: 灰度处理后的图片
    """
    if len(img.shape) > 2:
        img = np.mean(img, -1)
    return img


def name2vec(name):
    """
    将标签转化为向量
    :param name: 标签
    :return: 向量
    """
    text_len = len(name)
    if text_len > MAX_CAPTCHA:
        raise ValueError('验证码最长%s个字符' % MAX_CAPTCHA)
    v = np.zeros(MAX_CAPTCHA * len(LIB_TEXT))
    for i in range(text_len):
        v[LIB_TEXT.index(name[i]) + i * len(LIB_TEXT)] = 1
    return v


def vec2name(vec):
    """
    向量还原为标签
    :param vec: 向量
    :return: 标签
    """
    name = []
    for v in range(len(vec)):
        if vec[v] == 1:
            index = v % len(LIB_TEXT)
            name.append(LIB_TEXT[index])
    return ''.join(name)


def get_batch(batch_size=64):
    """
    生成一个训练batch
    :param batch_size:
    :return:
    """
    batch_x = np.zeros([batch_size, IMAGE_HEIGHT * IMAGE_WIDTH])
    batch_y = np.zeros([batch_size, MAX_CAPTCHA * len(LIB_TEXT)])

    for i in range(batch_size):
        try:
            name, image = get_name_img()
            image = convert2gray(image)
            batch_x[i, :] = 1 * (image.flatten())
            batch_y[i, :] = name2vec(name)
        except Exception as e:
            print("get_batch %s" % str(e))
            pass
    return batch_x, batch_y


if __name__ == '__main__':
    x, y = get_batch(batch_size=1)
    print(x, y)

