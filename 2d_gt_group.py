import json, os
import cv2
import matplotlib.pyplot as plt 
import numpy as np 
import scipy.ndimage as ndi
import pandas as pd 
import argparse

def main(args):

    print("-" * 50)
    print(f"Reconstructing RePAIR group {args.g}")
    print(f"json solution at: {args.json}")
    print(f"images folder at: {args.imgs}")
    print("-" * 50)

    if args.g == '':
        print("\nWARNING: no group specified, please use -g N for group number")

    json_file_path = args.json 
    images_folder = args.imgs 

    canvas_shape = 11000
    cc = canvas_shape // 2
    img_size = 2000 
    ihs = img_size // 2
    pre_proc_scaling = 1/100    # i scaled the pieces 0.01 in align_face_up.py
    ort_proj = 2.714            # blender orthographic projection scale    

    visualize = args.show
    save_solution_as_txt = args.save_txt
    if args.output == "":
        output_folder = 'gt_2d_txt'
    else:
        output_folder = args.output
    os.makedirs(output_folder, exist_ok=True)

    with open(json_file_path, 'r') as jgt:
        gt = json.load(jgt)

    df = pd.DataFrame()
    solution = np.zeros((len(gt.keys()), 3))
    names = []
    canvas = np.zeros((canvas_shape, canvas_shape, 4))
    k = 0
    for gtk in gt.keys():
        print(f"Reading image of piece {gtk}..", end='\r')
        img_name = f"{gtk}_intact_mesh.png"
        img = plt.imread(os.path.join(images_folder, img_name))
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
        names.append(img_name)

    if visualize == True:
        print("\nVisualizing..")
        plt.subplot(1,3,j+1)
        plt.title(f"Group {group}")
        plt.imshow(canvas)
        plt.show()

    if args.save_img == True:
        print("\nSaving reconstructed image..")
        os.makedirs(output_folder, exist_ok=True)
        final_solution = os.path.join(output_folder, f"{args.g}.png")
        plt.imsave(final_solution, (canvas * 255).astype(np.uint8))
        print("Done")

    if save_solution_as_txt == True:
        print("\nSaving reconstruction as txt..")
        const_x = np.min(solution[:, 0])
        const_y = np.min(solution[:, 1])
        df['rpf'] = names
        df['x'] = solution[:, 0] - const_x
        df['y'] = solution[:, 1] - const_y
        df['rot'] = solution[:, 2]
        df.to_csv(os.path.join(output_folder, f'group_{args.g}.txt'))
        print("Done")
    else:
        print("\nNot saving: solution is:\n")
        print(solution)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Given the json file, creates the reconstructed 2D version')  # add some discription
    parser.add_argument('-imgs', type=str, default='', help='folder of the images (of a group)')  
    parser.add_argument('-json', type=str, default='', help='path of the json file (gt)')  
    parser.add_argument('-g', type=str, default='', help='group number')  
    parser.add_argument('-show', type=bool, default=False, help='visualize the reconstruction')  
    parser.add_argument('-save_img', type=bool, default=True, help='save an image-version of the reconstruction')  
    parser.add_argument('-save_txt', type=bool, default=True, help='save a txt-version of the reconstruction')  
    parser.add_argument('-output', type=str, default='', help='output folder')  

    args = parser.parse_args() 

    main(args)