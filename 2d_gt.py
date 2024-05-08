import json, os
import cv2
import matplotlib.pyplot as plt 
import numpy as np 
import scipy.ndimage as ndi

canvas_shape = 8000
cc = canvas_shape // 2
img_size = 2000 
ihs = img_size // 2
pre_proc_scaling = 1/100    # i scaled the pieces 0.01 in align_face_up.py
ort_proj = 2.714            # blender orthographic projection scale    

for j, group in enumerate([1, 13, 15]):
    json_gt = f'/media/lucap/big_data/datasets/repair/ground_truth/gt_json/group_{group}.json'
    images_f = f'/media/lucap/big_data/datasets/repair/2DGT/group_{group}'

    with open(json_gt, 'r') as jgt:
        gt = json.load(jgt)

    canvas = np.zeros((canvas_shape, canvas_shape, 4))
    for gtk in gt.keys():
        print(gtk)
        img = plt.imread(os.path.join(images_f, f"{gtk}_intact_mesh.png"))
        scaled_img = cv2.resize((img * 255).astype(np.uint8), (img_size, img_size))
        rot_angle = np.rad2deg(gt[gtk]['rotation_euler'][2])
        rotated_img = ndi.rotate(scaled_img, rot_angle, reshape=False)
        coords_px = np.asarray(gt[gtk]['location']) * img_size * pre_proc_scaling / ort_proj #* 2000 / 36 / ort_proj
        px = np.round(cc + coords_px[0]).astype(int)
        py = np.round(cc - coords_px[1]).astype(int)
        canvas[py-ihs:py+ihs, px-ihs:px+ihs, :] += rotated_img / 255

    plt.subplot(1,3,j+1)
    plt.title(f"Group {group}")
    plt.imshow(canvas)
plt.show()
breakpoint()