import open3d as o3d 
import argparse
import json, os
import numpy as np 
import copy 

def main(args):

    root_folder = args.root 
    json_path = args.json 
    with open(json_path, 'r') as jp:
        gt = json.load(jp)

    meshes = []
    for gtk in gt.keys():
        print(f"{gtk}", end='\r')
        obj_path = os.path.join(root_folder, f"{gtk}.obj")
        mesh = o3d.io.read_triangle_mesh(obj_path)
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
    cframe = o3d.geometry.TriangleMesh.create_coordinate_frame(size=100)
    o3d.visualization.draw_geometries(meshes+[cframe])
    # breakpoint()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Reconstruct a puzzle using open3d given GT')  # add some discription
    parser.add_argument('-r', '--root', type=str, default='', help='puzzle root folder')  
    parser.add_argument('-j', '--json', type=str, default='', help='json ground truth file')  
    args = parser.parse_args()

    main(args)