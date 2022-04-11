# Running the script
You can run the script by providing the dataset folder (with `-d`) and the group you are working on (with `-g`).
An example with group 13 (with a fake path)
```
python prepare_for_gt_blender.py -d '/home/.../Datasets/RePAIR_dataset' -g 13
```

## Help with the commands
If you need help with parameters, run
```
python prepare_for_gt_blender.py -h
```
which will print the help, that should looks something like this:
```
usage: prepare_for_gt_blender.py [-h] [-m METHOD] [-d DATASET_FOLDER] [-g GROUP] [-o OUTPUT_FOLDER] [-v]

Preparing the fragments for manual ground truth: moving them to origin and aligning them with the flat surface facing up. It
is suggested to use the `open3d` method for central (flat) pieces and `vedo` method for edge (bulky) pieces.

optional arguments:
  -h, --help            show this help message and exit
  -m METHOD, --method METHOD
                        method to rotate the pcl. "open3d" segment the largest plane and align that, "vedo" aligns based on
                        pca ellipsoid of the fragment
  -d DATASET_FOLDER, --dataset_folder DATASET_FOLDER
                        root folder of the dataset. Here the absolute path should be used
  -g GROUP, --group GROUP
                        group number. it will be appended to the root path (after `processed` to find the correct group
                        folder)
  -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                        name of the folder where to save files (appended to the root folder)
  -v, --visualize       show pointclouds (original and rotated)
```
