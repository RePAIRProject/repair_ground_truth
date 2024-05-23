import json, os
import cv2
import matplotlib.pyplot as plt 
import numpy as np 
import scipy.ndimage as ndi
import pandas as pd
import shutil
from os.path import exists

crate_image = True

canvas_shape = 14000
cc = canvas_shape // 2
img_size = 2000 
ihs = img_size // 2
pre_proc_scaling = 1/100    # i scaled the pieces 0.01 in align_face_up.py
ort_proj = 2.714            # blender orthographic projection scale    

visualize = False
save_solution_as_txt = True
#output_folder = 'gt_2d_txt'
output_folder = os.path.join(f'C:/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/gt_2d_txt')
os.makedirs(output_folder, exist_ok=True)

images_f = f'C:/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/images'
json_folder = f'C:/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/json_obj'
object_folder = f'C:/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/images_in_objects'
json_files = os.listdir(json_folder)
json_files.sort()
groups_nums = np.arange(len(json_files))

#groups_nums = np.arange(1, 3, 1)
groups_nums = np.arange(114, 115, 1)

#for j, group in enumerate([4]):
for j, group in enumerate(groups_nums):
    group_name = json_files[group]    # modify path accordingly!
    json_gt = os.path.join(json_folder, group_name)
    print(group_name)
    group_name.replace('.json', '')

    # json_gt = f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/json/group_{group}.json'
    # images_f = f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/images/group_{group}'
    # images_f = f'/media/lucap/big_data/datasets/repair/2DGT/group_{group}'
    # json_gt = f'/media/lucap/big_data/datasets/repair/ground_truth/gt_json/group_{group}.json'

    with open(json_gt, 'r') as jgt:
        gt = json.load(jgt)

    df = pd.DataFrame()
    solution = np.zeros((len(gt.keys()), 3))
    names = []
    names_full = []
    canvas = np.zeros((canvas_shape, canvas_shape, 4))
    k = 0
    for gtk in gt.keys():
        print(gtk)

        coords_px = np.asarray(gt[gtk]['location']) * img_size * pre_proc_scaling / ort_proj
        px = np.round(cc + coords_px[0]).astype(int)
        py = np.round(cc - coords_px[1]).astype(int)
        rot_angle = np.rad2deg(gt[gtk]['rotation_euler'][2])

        # image_moving part - NEW
        output_name = group_name.replace('.json', '')
        images_folder =  os.path.join(object_folder, output_name)
        os.makedirs(images_folder, exist_ok=True)
        file = os.path.join(images_f, f"{gtk}_intact_mesh.png")
        file_exists = exists(file)
        if file_exists:
            shutil.copy(file, images_folder)
        else:
            print(f"File {gtk} is missing")


        if crate_image == True:
            if file_exists:
                img = plt.imread(os.path.join(images_f, f"{gtk}_intact_mesh.png"))
                scaled_img = cv2.resize((img * 255).astype(np.uint8), (img_size, img_size))
                rotated_img = ndi.rotate(scaled_img, rot_angle, reshape=False)
                canvas[py - ihs:py + ihs, px - ihs:px + ihs, :] += rotated_img / 255

        solution[k, 0] = px
        solution[k, 1] = py
        solution[k, 2] = rot_angle
        k += 1
        gtk_full = (f"{gtk}_intact_mesh.png")
        names_full.append(gtk_full)
        names.append(gtk)

    if visualize == True:
        plt.subplot(1,3,j+1)
        plt.title(f"Group {group}")
        plt.imshow(canvas)

    output_name = group_name.replace('.json', '')

    if crate_image == True:
        final_solution = os.path.join(
            f'C:/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/final_img/{output_name}.png')
        # final_solution = os.path.join(f'C:/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/final_img/{group_name}.png')
        # final_solution = os.path.join(f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/final_img/group_{group}.png')
        plt.subplot(1, 3, j + 1)
        plt.title(f"Group {group}")
        plt.imsave(final_solution, (canvas * 255).astype(np.uint8))


    const_x = np.min(solution[:, 0])
    const_y = np.min(solution[:, 1])
    df['rpf'] = names_full
    df['x'] = solution[:, 0] - const_x
    df['y'] = solution[:, 1] - const_y
    df['rot'] = solution[:, 2]

    if save_solution_as_txt == True:
        df.to_csv(os.path.join(output_folder, f'{output_name}.txt'), index=False, index_label=False)
    else:
        print(solution)

if visualize == True:
    plt.show()
    plt.imsave()
