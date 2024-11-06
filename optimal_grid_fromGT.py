
import json, os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi
import pandas as pd


groups_nums = [1, 3, 39]  # DONE for RM
#groups_nums = [45, 51, 52, 53, 59, 37, 40, 47, 48, 54, 55] ## todo

xy_step = 3
xy_grid_points = 121

visualize = False
save_solution_as_txt = True

output_folder_px = 'gt_px251'
output_folder_grid = 'gt_grid3'
output_folder_PTS = 'opt_PTS'
output_folder_Fin_Im = 'final_img251'

os.makedirs(output_folder_px, exist_ok=True)
os.makedirs(output_folder_grid, exist_ok=True)
os.makedirs(output_folder_PTS, exist_ok=True)
os.makedirs(output_folder_Fin_Im, exist_ok=True)

img_size = 251
ihs = img_size // 2
pre_proc_scaling = 1/100    # i scaled the pieces 0.01 in align_face_up.py
ort_proj = 2.714            # blender orthographic projection scale

optimal_grid3 = np.zeros((len(groups_nums), 3))

for j, group in enumerate(groups_nums):
    # modify path accordingly!
    #json_gt = f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/json/group_{group}.json'
    #images_f = f'/home/marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/images/group_{group}'

    # CASA modify path accordingly!
    json_gt = f'/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/json_obj/RPobj_g{group}_o000{group}.json'
    images_f = f'/Users/Marina/PycharmProjects/repair_ground_truth/RePAIR_dataset/resize_images'

    # images_f = f'/media/lucap/big_data/datasets/repair/2DGT/group_{group}'
    # json_gt = f'/media/lucap/big_data/datasets/repair/ground_truth/gt_json/group_{group}.json'

    with open(json_gt, 'r') as jgt:
        gt = json.load(jgt)

    solution = np.zeros((len(gt.keys()), 3))
    names = []
    k = 0
    for gtk in gt.keys():
        print(gtk)
        coords_px = np.asarray(gt[gtk]['location']) * img_size * pre_proc_scaling / ort_proj
        cc = 0
        solution[k, 0] = np.round(cc+coords_px[0]).astype(int)  # px
        solution[k, 1] = np.round(cc-coords_px[1]).astype(int)  # py
        solution[k, 2] = np.mod(np.rad2deg(gt[gtk]['rotation_euler'][2]), 360) # rot_angle
        names.append(gtk)
        k += 1

    solution[:, 0] -= np.min(solution[:, 0])  # min_x
    solution[:, 1] -= np.min(solution[:, 1])  # min_y

    # GT_grtid for puzzle solving
    gt_on_grid = np.zeros_like(solution)
    gt_on_grid[:, 0] = (np.ceil(solution[:, 0] / xy_step)).astype(int)
    gt_on_grid[:, 1] = (np.ceil(solution[:, 1] / xy_step)).astype(int)
    gt_on_grid[:, 2] = solution[:, 2]

    pts_X = (np.max(gt_on_grid[:, 0]) + 10)   # xy_grid_points//10
    pts_Y = (np.max(gt_on_grid[:, 1]) + 10)

    optimal_grid3[j, 0] = group
    optimal_grid3[j, 1] = pts_X
    optimal_grid3[j, 2] = pts_Y

    ihs = img_size // 2
    solution[:, 0] += ihs+1
    solution[:, 1] += ihs+1
    canvas_shape_X = (np.max(solution[:, 0])+ihs+1).astype(int) ## +126
    canvas_shape_Y = (np.max(solution[:, 1])+ihs+1).astype(int)

    canvas = np.zeros((canvas_shape_Y, canvas_shape_X, 4))
    k = 0
    for gtk in gt.keys():
        print(gtk)
        img = plt.imread(os.path.join(images_f, f"{gtk}_intact_mesh.png"))
        scaled_img = cv2.resize((img * 255).astype(np.uint8), (img_size, img_size))

        px = (solution[k, 0]).astype(int)
        py = (solution[k, 1]).astype(int)
        rot_angle = solution[k, 2]

        rotated_img = ndi.rotate(scaled_img, rot_angle, reshape=False)
        canvas[py-ihs:py+ihs+1, px-ihs:px+ihs+1, :] += rotated_img / 255
        k += 1

    plt.imshow((canvas * 255).astype(np.uint8))
    plt.show()

    #final_solution = os.path.join(f'/home/marina/PycharmProjects/repair_ground_truth/final_img251/group_{group}.png')
    final_solution = os.path.join(output_folder_Fin_Im, f'group_{group}.png')
    plt.imsave(final_solution, (canvas * 255).astype(np.uint8))

    # save GT_pixelwise_251
    df = pd.DataFrame()
    df['rpf'] = names
    df['x'] = solution[:, 0]
    df['y'] = solution[:, 1]
    df['rot'] = solution[:, 2]
    if save_solution_as_txt == True:
        df.to_csv(os.path.join(output_folder_px, f'gt_px251_group_{group}.txt'))
    else:
        print(solution)

    # save GT_pixelwise_251
    df1 = pd.DataFrame()
    df1['rpf'] = names
    df1['x'] = gt_on_grid[:, 0]
    df1['y'] = gt_on_grid[:, 1]
    df1['rot'] = gt_on_grid[:, 2]
    if save_solution_as_txt == True:
        df1.to_csv(os.path.join(output_folder_grid, f'gt_grid3_group_{group}.txt'))
    else:
        print(gt_on_grid)

    # save optimal grid for xy_step3
    df2 = pd.DataFrame([pts_X.astype(int), pts_Y.astype(int)], index=["p_pts_x", "p_pts_y"], columns=["n_points"])
    if save_solution_as_txt == True:
        df2.to_csv(os.path.join(output_folder_PTS, f'optimal_grid3_group_{group}.txt'))
    else:
        print(gt_on_grid)

print(optimal_grid3)

if visualize == True:
    plt.show()
    plt.imsave()