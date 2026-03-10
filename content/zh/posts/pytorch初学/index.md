---
title: Pytorch初学
date: 2026-03-10T16:18:00
categories: 技术探索
tags:
  - ai
---

PyTorch 官方教程60分钟入门：https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html

LeNet-5：最早的卷积神经网络之一，用于识别手写数字。

![](https://pytorch.org/tutorials/_static/img/mnist.png)

数据流从左到右依次是：

1、输入input：手写数字图片

2、C1（卷积）：用6个滤波器扫描图片，提取低级特征，比如边缘、线条。

> （滤波器移动一次就能采样一次，因此这里的尺寸就会因为垂直或者水平方向能采样多少次决定）

    以 C1 为例：输入 32×32，滤波器大小 5×5

-     滤波器水平方向能够移动多少次：32-5+1=28次
-     滤波器垂直方向能够移动多少次：32-5+1=28次
-     因此输出是28x28

3、S2（下采样/池化）：只保留关键信息，缩小尺寸。

> 把刚才的C1输出再次缩小，LeNet-5使用2x2的池化窗口，步长为2，意味着每2x2的区域会取这个区域中的一个值，例如最大值来代表这个区域。

    28x28 -- 2x2

    28/2=14

    输出尺寸：14x14

4、C3（卷积）：用16个滤波器扫描S2的内容，提取特征的组合，比如拐角、弧线。

5、S4（下采样/池化）：再次缩小

6、F5（全连接）：把所有特征拉平，综合判断。

> 400x120，120中的每一个都吸收了400，只是权重不同。120这个数字可以被修改，它决定了这一层能学到多少种特征组合。

    比如：w1x1+w2x2+...w400x400

7、F6（全连接）：进一步提炼特征组合。84个。

8、输出(全连接)：10个类别，最大数值的就是预测结果。

pytorch给的代码，可以对应上刚才的输入到输出各个层级：

```plain
class LeNet(nn.Module):
    def __init__(self):

        super(LeNet, self).__init__()

        # 1 input image channel (black & white), 6 output channels, 5x5 square convolution

        # kernel

        self.conv1 = nn.Conv2d(1, 6, 5)

        self.conv2 = nn.Conv2d(6, 16, 5)

        # an affine operation: y = Wx + b

        self.fc1 = nn.Linear(16 * 5 * 5, 120)  # 5*5 from image dimension

        self.fc2 = nn.Linear(120, 84)

        self.fc3 = nn.Linear(84, 10)



    def forward(self, x):

        # Max pooling over a (2, 2) window

        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))

        # If the size is a square you can only specify a single number

        x = F.max_pool2d(F.relu(self.conv2(x)), 2)

        x = x.view(-1, self.num_flat_features(x))

        x = F.relu(self.fc1(x))

        x = F.relu(self.fc2(x))

        x = self.fc3(x)

        return x



    def num_flat_features(self, x):

        size = x.size()[1:]  # all dimensions except the batch dimension

        num_features = 1

        for s in size:

            num_features *= s

        return num_features
```

## Pytorch模型的基本结构

1、继承自torch.nn.module：提供了训练所需的基础功能，例如参数管理、GPU转移等功能。

2、__init__() 方法：在这里定义各个层。

```plain
    def __init__(self):
        self.conv1 = Conv2d(...)
        self.fc1 = Linear(...)
```

3、forward() 方法：在这里定义数据怎么流过这些层。

```plain
def forward(self, x):
    x = self.conv1(x)    # 输入先过卷积
    x = self.fc1(x)      # 再过全连接
    return x              # 输出结果
```

上面的代码有些许不同，引入一个F.relu()方法，目的是引入非线性计算，relu可以把负数变成0，正数不变。

激活函数：引入非线性运算，让网络能学到复杂的模式。

激活函数举例：

            ReLU:       负数→0，正数不变        最常用，简单快速

```plain
       ____/
```

            Sigmoid:    压缩到 0\~1 之间         用于输出概率

```plain
       __/‾‾
```

            Tanh:       压缩到 -1\~1 之间        比 sigmoid 中心对称

```plain
        __/‾‾
```

            Leaky ReLU: 负数→很小的值（不是0）   解决 ReLU "神经元死亡"问题

```plain
	 ___/
	/ 
```
