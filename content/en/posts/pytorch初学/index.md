---
title: Learning PyTorch
date: 2026-03-10T16:18:00
categories: Tech & Projects
tags:
  - ai
---

PyTorch Official 60-Minute Blitz Tutorial: https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html

LeNet-5: One of the earliest convolutional neural networks, used for recognizing handwritten digits.

![](https://pytorch.org/tutorials/_static/img/mnist.png)

The data flow from left to right is as follows:

1. Input: Handwritten digit images

2. C1 (Convolution): Uses 6 filters to scan the image, extracting low-level features like edges and lines.

> (A sample is taken every time the filter moves, so the size here is determined by how many times sampling can occur in the vertical or horizontal direction.)

Taking C1 as an example: input 32×32, filter size 5×5

- Number of times the filter can move horizontally: 32-5+1=28 times
- Number of times the filter can move vertically: 32-5+1=28 times
- Therefore, the output is 28x28

3. S2 (Subsampling/Pooling): Retains only key information and reduces dimensions.

> Scaling down the C1 output again, LeNet-5 uses a 2x2 pooling window with a stride of 2, meaning it takes one value (e.g., the maximum value) from every 2x2 area to represent that area.

    28x28 -- 2x2

    28/2=14

    Output size: 14x14

4. C3 (Convolution): Uses 16 filters to scan the S2 content, extracting combinations of features such as corners and curves.

5. S4 (Subsampling/Pooling): Shrinks again

6. F5 (Fully Connected): Flattens all features for comprehensive judgment.

> 400x120, where each of the 120 nodes absorbs 400 inputs, just with different weights. This number 120 can be modified; it determines how many types of feature combinations this layer can learn.

    Example: w1x1+w2x2+...w400x400

7. F6 (Fully Connected): Further refines feature combinations. 84 nodes.

8. Output (Fully Connected): 10 categories; the one with the highest value is the prediction result.

The code provided by PyTorch corresponds to the input-to-output levels mentioned above:

```plain
class LeNet(nn.Module):
    def __init__(self):

        super(LeNet, self).__init__()

        # 1 input image channel (black & white), 6 output channels, 5x5 square convolution

        # kernel

        self.conv1 = nn.Conv2d(1, 6, 5)

        self.conv2 = nn.Conv2d(6, 16, 5)

        # an affine operation: y = Wx + b

        self.fc1 = nn.Linear(16 * 5 * 5, 120)  # 5*5 from image dimension

        self.fc2 = nn.Linear(120, 84)

        self.fc3 = nn.Linear(84, 10)



    def forward(self, x):

        # Max pooling over a (2, 2) window

        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))

        # If the size is a square you can only specify a single number

        x = F.max_pool2d(F.relu(self.conv2(x)), 2)

        x = x.view(-1, self.num_flat_features(x))

        # In the code above, F.relu() is introduced to add non-linear computation

        x = F.relu(self.fc1(x))

        x = F.relu(self.fc2(x))

        x = self.fc3(x)

        return x



    def num_flat_features(self, x):

        size = x.size()[1:]  # all dimensions except the batch dimension

        num_features = 1

        for s in size:

            num_features *= s

        return num_features
```

## Basic Structure of a PyTorch Model

1. Inherit from torch.nn.Module: Provides foundational functionality required for training, such as parameter management and GPU transfers.

2. __init__() method: Define various layers here.

```plain
    def __init__(self):
        self.conv1 = Conv2d(...)
        self.fc1 = Linear(...)
```

3. forward() method: Define how data flows through these layers here.

```plain
def forward(self, x):
    x = self.conv1(x)    # Input passes through convolution first
    x = self.fc1(x)      # Then passes through fully connected layer
    return x              # Output result
```

The code above is slightly different as it introduces an F.relu() method to incorporate non-linear computation. ReLU turns negative numbers into 0 while leaving positive numbers unchanged.

Activation Function: Introduces non-linear operations, allowing the network to learn complex patterns.

Examples of Activation Functions:

            ReLU: Negative numbers → 0, positive numbers remain unchanged. Most common, simple, and fast.

```plain
        ____/
```

            Sigmoid: Compresses values between 0 and 1. Used for outputting probabilities.

```plain
       __/‾‾
```

            Tanh: Compresses values between -1 and 1. More centrally symmetric than sigmoid.

```plain
         __/‾‾
```

            Leaky ReLU: Negative numbers → a very small value (not 0). Solves the ReLU "dying neuron" problem.

```plain
	 ___/
	/ 
```
