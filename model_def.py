import torch
from torch import nn

class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc = nn.Linear(10, 2)  # Input: 10 features → Output: 2 classes

    def forward(self, x):
        return self.fc(x)
