目的：缩小当前yolov5s模型大小，提升检测速度

可供开源方案

- 方案一：先稀疏训练，然后以darknet版本网络进行剪枝，可参考https://github.com/tanluren/yolov3-channel-and-layer-pruning
- 方案二：替换backbone后重新训练，经过稀疏训练后，再进行剪枝和蒸馏，可参考https://github.com/Syencil/mobile-yolov5-pruning-distillation

---

方案一：

#### 1.基础训练

使用yolov5s训练自己数据集，满足精度要求

#### 2.稀疏训练

参考论文《Learning Efficient Convolutional Networks through Network Slimming》，在BN层引入缩放因子（稀疏度），缩放因子与通道相乘，接着进行联合训练，经过正则化后的缩放因子随着网络训练逐渐趋于0。目的是防止后续剪枝导致精度骤降。稀疏训练就是精度和稀疏度的博弈过程，根据稀疏度的衰减模式提供三种稀疏策略。

具体操作，将pt模型转换为Darknet的weights格式，以去掉其中的epoch信息。设定稀疏策略进行稀疏训练。

#### 3.剪枝（3种剪枝策略）

##### 3-1 不对shortcut直连的层进行剪枝

##### 3-2 对shortcut层也进行了剪枝，以及每组shortcut中第一个卷积层的mask

##### 3-3 先以全局阈值找出各卷积层的mask，然后对于每组shortcut，它将相连的各卷积层的剪枝mask取并集，用merge后的mask进行剪枝

###### 4.蒸馏（可选）  --网络知识迁移，恢复精度

小结：该方案通过稀疏训练后借助darknet格式权重完成剪枝，并且提供yolov5_v4.0剪枝示例。

---

方案二：

#### 1.基础训练

mobilev2替换原有backbone，重新训练

#### 2.稀疏训练

正则化采用L1范数，设置稀疏率训练。

#### 3.剪枝及微调（层剪枝）

统计所有参与剪枝层的bn参数l1值并进行排序，依据稀疏率确定阈值。将所有小于阈值的层全部减掉，如果有依赖则将依赖的对应部分也剪掉。如果一层中所有的层都需要被移除，那么就保留最大的一层通道(保证网络结构)，得到Student模型。

#### 4.蒸馏（3种蒸馏策略）  --恢复精度

训练Teacher网络，将T网络模型学习到的知识迁移到Student模型中

##### 4-1 Teacher网络采用基于darknet为backbone的yolo5s

##### 4-2 Teacher网络采用基于darknet为backbone的yolo5l

小结：该方案通过替换backbone实现模型精简，经过剪枝的模型精度进一步下降，因此需要通过蒸馏方可恢复原来精度。

---