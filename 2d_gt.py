import json, os
import cv2
import matplotlib.pyplot as plt 
import numpy as np 
import scipy.ndimage as ndi
import pandas as pd 

canvas_shape = 11000
cc = canvas_shape // 2
img_size = 2000 
ihs = img_size // 2
pre_proc_scaling = 1/100    # i scaled the pieces 0.01 in align_face_up.py
ort_proj = 2.714            # blender orthographic projection scale    

visualize = False
save_solution_as_txt = True
output_folder = 'gt_2d_txt'
os.makedirs(output_folder, exist_ok=True)
#groups_nums = np.arange(1, 3, 1)
groups_nums = np.arange(38, 41, 1)

#for j, group in enumerate([4]):
for j, group in enumerate(groups_nums):
    # modify path accordingly!
    json_gt = f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/json/group_{group}.json'
    images_f = f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/images/group_{group}'

    # images_f = f'/media/lucap/big_data/datasets/repair/2DGT/group_{group}'
    # json_gt = f'/media/lucap/big_data/datasets/repair/ground_truth/gt_json/group_{group}.json'

    with open(json_gt, 'r') as jgt:
        gt = json.load(jgt)

    df = pd.DataFrame()
    solution = np.zeros((len(gt.keys()), 3))
    names = []
    canvas = np.zeros((canvas_shape, canvas_shape, 4))
    k = 0
    for gtk in gt.keys():
        print(gtk)
        img = plt.imread(os.path.join(images_f, f"{gtk}_intact_mesh.png"))
        scaled_img = cv2.resize((img * 255).astype(np.uint8), (img_size, img_size))
        rot_angle = np.rad2deg(gt[gtk]['rotation_euler'][2])
        rotated_img = ndi.rotate(scaled_img, rot_angle, reshape=False)
        coords_px = np.asarray(gt[gtk]['location']) * img_size * pre_proc_scaling / ort_proj
        px = np.round(cc + coords_px[0]).astype(int)
        py = np.round(cc - coords_px[1]).astype(int)
        canvas[py-ihs:py+ihs, px-ihs:px+ihs, :] += rotated_img / 255
        solution[k, 0] = px
        solution[k, 1] = py
        solution[k, 2] = rot_angle
        k += 1
        names.append(gtk)

    if visualize == True:
        plt.subplot(1,3,j+1)
        plt.title(f"Group {group}")
        plt.imshow(canvas)

    final_solution = os.path.join(f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/final_img/group_{group}.png')
    plt.subplot(1, 3, j + 1)
    plt.title(f"Group {group}")
    #plt.imshow((canvas * 255).astype(np.uint8))
    plt.imsave(final_solution, (canvas * 255).astype(np.uint8))

    df['rpf'] = names
    df['x'] = solution[:, 0]
    df['y'] = solution[:, 1]
    df['rot'] = solution[:, 2]

    if save_solution_as_txt == True:
        df.to_csv(os.path.join(output_folder, f'group_{group}.txt'))
    else:
        print(solution)

if visualize == True:
    plt.show()
    plt.imsave()
