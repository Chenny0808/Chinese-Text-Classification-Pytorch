# coding: UTF-8
import time
import torch
import numpy as np
from train_eval import train, init_network
from importlib import import_module

import os


def visualize(event_dir, port):
    """可视化训练过程"""
    url = 'http://localhost:' + str(port)
    os.system('tensorboard --logdir %s --port %s && xdg-open %s' % (event_dir, port))
    os.system('xdg-open %s' % url)

if __name__ == '__main__':
    dataset = 'THUCNews'  # 数据集
    model = 'TextCNN'
    embedding = 'embedding_SougouNews.npz'
    word = False
    # 搜狗新闻:embedding_SougouNews.npz, 腾讯:embedding_Tencent.npz, 随机初始化:random
    if embedding == 'random':
        embedding = 'random'
    model_name = model  # 'TextRCNN'  # TextCNN, TextRNN, FastText, TextRCNN, TextRNN_Att, DPCNN, Transformer
    if model_name == 'FastText':
        from utils_fasttext import build_dataset, build_iterator, get_time_dif

        embedding = 'random'
    else:
        from utils import build_dataset, build_iterator, get_time_dif

    x = import_module('models.' + model_name)
    config = x.Config(dataset, embedding)  # 模型超参数配置
    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed_all(1)
    torch.backends.cudnn.deterministic = True  # 保证每次结果一样

    start_time = time.time()
    print("Loading data...")
    vocab, train_data, dev_data, test_data = build_dataset(config, word)
    train_iter = build_iterator(train_data, config)
    dev_iter = build_iterator(dev_data, config)
    test_iter = build_iterator(test_data, config)
    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)

    # train
    config.n_vocab = len(vocab)
    model = x.Model(config).to(config.device)
    if model_name != 'Transformer':
        init_network(model)
    print(model.parameters)  # 打印模型参数
    train(config=config, model=model, train_iter=train_iter, dev_iter=dev_iter, test_iter=test_iter)
