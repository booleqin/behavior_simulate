# 基于CNN的图形验证码识别
## 环境

captcha: 0.3

numpy: 1.14.3

Pillow: 5.1.0

tensorflow: 1.9.0

## 运行

生成验证码
python gen_captcha.py

识别验证码
python cnn_model_train.py

    Wed May  1 10:58:39 2019  step: 0  accuracy: 0.10546875
    Wed May  1 11:06:23 2019  step: 100  accuracy: 0.13854763
    Wed May  1 11:13:32 2019  step: 200  accuracy: 0.12539845

## 结果保存

生成的验证码保存在codeimg中

训练完成的结果保存在model中

## 示例

生成验证码图片如下
![avatar](./codeimg/0001.png =180x40)


