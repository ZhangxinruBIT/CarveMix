# CarveMix
CarveMix: A Simple Data Augmentation Method for Brain Lesion Segmentation

CarveMix stochastically combines two existing labeled images to generate new labeled samples. where the combination is performed with an attention on the lesions and a proper annotation is created for the generated image. Specifically, from one labeled image we carve a rgion of interest (ROI) according to the lesion location and geometry, and
the size of the ROI is sampled from a probability distribution. The carved ROI then replaces the corresponding voxels in a second labeled image, and the annotation of the second image is replaced accordingly as well.
