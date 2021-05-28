# CarveMix
CarveMix: A Simple Data Augmentation Method for Brain Lesion Segmentation

CarveMix stochastically combines two existing labeled images to generate new labeled samples. where the combination is performed with an attention on the lesions and a proper annotation is created for the generated image. Specifically, from one labeled image we carve a rgion of interest (ROI) according to the lesion location and geometry, and
the size of the ROI is sampled from a probability distribution. The carved ROI then replaces the corresponding voxels in a second labeled image, and the annotation of the second image is replaced accordingly as well.

Fig.1 below is a set of image generation examples

![image](https://github.com/ZhangxinruBIT/CarveMix/blob/main/readme_Img/carve.png)

For more information about nnU-Net, please read the following paper:


      Zhang, Xinru.,(2021). CarveMix: A Simple Data Augmentation Method for Brain Lesion Segmentation. In: International Conference 
      on Medical Image Computing and Computer Assisted Intervention.

Please also cite this paper if you are using CarveMix for your research!
# Usage
**CarveMix augmentation method is agnostic to the network structure**
we selected the nnU-Net as it has consistently achieved the state-of-the-art performance in a variety of medical image segmentation tasks. Even thed ata format and naming can be referenced in the nnU-Net example (see [here](https://github.com/MIC-DKFZ/nnUNet.git)).
Note that you need to determine the data partition beforehand, especially for training sets and validation sets, because validation sets do not participate in CarveMix. If you are using the nnU-Net framework,You need  divide themselves at nnunet.training.net work_training. NnUNetTrainerV2. do_split data, you can distinguish by the presence of 'CarveMix' in the name.

**First you should prepare task folder**, the following structure is expected:

    /data4/xinruzhang/nnUNet/nnUNet_raw/nnUNet_raw_data/Task100_ATLASwithCarveMix/
    ├── dataset.json
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
    
 "mask" is folder to save Mi as Fig.1 shows, but not for training, it's optional. We provide a demo datafile named "Task100_ATLASwithCarveMix" which contains 3 subjects of ATLAS dataet.
 **Second, you can run CarveMix_uniform.py**, you need to specify several path interfaces and generate_number you want. Take the demo, for example:

    imagesTr_path = '/data4/xinruzhang/nnUNet/nnUNet_raw/nnUNet_raw_data/Task100_ATLASwithCarveMix/imagesTr'
    labelsTr_path = '/data4/xinruzhang/nnUNet/nnUNet_raw/nnUNet_raw_data/Task100_ATLASwithCarveMix/labelsTr'
    mask_check_path = '/data4/xinruzhang/nnUNet/nnUNet_raw/nnUNet_raw_data/Task100_ATLASwithCarveMix/mask'
    mixid_csv_path = '/data4/xinruzhang/nnUNet/nnUNet_raw/nnUNet_raw_data/Task100_ATLASwithCarveMix/'
    generate_number = 5
 
Then, your task file can look like this:
 <img align="left"  src="https://github.com/ZhangxinruBIT/CarveMix/blob/main/readme_Img/dirlistname.png">
 
 
The name of the newly generated image will include the 'Carvemix', the specific information of each generated image is in "CarveMixID.csv".
    
    

