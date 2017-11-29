import torch, random
import torchvision.transforms as transforms
from torch.autograd import Variable
import torch.nn as nn
import torch.utils.data as data
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
import torchvision.models as models
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import torch.nn.functional as F
from tqdm import tqdm_notebook as tqdm
import os as os
import os.path
from PIL import Image
import json, string

import PIL, torch
from PIL import Image
import numpy as np
import IPython.display
from io import BytesIO
import torchvision.transforms as transforms

import sys # for command line 
from sys import argv

class UnNormalize(object):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std
    def __call__(self, tensor):
        for t, m, s in zip(tensor, self.mean, self.std):
            t.mul_(s).add_(m)
        return tensor
    
def pil2tensor(img):
    return transforms.ToTensor()(img)

def tensor2pil(tensor):
    return transforms.ToPILImage()(tensor)

def show_image(input_image):
    f = BytesIO()
    if type(input_image) == torch.Tensor:
        input_image = np.uint8(input_image.mul(255).numpy().transpose(1, 2, 0)) 
        Image.fromarray(input_image).save(f, 'png')
    else:
        input_image.save(f, 'png')
    IPython.display.display(IPython.display.Image(data = f.getvalue()))

def family_index():
    with open("./aircraft/data/families.txt") as f:
        dat = f.readlines()
    for i in range(len(dat)):
        dat[i] = dat[i].replace('\n','')
    return dat

def manufacturer_index():
    with open("./aircraft/data/manufacturers.txt") as f:
        dat = f.readlines()
    for i in range(len(dat)):
        dat[i] = dat[i].replace('\n','')
    return dat

# from PyTorch GitHub:  https://github.com/pytorch/vision/issues/81  

def default_loader(path):
    return Image.open(path).convert('RGB')

def default_flist_reader(flist):
    imlist = []
    fams = family_index()
    mfctrs = manufacturer_index()
    with open(flist, 'r') as rf:
        for line in rf.readlines():
            impath, imlabel = line.strip().split()
            imlist.append( ((''.join([impath,'.jpg'])), fams.index(imlabel)) )
    return imlist

class ImageFilelist(data.Dataset):
    def __init__(self, root, flist, transform=None, target_transform=None, 
                 flist_reader=default_flist_reader, loader=default_loader):
        self.root   = root
        self.imlist = flist_reader(flist)
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader

    def __getitem__(self, index):
        impath, target = self.imlist[index]
        img = self.loader(os.path.join(self.root,impath))
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return img, target

    def __len__(self):
        return len(self.imlist)

def manual_classification(*args):
    # saved network
    network = torch.load('resnet50_rescale.pth', map_location=lambda storage, loc: storage)

    # network eval
    network.eval()

    # class names
    classes = family_index()

    # image from the internet (simulating a user-provided photo)
    image = Image.open(*args).convert('RGB')
    preprocessFn = transforms.Compose([transforms.Scale((256,256)), 
                                   transforms.CenterCrop(224), 
                                   transforms.ToTensor()])
    inputVar = Variable(preprocessFn(image).unsqueeze(0))
    predictions = network(inputVar)

    # top N classes
    n = 5
    probs, indices = (-F.softmax(predictions)).data.sort()
    probs = (-probs).numpy()[0][:n]; indices = indices.numpy()[0][:n]
    for (prob, idx) in zip(probs, indices):
        print({"idx": idx, "classification": classes[idx], "probability": '%.3f' % prob })

    # 5. Show image and predictions

if __name__ == "__main__":
    manual_classification(*argv[1:])
