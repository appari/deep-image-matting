#!/usr/bin/env python
# coding: utf-8

# ### Packages

# In[1]:


import torch
import torch.nn as nn
import math
import cv2
import torch.nn.functional as F


# ### Encoder Decoder Network

# In[2]:


class EDNet(nn.Module):
    def __init__(self):
        super(EDNet, self).__init__()
        
        # Encoder layers
        self.conv1_1 = nn.Conv2d(4, 64, kernel_size=3,stride = 1, padding=1,bias=True)
        self.conv1_2 = nn.Conv2d(64, 64, kernel_size=3,stride = 1, padding=1,bias=True)
        self.conv2_1 = nn.Conv2d(64, 128, kernel_size=3, padding=1,bias=True)
        self.conv2_2 = nn.Conv2d(128, 128, kernel_size=3, padding=1,bias=True)
        self.conv3_1 = nn.Conv2d(128, 256, kernel_size=3, padding=1,bias=True)
        self.conv3_2 = nn.Conv2d(256, 256, kernel_size=3, padding=1,bias=True)
        self.conv3_3 = nn.Conv2d(256, 256, kernel_size=3, padding=1,bias=True)
        self.conv4_1 = nn.Conv2d(256, 512, kernel_size=3, padding=1,bias=True)
        self.conv4_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1,bias=True)
        self.conv4_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1,bias=True)
        self.conv5_1 = nn.Conv2d(512, 512, kernel_size=3, padding=1,bias=True)
        self.conv5_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1,bias=True)
        self.conv5_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1,bias=True)
        self.conv6_1 = nn.Conv2d(512, 512, kernel_size=1, padding=0,bias=True)
        
        # Decoder layers
        self.deconv6_1 = nn.Conv2d(512, 512, kernel_size=1,bias=True)
        self.deconv5_1 = nn.Conv2d(512, 512, kernel_size=5, padding=2,bias=True)
        self.deconv4_1 = nn.Conv2d(512, 256, kernel_size=5, padding=2,bias=True)
        self.deconv3_1 = nn.Conv2d(256, 128, kernel_size=5, padding=2,bias=True)
        self.deconv2_1 = nn.Conv2d(128, 64, kernel_size=5, padding=2,bias=True)
        self.deconv1_1 = nn.Conv2d(64, 64, kernel_size=5, padding=2,bias=True)
        
        # Alpha prediction layer
        self.deconv1 = nn.Conv2d(64, 1, kernel_size=5, padding=2,bias=True)
        
    def forward(self, x):
        # Stage 1
        x11 = F.relu(self.conv1_1(x))
        x12 = F.relu(self.conv1_2(x11))
        x1p, id1 = F.max_pool2d(x12,kernel_size=(2,2), stride=(2,2),return_indices=True)

        # Stage 2
        x21 = F.relu(self.conv2_1(x1p))
        x22 = F.relu(self.conv2_2(x21))
        x2p, id2 = F.max_pool2d(x22,kernel_size=(2,2), stride=(2,2),return_indices=True)

        # Stage 3
        x31 = F.relu(self.conv3_1(x2p))
        x32 = F.relu(self.conv3_2(x31))
        x33 = F.relu(self.conv3_3(x32))
        x3p, id3 = F.max_pool2d(x33,kernel_size=(2,2), stride=(2,2),return_indices=True)

        # Stage 4
        x41 = F.relu(self.conv4_1(x3p))
        x42 = F.relu(self.conv4_2(x41))
        x43 = F.relu(self.conv4_3(x42))
        x4p, id4 = F.max_pool2d(x43,kernel_size=(2,2), stride=(2,2),return_indices=True)

        # Stage 5
        x51 = F.relu(self.conv5_1(x4p))
        x52 = F.relu(self.conv5_2(x51))
        x53 = F.relu(self.conv5_3(x52))
        x5p, id5 = F.max_pool2d(x53,kernel_size=(2,2), stride=(2,2),return_indices=True)

        # Stage 6
        x61 = F.relu(self.conv6_1(x5p))

        # Stage 1d
        x61d = F.relu(self.deconv6_1(x61))

        # Stage 2d
        x5d = F.max_unpool2d(x61d,id5, kernel_size=2, stride=2)
        x51d = F.relu(self.deconv5_1(x5d))

        # Stage 3d
        x4d = F.max_unpool2d(x51d, id4, kernel_size=2, stride=2)
        x41d = F.relu(self.deconv4_1(x4d))

        # Stage 4d
        x3d = F.max_unpool2d(x41d, id3, kernel_size=2, stride=2)
        x31d = F.relu(self.deconv3_1(x3d))

        # Stage 5d
        x2d = F.max_unpool2d(x31d, id2, kernel_size=2, stride=2)
        x21d = F.relu(self.deconv2_1(x2d))

        # Stage 6d
        x1d = F.max_unpool2d(x21d, id1, kernel_size=2, stride=2)
        x12d = F.relu(self.deconv1_1(x1d))

        raw_alpha = self.deconv1(x12d)
        pred_mattes = torch.sigmoid(raw_alpha)
        
        return pred_mattes


# In[7]:


def get_model():
    model = EDNet()
    model.apply(intialize_weights)
    return model


# ### Using Xavier intialization for weights

# In[4]:


def intialize_weights(m):
    if isinstance(m, nn.Conv2d):
        torch.nn.init.xavier_normal_(m.weight.data)
    elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()


# ### Model example

# In[8]:


get_model()

