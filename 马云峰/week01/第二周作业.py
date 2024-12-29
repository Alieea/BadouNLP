import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 定义一个简单的神经网络模型
class TorchModel(nn.Module):
    def __init__(self, input_size, num_classes):
        super(TorchModel, self).__init__()
        self.linear = nn.Linear(input_size, num_classes)  # 线性层
        #self.softmax = nn.Softmax(dim=1)  # Softmax激活函数
        self.loss = nn.CrossEntropyLoss()  # 交叉熵损失函数

    def forward(self, x, y=None):
        x = self.linear(x)  # (batch_size, input_size) -> (batch_size, num_classes)
        #y_pred = self.softmax(x)  # (batch_size, num_classes) -> (batch_size, num_classes)
        if y is not None:
            return self.loss(x, y)  # 返回预测值和真实标签的损失
        return x  # 输出预测结果

# 生成一个样本，这是我们要学习的规律
def build_sample():
    x = np.random.rand(5)
    label = np.argmax(x)  # 最大值所在的维度作为类别标签
    return x, label

# 随机生成一批样本
def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(X), torch.LongTensor(Y)

# 测试代码，用来测试每轮模型的准确率
def evaluate(model):
    test_sample_num = 100
    x, y = build_dataset(test_sample_num)
    print("本次预测集中共有%d个正样本，%d个负样本" % (sum(y), test_sample_num - sum(y)))
    model.eval()  # 设置模型为评估模式
    with torch.no_grad():
        y_pred = model(x)  # 模型预测 forward(x).model
    correct, wrong = 0, 0
    for y_p, y_t in zip(torch.argmax(y_pred, dim=1), y):
        if y_p == y_t:
            correct += 1  # 判断正确
        else:
            wrong += 1
    print("正确预测个数：%d，正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)

# 主函数
def main():
    epoch_num = 20  # 训练轮数
    batch_size = 20  # 每次训练样本个数
    train_sample = 5000  # 总共训练的样本总数
    input_size = 5  # 输入向量维度
    num_classes = 5  # 类别数量
    learning_rate = 0.01  # 学习率
    model = TorchModel(input_size, num_classes)
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    train_x, train_y = build_dataset(train_sample)
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size : (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size : (batch_index + 1) * batch_size]
            loss = model(x, y)  # 计算loss
            loss.backward()  # 计算梯度
            optim.step()  # 更新权重
            optim.zero_grad()  # 梯度归零
            watch_loss.append(loss.item())
        print("========第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "model.bin")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return

# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    num_classes = 5
    model = TorchModel(input_size, num_classes)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    model.eval()  # 设置为评估模式
    with torch.no_grad():  # 不计算梯度
        result = model.forward(torch.FloatTensor(input_vec))  # 模型预测
    for vec, res in zip(input_vec, result):
        print("输入：%s, 预测类别：%d, 概率值：%f" % (vec, torch.argmax(res).item(), torch.max(res).item()))  # 打印结果

if __name__ == "__main__":
    main()
    # test_vec = [[0.97889086,0.15229675,0.31082123,0.03504317,0.88920843],
    #             [0.74963533,0.5524256,0.95758807,0.95520434,0.84890681],
    #             [0.00797868,0.67482528,0.13625847,0.34675372,0.19871392],
    #             [0.09349776,0.59416669,0.92579291,0.41567412,0.1358894]]
    # predict("model.pt", test_vec)
