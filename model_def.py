import torch
from torch import nn

class SimpleNet(nn.Module):
    """Legacy simple model - kept for backward compatibility"""
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc = nn.Linear(10, 2)  # Input: 10 features → Output: 2 classes

    def forward(self, x):
        return self.fc(x)


class MNISTNet(nn.Module):
    """Neural network for MNIST digit classification (28x28 grayscale images)"""
    def __init__(self):
        super(MNISTNet, self).__init__()
        self.fc1 = nn.Linear(784, 128)  # 28x28 = 784 input features
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)    # 10 digit classes (0-9)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = x.view(-1, 784)  # Flatten 28x28 images to 784
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x
