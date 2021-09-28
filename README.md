# CarveMix
CarveMix: A Simple Data Augmentation Method for Brain Lesion Segmentation

CarveMix stochastically combines two existing labeled images to generate new labeled samples. where the combination is performed with an attention on the lesions and a proper annotation is created for the generated image. Specifically, from one labeled image we carve a region of interest (ROI) according to the lesion location and geometry, and
the size of the ROI is sampled from a probability distribution. The carved ROI then replaces the corresponding voxels in a second labeled image, and the annotation of the second image is replaced accordingly as well.

Fig.1 below is a set of image generation examples
![image](https://github.com/ZhangxinruBIT/CarveMix/blob/main/readme_Img/carve.png)

For more information about CarveMix, please read the following paper:


      Xinru Zhang, Chenghao Liu, Ni Ou, Xiangzhu Zeng, Xiaoliang Xiong, Yizhou Yu, Zhiwen Liu, Chuyang Ye,
      "CarveMix: A Simple Data Augmentation Method for Brain Lesion Segmentation". Medical Image Computing
      and Computer Assisted Intervention(MICCAI),2021.
      


Please also cite this paper if you are using CarveMix for your research!


      @InProceedings{10.1007/978-3-030-87193-2_19,
      author="Zhang, Xinru
      and Liu, Chenghao
      and Ou, Ni
      and Zeng, Xiangzhu
      and Xiong, Xiaoliang
      and Yu, Yizhou
      and Liu, Zhiwen
      and Ye, Chuyang",
      title="CarveMix: A Simple Data Augmentation Method for Brain Lesion Segmentation",
      booktitle="Medical Image Computing and Computer Assisted Intervention -- MICCAI 2021",
      year="2021",
      publisher="Springer International Publishing",
      address="Cham",
      pages="196--205",
      isbn="978-3-030-87193-2"
      }
      

# Installation
```
git clone https://github.com/ZhangxinruBIT/CarveMix.git
pip install -r requirements.txt
```
# Usage
**CarveMix augmentation method is agnostic to the network structure**

we selected the nnU-Net as it has consistently achieved the state-of-the-art performance in a variety of medical image segmentation tasks. Even the data format and naming can be referenced in the nnU-Net example (see [nnU-Net](https://github.com/MIC-DKFZ/nnUNet.git)).

Note that you need to determine the data partition beforehand, especially for training sets and validation sets, because validation sets do not participate in CarveMix. If you are using the nnU-Net framework,You need  divide themselves at **nnunet.training.net work_training.nnUNetTrainerV2.do_split()**, you can distinguish by the presence of 'CarveMix' in the name.

We just provide a simple demo data file named "Task100_ATLASwithCarveMix" which contains 3 subjects of ATLAS dataet. It is important to note that the demo data schema is single-label single-mode. 

**And multi-modes such as the BraTS dataset can be modified based on "Simple_CarveMix.py" as you need, even make sure if you need intensity normalization for heterogeneous data.**

**First, prepare task folder**, the following structure is expected:

    CarveMix/Task100_ATLASwithCarveMix/
    ├── Simple_CarveMix.py
    ├── imagesTr
    │   ├── ATLAS_001_0000.nii.gz
    │   ├── ATLAS_002_0000.nii.gz
    │   ├── ATLAS_003_0000.nii.gz
    │   ├── ...
    ├── mask
    └── labelsTr
    │   ├── ATLAS_001.nii.gz
    │   ├── ATLAS_002.nii.gz
    │   ├── ATLAS_003.nii.gz
    │   ├── ...
    
 "mask" is folder to save <img src="http://latex.codecogs.com/gif.latex?M_i" height=10/> as Fig.1 shows, but not for training, it's optional. 
 **Second,  run Simple_CarveMix.py**, you need to specify several path interfaces and generate_number you want. To run the demo:

    cd Task100_ATLASwithCarveMix/
    python Simple_CarveMix.py -num 5
 
 
The name of the newly generated image will include the 'Carvemix', the specific information of each generated image is in "CarveMixID.csv".

Because this is the offline version of the data augmentation(currently targeting brain lesions), completely independent of the network architecture and framework, you can continue to complete training and other operations based on this data. We recommend the nnU-Net framework, and experiments show that our data augmentation approach has a stacking effect on improvement overlap with the traditional data augmentation(**nnunet.training.data_augmentation.default_data_augmentation.get_moreDA_augmentation()**) set in the nnU-Net.

# Notes
A  preliminary  conference  version  of  this  work  has  been  accepted  by  MICCAI2021 (Zhang et al., 2021)(see [Zhang et al.](https://arxiv.org/abs/2108.06883)) which corresponds to Simple_CarveMix.py in demo **Task100_ATLASwithCarveMix.** 

Compared with the conference version,  we have extended CarveMix so that it can be better applied to heterogeneous data acquired at different sites with possibly different appearances or with the multi-modes. Here, we also give a demo **Task101_heterogeneous_data**  to test.
    

