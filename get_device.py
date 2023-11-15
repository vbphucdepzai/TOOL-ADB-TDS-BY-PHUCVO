import subprocess
import numpy as np
import os 
import time 
import random 
import pyotp
from datetime import datetime
import time 
from PIL import Image

#get_device
device= input('Nhap ma thiet bi muon chay : ')
#Follow
button ={}
button['follow'] = Image.open('image/fl1.png')
#Click 
def click(device, x, y) :
    subprocess.call(f'adb.exe -s {device} shell input tap {x} {y} ', shell=True)
#Find Image 
def find_image(im, tpl):
    im =np.atleast_3d(im)
    tpl = np.atleast_3d(tpl)
    H, W, D = im.shape[:3]
    h ,w = tpl.shape[:2]

    sat = im.cumsum(1).cumsum(0)
    tplsum =np.array([tpl[:, :, i].sum() for i in range(D)])
    iA,iB,iC,iD = sat[:-h, :-w], sat[:-h, w:], sat[h: , :-w], sat[h:, w:]
    lookup = iD - iB - iC + iA
    possible_match = np.where(np.logical_and.reduce([lookup[..., i] == tplsum[i] for i in range(D)]))
    for y,x in zip(*possible_match) :
        if np.all(im[y+1:y+h+1, x+1:x+w+1] == tpl):
            return(x+1,y+1)
    return(-1,-1)
#Search position
def search_position(device, action):

    
    subprocess.call('scrcpy\\adb.exe -s '+device+' shell screencap -p /sdcard/screen.png', shell=True)
    subprocess.call('scrcpy\\adb.exe -s '+device+' pull /sdcard/screen.png image/screen.png', shell=True)
    subprocess.call('scrcpy\\adb.exe -s '+device+' shell rm /sdcard/screen.png', shell=True)

    img = button[action]
    template = Image.open('image/screen.png')
    print(template)
    position = find_image(template, img)
    return position

#Auto Follow
position = search_position(device, 'follow')
print(position)
click(device, 507, 461)
