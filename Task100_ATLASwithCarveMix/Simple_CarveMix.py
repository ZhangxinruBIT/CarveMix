# -*- coding: utf-8 -*-
"""
Created on Thu May 27 15:17:22 2021

@author: 73239
"""


import numpy as np
from scipy.ndimage import gaussian_filter
import random
import os
import SimpleITK as sitk
import sys, time
import nibabel as nib
from scipy import ndimage
from tqdm import tqdm
import argparse
import os

def get_distance(f,spacing):
    """Return the signed distance."""

    dist_func = ndimage.distance_transform_edt
    distance = np.where(f, -(dist_func(f,sampling=spacing)),
                        dist_func(1-f,sampling=spacing))

    return distance


def get_head(img_path):
    
    temp = sitk.ReadImage(img_path)
    spacing = temp.GetSpacing()
    direction = temp.GetDirection()
    origin = temp.GetOrigin()
    
    return spacing,direction,origin

def copy_head_and_right_xyz(data,spacing,direction,origin):
    
    TrainData_new = data.astype('float32')
    TrainData_new = TrainData_new.transpose(2,1,0)
    TrainData_new = sitk.GetImageFromArray(TrainData_new)
    TrainData_new.SetSpacing(spacing)
    TrainData_new.SetOrigin(origin)
    TrainData_new.SetDirection(direction)
    
    return TrainData_new

"""
==========================================
The input must be nii.gz which contains 
import header information such as spacing.
Spacing will affect the generation of the
signed distance.
=========================================
"""
def generate_new_sample(image_a,image_b,label_a,label_b):
    spacing,direction,origin = get_head(image_a)
    
    target_a = nib.load(image_a).get_fdata()
    target_b = nib.load(image_b).get_fdata()
    label_a = nib.load(label_a).get_fdata()
    label_b = nib.load(label_b).get_fdata()
    label = np.copy(label_b)
    
    dis_array = get_distance(label,spacing)    #creat signed distance
    c = np.random.beta(1, 1)#[0,1]             #creat distance
    λl = np.min(dis_array)/2                   #λl = -1/2|min(dis_array)|
    λu = -np.min(dis_array)                    #λu = |min(dis_array)|
    lam = np.random.uniform(λl,λu,1)           #λ ~ U(λl,λu)
              
    mask = (dis_array<lam).astype('float32')   #creat M   
    
    new_target = target_a * (mask==0) + target_b * mask  
    new_label  = label_a  * (mask==0) + label_b  * mask  

    new_target = copy_head_and_right_xyz(new_target,spacing,direction,origin)
    new_label = copy_head_and_right_xyz(new_label,spacing,direction,origin)
    mask = copy_head_and_right_xyz(mask,spacing,direction,origin)
    
    return new_target, new_label, mask, lam

        
        

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("--generate_number","-num",default=5,type=int,
                       help="number of samples you want to creat: ")
    parse.add_argument("--imagesTr_path","-imgTr",default="imagesTr",type=str,
                       help="Path to raw images")
    parse.add_argument("--labelsTr_path","-labelTr",default="labelsTr",type=str,
                       help="Path to raw labels")
    parse.add_argument("--mask_check_path","-mask",default="mask",type=str,
                       help="Path to save masks generated by CarveMix")
    parse.add_argument("--mixid_csv_path","-csv",default="CarveMixID.csv",type=str,
                       help="Path to save csv file")
    opt = parse.parse_args()
    print('=====================================================')
    print('======Edited by Xinru Zhang, offline CarveMix========')
    print('=====================================================')
    if not os.path.exists(opt.mask_check_path):
        os.makedirs(opt.mask_check_path,exist_ok=True)
        
    Cases = os.listdir(opt.labelsTr_path)
    simpleCases = [case.split('.')[0] for i, case in enumerate(Cases) if 'Mix' not in case]
    Cases = simpleCases
    prefix = Cases[0].split('_')[0]

    """
    Prepare data split, note that validation sets do not participate in 
    CarveMix, and remember to split training sets and validation sets 
    independently in nnunet.training.network_training.nnUNetTrainerV2.do_split 
    when using nnUNet framework
    """
    num = len(Cases)
    print('all_set_size: ',num)
    Cases.sort()
    start = 1
    val_num = int(num*0.2)
    random.seed(985)
    val_id = random.sample(range(1,num-1),val_num)
    val_id.sort()
    val_set = [Cases[i-start] for i in val_id]
    print('val_set:',val_set)
    print('We use 20% num of imagesTr for validation,\n \
    if you are using demo data file, it will be null')
    tr_set = list(set(Cases) - set(val_set))
    Cases = tr_set 
    print('====================================')
    print('=Only select train_set for CarveMix=')
    print('============val_set_not=============')
    print('==========tr_set_size:%d============'%len(Cases))
    print('====================================')
    print(opt)
    
    with open(opt.mixid_csv_path,'w') as f:
        f.write('id,mixid1,mixid2,lam\n') 
    
    """
    Start generating CarveMix samples
    """
    for i in tqdm(range(opt.generate_number),desc="mixing:"):
        rand_index_a = random.randint(0,len(Cases)-1)
        rand_index_b = random.randint(0,len(Cases)-1)
        
        image_a = os.path.join(opt.imagesTr_path, Cases[rand_index_a] + '_0000.nii.gz')
        label_a = os.path.join(opt.labelsTr_path, Cases[rand_index_a] + '.nii.gz')
        image_b = os.path.join(opt.imagesTr_path, Cases[rand_index_b] + '_0000.nii.gz')
        label_b = os.path.join(opt.labelsTr_path, Cases[rand_index_b] + '.nii.gz')
    
        new_target, new_label, mask, c = generate_new_sample(image_a,image_b,label_a,label_b)
        
        s = str(i)
        sitk.WriteImage(new_target, os.path.join(opt.imagesTr_path, prefix +'_CarveMix_' + s + '_0000.nii.gz'))
        sitk.WriteImage(new_label, os.path.join(opt.labelsTr_path, prefix +'_CarveMix_' + s + '.nii.gz'))
        if i%100==0:
            sitk.WriteImage(mask, os.path.join(opt.mask_check_path, 'mask'+ '_CarveMix_mask'+ s + '.nii.gz'))
            
        csv_string = s + ',' + str(Cases[rand_index_a]) + ',' + str(Cases[rand_index_b]) +','+str(c)+ '\n'
        with open(opt.mixid_csv_path,'a') as f:
            f.write(csv_string)         

    
    
