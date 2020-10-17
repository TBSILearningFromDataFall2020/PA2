import numpy as np

import lfdnn
from lfdnn import operator

class MLP(lfdnn.Graph):
    '''
        epoch_num: int, number of epochs in traning
        batch_size: int, batch size used in SGD, default to all data
        input_dim: int, number of feature for each input data
        output_dim: int, number of classes for output label
        layer_num: int, number of intermediate layer
        hidden_layer_num: array-like, len(hidden_layer_num) = layer_num, the number of nodes at each hidden layer
        learning_rate: double, learning rate in SGD
        _lambda: double, regularization parameter
    '''
    def __init__(self, learning_rate=0.05, epoch_num=1, batch_size='auto', hidden_layer_sizes=(), _lambda=0):
        self.hidden_layer_sizes = hidden_layer_sizes
        self._lambda = _lambda
        super().__init__(learning_rate=learning_rate, epoch_num=epoch_num, batch_size=batch_size)

    def construct_model(self, x_train, y_train):
        # get number of features
        input_dim = x_train.shape[-1]
        # get number of classes
        output_dim = len(np.unique(y_train))
        layer_num = len(self.hidden_layer_sizes)
        hidden_layer_num = self.hidden_layer_sizes
        batch_size = self.batch_size
        _lambda = self._lambda
        if batch_size == 'auto':
            # use all data
            batch_size = x_train.shape[0]

        self.input = lfdnn.tensor([batch_size, input_dim], 'Input')
        self.label = lfdnn.tensor([batch_size, output_dim], 'Label')
        h = self.input
        for i in range(layer_num):
            if i == 0:
                w = lfdnn.tensor([input_dim, hidden_layer_num[i]], 'Weight' + str(i))
                self.weight['Weight' + str(i)] = w
            else:
                w = lfdnn.tensor([hidden_layer_num[i - 1], hidden_layer_num[i]], 'Weight' + str(i))
                self.weight['Weight' + str(i)] = w
            b = lfdnn.tensor([1, hidden_layer_num[i]],'Bias' + str(i))
            self.weight['Bias' + str(i)] = b
            h = operator.add(operator.matmul(h, w), b)
            h = operator.sigmoid(h)
        if len(hidden_layer_num) > 0:
            w = lfdnn.tensor([hidden_layer_num[-1], output_dim], 'output_weight')
        else:
            w = lfdnn.tensor([input_dim, output_dim], 'output_weight')
        self.weight['output_weight'] = w
        b = lfdnn.tensor([1, output_dim], 'output_bias')
        self.weight['output_bias'] = b
        h = operator.add(operator.matmul(h, w), b)
        self.output = operator.softmax(h)
        self.loss = operator.CE_with_logit(h, self.label)
        if _lambda > 0:
            for w in self.weight.values():
                regularization_term = operator.scale(operator.mean_square_sum(w), _lambda)
                self.loss = operator.add(self.loss, regularization_term)
        self.accuracy = operator.accuracy(self.output, self.label)
