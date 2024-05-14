import open3d as o3d 
import argparse
import json, os
import numpy as np 
import copy 

def main(args):

    root_folder = args.root 
    gt_folder = args.ground_truth 

    done_folder = os.path.join(gt_folder, "RP_objects_gt_json")            # the .json files   
    puzzle_folder = os.path.join(gt_folder, "RP_dataset_NIPS_2024")     # dataset folder for release
    assembled_folder = os.path.join(puzzle_folder, 'assembled_objects')     # assembled objects here
    os.makedirs(assembled_folder, exist_ok=True)
    isolated_folder = os.path.join(puzzle_folder, 'isolated_pieces')        # isolated pieces here
    os.makedirs(isolated_folder, exist_ok=True)


    done_objects = [ff for ff in os.listdir(done_folder) if ff.endswith(".json")]   # all json files
    for done_obj in done_objects:
        group_string = done_obj.split("_")[1]           # g1, g2, g45, ..
        group_num = group_string[1:]                    # the number of the group (1, 2, 3, ... 89, 90, 91)
        obj_string = done_obj.split("_")[2]             # o0001, o0002, o0045, .. or i0001, i0002, i0033, ..
        obj_type = obj_string[0]                        # o = assembled object // i = isolated piece
        obj_num = obj_string[1:]                        # number of the object
        group_name = f"group_{group_num}"               # this is to find the original piece
        print(f"working on obj {obj_num} ({obj_type}) from group {group_num}")
        
        json_path = os.path.join(done_folder, done_obj)
        with open(json_path, 'r') as jp:
            gt = json.load(jp)

        if obj_type == 'o':
            output_puzzle_folder = os.path.join(assembled_folder, f"{done_obj[:-5]}")
        elif obj_type == 'i':
            output_puzzle_folder = os.path.join(isolated_folder, f"{done_obj[:-5]}")
        else:
            print("error with substringing..")

        if os.path.exists(output_puzzle_folder):
            print(f"skipping {done_obj} as {output_puzzle_folder} already exist")
        else:
            os.makedirs(output_puzzle_folder, exist_ok=False)
            processed_folder = os.path.join(root_folder, group_name, 'processed')
            meshes = []
            meshes_names = []
            all_pts = np.array([])
            # here we assemble the pieces
            for gtk in gt.keys():
                # print(f"{gtk}", end='\r')
                obj_path = os.path.join(processed_folder, f"{gtk}.obj")
                meshes_names.append(f"{gtk}.obj")
                mesh = o3d.io.read_triangle_mesh(obj_path, enable_post_processing=True)
                # place them in the origin 
                mesh.translate(-mesh.get_center())
                # rotation in blender style
                rot_angles = gt[gtk]['rotation_euler']
                mesh.rotate(o3d.geometry.get_rotation_matrix_from_xyz([rot_angles[0], 0, 0]), center=mesh.get_center())
                mesh.rotate(o3d.geometry.get_rotation_matrix_from_xyz([0, rot_angles[1], 0]), center=mesh.get_center())
                mesh.rotate(o3d.geometry.get_rotation_matrix_from_xyz([0, 0, rot_angles[2]]), center=mesh.get_center())
                # now translation
                mesh.translate(gt[gtk]['location'])
                meshes.append(mesh)
                if len(all_pts) == 0:
                    all_pts = np.asarray(mesh.vertices)
                else:
                    all_pts = np.concatenate((all_pts, np.asarray(mesh.vertices)))

            # This is needed to align the whole object to the origin
            pcd = o3d.geometry.PointCloud(points=o3d.utility.Vector3dVector(all_pts))
            translation = -pcd.get_center()

            for mesh, mesh_name in zip(meshes, meshes_names):
                mesh.translate(translation)
                o3d.io.write_triangle_mesh(filename=os.path.join(output_puzzle_folder, mesh_name), \
                    mesh=mesh, write_ascii=True)

            # only for visualization
            # UNCOMMENT THIS TO VISUALIZE 
            # cframe = o3d.geometry.TriangleMesh.create_coordinate_frame(size=100)
            # pcd.translate(translation)
            # o3d.visualization.draw_geometries([pcd, cframe])
            print("Done with", group_name)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Reconstruct a puzzle using open3d given GT')  # add some discription
    parser.add_argument('-r', '--root', type=str, default='', help='root folder (where the dataset is)')  
    parser.add_argument('-gt', '--ground_truth', type=str, default='', help='ground truth folder (blender and json files)')  
    args = parser.parse_args() 

    main(args)
