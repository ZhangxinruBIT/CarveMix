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


def get_distance(f,spacing):
    """Return the signed distance."""

    dist_func = ndimage.distance_transform_edt
    distance = np.where(f, -(dist_func(f,sampling=spacing)-np.ones_like(f)),
                        dist_func(1-f,sampling=spacing)-np.ones_like(f))

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

class ShowProcess():
    """
    shows the progress of the processing
    """
    i = 0 
    max_steps = 0 
    max_arrow = 50 
    infoDone = 'done'

    # initialize
    def __init__(self, max_steps, infoDone = 'Done'):
        self.max_steps = max_steps
        self.i = 0
        self.infoDone = infoDone

    # display
    # exg[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]100.00%
    def show_process(self, i=None):
        if i is not None:
            self.i = i
        else:
            self.i += 1
        num_arrow = int(self.i * self.max_arrow / self.max_steps) 
        num_line = self.max_arrow - num_arrow 
        percent = self.i * 100.0 / self.max_steps 
        process_bar = '[' + '>' * num_arrow + '-' * num_line + ']'\
                      + '%.2f' % percent + '%' + '\r' 
        sys.stdout.write(process_bar) 
        sys.stdout.flush()
        if self.i >= self.max_steps:
            self.close()

    def close(self):
        print('')
        print(self.infoDone)
        self.i = 0
        
        

if __name__ == '__main__':
    
    # imagesTr_path = ''
    # labelsTr_path = ''
    # mask_check_path = ''
    print('=====================================================')
    print('======Edited by Xinru Zhang, offline CarveMix========')
    print('=====================================================')
    imagesTr_path = input('imagesTr_path: ') + '/'
    labelsTr_path = input('labelsTr_path: ') + '/'
    mask_check_path = input('mask_path: ')   + '/'
    mixid_csv_path = input(' mixid_csv_path: ') + '/''CarveMixID.csv'
    generate_number = input(' number of samples you want to creat: ')
    Cases = os.listdir(labelsTr_path)
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
    print(val_set)
    tr_set = list(set(Cases) - set(val_set))
    Cases = tr_set 
    print('====================================')
    print('=Only select train_set for CarveMix=')
    print('============val_set_not=============')
    print('==========tr_set_size:%d============'%len(Cases))
    print('====================================')
    
    
    with open(mixid_csv_path,'w') as f:
        f.write('id,mixid1,mixid2,lam\n') 
    
    """
    Start generating CarveMix samples
    """
    process_bar = ShowProcess(generate_number, 'CarveMix done')
    for i in range(generate_number):
        rand_index_a = random.randint(0,len(Cases)-1)
        rand_index_b = random.randint(0,len(Cases)-1)
        
        image_a = imagesTr_path + Cases[rand_index_a] + '_0000.nii.gz'
        label_a = labelsTr_path + Cases[rand_index_a] + '.nii.gz'
        image_b = imagesTr_path + Cases[rand_index_b] + '_0000.nii.gz'
        label_b = labelsTr_path + Cases[rand_index_b] + '.nii.gz'
    
        new_target, new_label, mask, c = generate_new_sample(image_a,image_b,label_a,label_b)
        
        s = str(i)
        sitk.WriteImage(new_target, imagesTr_path + prefix +'CarveMix_' + s + '_0000.nii.gz')
        sitk.WriteImage(new_label, labelsTr_path + prefix +'CarveMix_' + s + '.nii.gz')
        if i%100==0:
            sitk.WriteImage(mask, mask_check_path+ 'mask'+ 'CarveMix_mask'+ s + '.nii.gz')
            
        csv_string = s + ',' + str(Cases[rand_index_a]) + ',' + str(Cases[rand_index_b]) +','+str(c)+ '\n'
        with open(mixid_csv_path,'a') as f:
            f.write(csv_string)         
        
        process_bar.show_process()
    
    