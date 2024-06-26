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
    meshes_names = []
    all_pts = np.array([])
    for gtk in gt.keys():
        # print(f"{gtk}", end='\r')
        obj_path = os.path.join(root_folder, f"{gtk}.obj")
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
        print(f"{gtk} : {mesh.get_center()}")
        meshes.append(mesh)
        if len(all_pts) == 0:
            all_pts = np.asarray(mesh.vertices)
        else:
            all_pts = np.concatenate((all_pts, np.asarray(mesh.vertices)))

    cframe = o3d.geometry.TriangleMesh.create_coordinate_frame(size=100)
    o3d.visualization.draw_geometries(meshes+[cframe])

    #cframe = o3d.geometry.TriangleMesh.create_coordinate_frame(size=100)
    pcd = o3d.geometry.PointCloud(points=o3d.utility.Vector3dVector(all_pts))
    translation = -pcd.get_center()
    print("np:", np.mean(all_pts, axis=0))
    print("o3d:", pcd.get_center())
    pcd.translate(translation)
    o3d.visualization.draw_geometries([pcd, cframe])

    for mesh, mesh_name in zip(meshes, meshes_names):
        mesh.translate(translation)
        o3d.io.write_triangle_mesh(filename=os.path.join(args.output, mesh_name), \
            mesh=mesh, write_ascii=True)
    # breakpoint()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Reconstruct a puzzle using open3d given GT')  # add some discription
    parser.add_argument('-r', '--root', type=str, default='', help='puzzle root folder')  
    parser.add_argument('-j', '--json', type=str, default='', help='json ground truth file') 
    parser.add_argument('-o', '--output', type=str, default='', help='output folder')
    args = parser.parse_args()

    main(args)