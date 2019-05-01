# -*-coding:utf-8 -*-
"""
使用cnn进行验证码识别
author @boole
date 2019-04-27
"""

import tensorflow as tf
from datetime import datetime
from gen_captcha import library_text as LIB_TEXT
from gen_captcha import IMAGE_HEIGHT, IMAGE_WIDTH, MAX_CAPTCHA
from vec_captcha import get_batch


BATCH_SIZE = 64
LEARN_RATE = 0.003


def weight_variable(shape, w_alpha=0.01):
    """
    初始化权值
    :param shape:
    :param w_alpha:
    :return:
    """
    initial = w_alpha * tf.random_normal(shape)
    return tf.Variable(initial)


def bias_variable(shape, b_alpha=0.1):
    """
    初始化偏置项
    :param shape:
    :param b_alpha:
    :return:
    """
    initial = b_alpha * tf.random_normal(shape)
    return tf.Variable(initial)


def conv2d(x, w):
    """
    卷基层
    :param x:
    :param w:
    :return:
    """
    return tf.nn.conv2d(x, w, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    """
    池化层
    :param x:
    :return:
    """
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


def cnn_graph(x, keep_prob, size, captcha_list=LIB_TEXT, captcha_len=MAX_CAPTCHA):
    """
    三层卷积神经网络
    :param x: 训练集 image x
    :param keep_prob: 神经元利用率
    :param size: 大小 (高,宽)
    :param captcha_list:
    :param captcha_len:
    :return: y_conv
    """
    # 将图片reshape为4维向量
    image_height, image_width = size
    x_image = tf.reshape(x, shape=[-1, image_height, image_width, 1])

    # 第一层
    w_conv1 = weight_variable([3, 3, 1, 32])  # 3 * 3的采样窗口，32个通道
    b_conv1 = bias_variable([32])
    h_conv1 = tf.nn.relu(conv2d(x_image, w_conv1) + b_conv1)  # rulu激活函数
    h_pool1 = max_pool_2x2(h_conv1)     # 池化
    h_drop1 = tf.nn.dropout(h_pool1, keep_prob)  # dropout防止过拟合

    # 第二层
    w_conv2 = weight_variable([3, 3, 32, 64])
    b_conv2 = bias_variable([64])
    h_conv2 = tf.nn.relu(conv2d(h_drop1, w_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)
    h_drop2 = tf.nn.dropout(h_pool2, keep_prob)

    # 第三层
    w_conv3 = weight_variable([3, 3, 64, 64])
    b_conv3 = bias_variable([64])
    h_conv3 = tf.nn.relu(conv2d(h_drop2, w_conv3) + b_conv3)
    h_pool3 = max_pool_2x2(h_conv3)
    h_drop3 = tf.nn.dropout(h_pool3, keep_prob)

    # 全连接层
    image_height = int(h_drop3.shape[1])
    image_width = int(h_drop3.shape[2])
    w_fc = weight_variable([image_height * image_width * 64, 1024])
    b_fc = bias_variable([1024])
    h_drop3_re = tf.reshape(h_drop3, [-1, image_height * image_width * 64])
    h_fc = tf.nn.relu(tf.matmul(h_drop3_re, w_fc) + b_fc)
    h_drop_fc = tf.nn.dropout(h_fc, keep_prob)

    # 输出层
    w_out = weight_variable([1024, len(captcha_list) * captcha_len])  # 4 * 10纬的网络
    b_out = bias_variable([len(captcha_list) * captcha_len])
    y_conv = tf.matmul(h_drop_fc, w_out) + b_out
    return y_conv


def optimize_graph(y, y_conv):
    """
    优化计算图
    :param y: 正确值
    :param y_conv: 预测值
    :return: optimizer
    """
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=y_conv))
    optimizer = tf.train.AdamOptimizer(LEARN_RATE).minimize(loss)
    return optimizer


def accuracy_graph(y, y_conv, width=len(LIB_TEXT), height=MAX_CAPTCHA):
    """
    偏差计算图，正确值和预测值，计算准确度
    :param y: 正确值 标签
    :param y_conv: 预测值
    :param width: 验证码预备字符列表长度
    :param height: 验证码的大小
    :return: 正确率
    """
    # 预测值
    predict = tf.reshape(y_conv, [-1, height, width])
    max_predict_idx = tf.argmax(predict, 2)
    # 标签
    label = tf.reshape(y, [-1, height, width])
    max_label_idx = tf.argmax(label, 2)
    correct_p = tf.equal(max_predict_idx, max_label_idx)
    accuracy = tf.reduce_mean(tf.cast(correct_p, tf.float32))
    return accuracy


def train(height=IMAGE_HEIGHT, width=IMAGE_WIDTH, y_size=len(LIB_TEXT) * MAX_CAPTCHA):
    """
    cnn训练
    :param height: 验证码高度
    :param width: 验证码宽度
    :param y_size: 验证码预备字符列表长度*验证码长度
    :return:
    """
    acc_rate = 0.1
    model_path = "./model/codecaptcha.model"  # 保存模型
    x = tf.placeholder(tf.float32, [None, height * width])
    y = tf.placeholder(tf.float32, [None, y_size])

    keep_prob = tf.placeholder(tf.float32)
    y_conv = cnn_graph(x, keep_prob, (height, width))
    optimizer = optimize_graph(y, y_conv)
    accuracy = accuracy_graph(y, y_conv)
    # 启动会话.开始训练
    saver = tf.train.Saver()
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    step = 0    # 步数
    while 1:
        batch_x, batch_y = get_batch(BATCH_SIZE)
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y, keep_prob: 0.75})
        # 每训练一百次测试一次
        if step % 100 == 0:
            batch_x_test, batch_y_test = get_batch(BATCH_SIZE)
            acc = sess.run(accuracy, feed_dict={x: batch_x_test, y: batch_y_test, keep_prob: 1.0})
            print(datetime.now().strftime('%c'), ' step:', step, ' accuracy:', acc)
            # 准确率满足要求，保存模型
            if acc > acc_rate:
                saver.save(sess, model_path, global_step=step)
                acc_rate = acc
                if acc_rate > 0.80:  # 准确率达到95%则退出
                    break
        step += 1
    sess.close()


if __name__ == '__main__':
    train()

