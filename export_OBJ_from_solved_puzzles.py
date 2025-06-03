import bpy 
import os, json, sys
scripts_dir = bpy.utils.user_resource('SCRIPTS')
sys.path.append(scripts_dir)
import bmesh
import numpy as np
import sys
import open3d as o3d 
import pandas as pd 
from natsort import natsorted
import shutil 

root_path = '/home/lucap/code/RePair_3D_new' #'/media/lucap/big_data/datasets/repair/ground_truth'
solved_puzzles = os.path.join(root_path, 'DONE')
solved_puzzles_GT = os.path.join(root_path, 'PUZZLES')
open_discovery_folder = os.path.join(solved_puzzles_GT, 'OPEN_DISCOVERY')
solved_puzzles_json = os.path.join(root_path, 'JSON')
os.makedirs(solved_puzzles_GT, exist_ok=True)
os.makedirs(solved_puzzles_json, exist_ok=True)
os.makedirs(open_discovery_folder, exist_ok=True)

list_of_solved_puzzles_unsorted = [sp for sp in os.listdir(solved_puzzles) if sp.endswith('blend')]
list_of_solved_puzzles = natsorted(list_of_solved_puzzles_unsorted)

print(f"Found {len(list_of_solved_puzzles)} solved puzzles")
for nn, pf in enumerate(list_of_solved_puzzles):
    print(f"{nn}: {pf}")

puzzle_df = pd.DataFrame()
puzzle_names = []
puzzle_num_fragments = []
puzzle_decor = []
puzzle_motives = []
puzzle_description = []
puzzle_backside = []


groups2obj_dict = pd.DataFrame()
frag_names = []
frags_id = []
objs = []
objs_names = []
objs_names_rs = []
groups = [] #[62, 73, 74, 75]: #
isolated = []
isolated_groups = [] # marked as isolated collections! [62, 73, 74, 75]
skip = [76]
puzzle_counter = 1
isolated_counter = 0

# breakpoint()

for solved_puzzle in list_of_solved_puzzles:

    # breakpoint()
    print("#" * 50)
    print("exporting from", solved_puzzle)

    # folder for the solved pieces 
    group_num = int(solved_puzzle.split('_')[1])
    # group_name = solved_puzzle[:-]
    
    print("1. Opening Blender file..")
    bpy.ops.wm.open_mainfile(filepath=os.path.join(solved_puzzles, solved_puzzle))
    bpy.data.use_autopack = True
    bpy.context.scene.unit_settings.scale_length = 0.001
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

    # print("2. Unpacking images..")
    # # Iterate through all images in the scene
    # for img in bpy.data.images:
    #     # Check if the image is packed
    #     if img.packed_file:
    #         # Unpack the image
    #         img.unpack()
    
    gt_dict = {}

    
    collections = bpy.data.collections 
    print("Collections:")
    for collection in collections:
        print('-' * 30)
        print(f"\t{collection.name}")
        gt_dict = {}
        if "O" in collection.name or "Collection" in collection.name \
            and ".00" not in collection.name:

            if len(collection.all_objects) > 0:

                puzzle_name = f"puzzle_{puzzle_counter:07d}_RP_group_{group_num}"
                print("- Creating", puzzle_name)
                solved_pieces_folder = os.path.join(solved_puzzles_GT, puzzle_name)
                os.makedirs(solved_pieces_folder, exist_ok=True)
                json_name_v1 = f"RPobj_g{group_num}_o{puzzle_counter:04d}.json"
                target_gt_path = os.path.join(solved_puzzles_json, json_name_v1)
                puzzle_counter += 1
                
                # json_name_rs = f"__RP_g{group_num}_o_{unique_random_strings[puzzle_counter]}.json"
                # target_gt_path_rs = os.path.join(solved_puzzles_gt, json_name_rs)
                num_frags = 0
                for obj in collection.all_objects:
                    if "RPf" in obj.name:
                        num_frags += 1
                        loc = obj.location 
                        rot_euler = obj.rotation_euler
                        rot_quat = rot_euler.to_quaternion()
                        gt_piece = {
                            'location': [loc[0], loc[1], loc[2]],
                            'rotation_euler': [rot_euler.x, rot_euler.y, rot_euler.z],
                            'rotation_quaternion': [rot_quat[0], rot_quat[1], rot_quat[2], rot_quat[3]]
                        }
                        gt_dict[f"{obj.name}"] = gt_piece
                        frag_names.append(obj.name)
                        frags_id.append(f"{obj.name[4:]}")
                        objs.append(puzzle_counter)
                        objs_names.append(json_name_v1)
                        # objs_names_rs.append(json_name_rs)
                        groups.append(group_num)
                        isolated.append(0)

                        # Saving the obj file
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.data.objects[obj.name].select_set(True)
                        filepath = os.path.join(solved_pieces_folder, f'{obj.name}.obj')
                        for mat in bpy.data.objects[obj.name].material_slots:
                            if mat.material.use_nodes:
                                for node in mat.material.node_tree.nodes:
                                    if node.type == 'TEX_IMAGE':
                                        if node.image.packed_file:
                                            os.chdir(solved_pieces_folder)
                                            orig_path = bpy.path.abspath(node.image.filepath)
                                            node.image.unpack(method='WRITE_LOCAL')
                                            src_path = os.path.join(solved_puzzles, 'textures', os.path.basename(node.image.filepath))
                                            dest_path = os.path.join(solved_pieces_folder, os.path.basename(node.image.filepath))
                                            shutil.copy2(src_path, dest_path)
                                            node.image.filepath = dest_path
                                            node.image.reload()
                        bpy.ops.wm.obj_export(filepath=filepath, 
                                             export_selected_objects=True, 
                                             path_mode='COPY',
                                             export_materials=True)
            
                puzzle_names.append(puzzle_name)
                puzzle_num_fragments.append(num_frags)
                puzzle_decor.append("")
                puzzle_motives.append("")
                puzzle_description.append("")
                puzzle_backside.append("")

                print(f"saving puzzle {puzzle_counter} from group {group_num}")
                if puzzle_counter < group_num:
                    print("WARNING! What happened?")
                with open(target_gt_path, 'w') as jtp:
                    json.dump(gt_dict, jtp, indent=3)
                # with open(target_gt_path_rs, 'w') as jtp:
                #     json.dump(gt_dict, jtp, indent=3)

        elif "isolated" in collection.name:
            
            for obj in collection.all_objects:
                gt_dict = {}
                if "RPf" in obj.name:
                    isolated_counter += 1
                    loc = obj.location 
                    rot_euler = obj.rotation_euler
                    rot_quat = rot_euler.to_quaternion()
                    gt_piece = {
                        'location': [loc[0], loc[1], loc[2]],
                        'rotation_euler': [rot_euler.x, rot_euler.y, rot_euler.z],
                        'rotation_quaternion': [rot_quat[0], rot_quat[1], rot_quat[2], rot_quat[3]]
                    }
                    json_name_v1 = f"RPobj_g{group_num}_i{isolated_counter:04d}.json"
                    # json_name_rs = f"__RP_g{group_num}_i_{unique_random_strings_I[isolated_counter]}.json"
                    gt_dict[f"{obj.name}"] = gt_piece
                    frag_names.append(obj.name)
                    frags_id.append(f"{obj.name[4:]}")
                    objs.append(puzzle_counter)
                    objs_names.append(json_name_v1)
                    # objs_names_rs.append(json_name_rs)
                    groups.append(group_num)
                    isolated.append(1)

                    target_gt_path = os.path.join(solved_puzzles_json, json_name_v1)
                    # target_gt_path_rs = os.path.join(solved_puzzles_gt, json_name_rs)
                    
                    print(f"saving isolated fragment n. {isolated_counter} from group{group_num}")
                    # Saving the obj file
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.data.objects[obj.name].select_set(True)
                    filepath = os.path.join(open_discovery_folder, f'{obj.name}.obj')
                    for mat in bpy.data.objects[obj.name].material_slots:
                        if mat.material.use_nodes:
                            for node in mat.material.node_tree.nodes:
                                if node.type == 'TEX_IMAGE':
                                    if node.image.packed_file:
                                        os.chdir(open_discovery_folder)
                                        orig_path = bpy.path.abspath(node.image.filepath)
                                        node.image.unpack(method='WRITE_LOCAL')
                                        src_path = os.path.join(solved_puzzles, 'textures', os.path.basename(node.image.filepath))
                                        dest_path = os.path.join(open_discovery_folder, os.path.basename(node.image.filepath))
                                        shutil.copy2(src_path, dest_path)
                                        node.image.filepath = dest_path
                                        node.image.reload()
                    bpy.ops.wm.obj_export(filepath=filepath, 
                                        export_selected_objects=True, 
                                        path_mode='COPY',
                                        export_materials=True)


                    with open(target_gt_path, 'w') as jtp:
                        json.dump(gt_dict, jtp, indent=3)
                    # with open(target_gt_path_rs, 'w') as jtp:
                    #     json.dump(gt_dict, jtp, indent=3)
        else:
            print(f"Group {group_num} should be there but not found!")
    else:
        print(f"Group {group_num} not found or not to be used!")


    print("finished with", solved_puzzle)
    print("#" * 50)
    print("\n\n\n")

groups2obj_dict['pieces_names'] = frag_names
groups2obj_dict['pieces_id'] = frags_id
groups2obj_dict['object'] = objs
groups2obj_dict['object_name'] = objs_names
# groups2obj_dict['object_name_random'] = objs_names_rs
groups2obj_dict['object'] = objs
groups2obj_dict['group'] = groups
groups2obj_dict['isolated'] = isolated
groups2obj_dict.to_csv(os.path.join(solved_puzzles_GT, "fragments.csv"))

puzzle_df['name'] = puzzle_names
puzzle_df['num_fragments'] = puzzle_num_fragments
puzzle_df['puzzle_decor'] = puzzle_decor
puzzle_df['puzzle_motives'] = puzzle_motives
puzzle_df['puzzle_description'] = puzzle_description
puzzle_df['puzzle_backside'] = puzzle_backside
puzzle_df.to_csv(os.path.join(solved_puzzles_GT, "puzzles.csv"))


    # # NOT SURE
    # cms = {}
    # big_list_of_vertices = np.asarray([])
    # pcds = []
    # # Switch to edit mode
    # for obj in bpy.data.objects:
    #     if "RPf" in obj.name:
    #         print(obj.name)
    #         bpy.ops.object.select_all(action='DESELECT')
    #         bpy.data.objects[obj.name].select_set(True)
    #         bpy.context.view_layer.objects.active = obj
    #         bpy.ops.object.mode_set(mode='EDIT')
    #         obj = bpy.context.active_object
    #         bm = bmesh.from_edit_mesh(obj.data)
    #         vertices_coords = [v.co for v in bm.verts]
    #         #big_list_of_vertices += vertices_coords
    #         np_verts = np.array(vertices_coords)
    #         if len(big_list_of_vertices) == 0:
    #             big_list_of_vertices = np_verts
    #         else:
    #             big_list_of_vertices = np.concatenate((big_list_of_vertices, np_verts))
    #         o3d_verts = o3d.utility.Vector3dVector(np_verts)
    #         pcd = o3d.geometry.PointCloud(points=o3d_verts)
    #         pcds.append(pcd)
    #         #cms[obj.name] = pcd.get_center()
    #         bpy.ops.object.mode_set(mode='OBJECT')
    #         # Print the indices of the selected vertices
    #         print(obj.name, ":", np.mean(np_verts, axis=0))
    #         o3d.visualization.draw_geometries(pcds)  

    # o3d_verts_bm = o3d.utility.Vector3dVector(big_list_of_vertices)
    # big_mesh = o3d.geometry.PointCloud(points=o3d_verts_bm)
    # cm_big_mesh = np.mean(big_list_of_vertices, axis=0)
    # print("big mesh:", np.mean(big_list_of_vertices, axis=0))
    # big_mesh.paint_uniform_color((1, 0, 0))
    # pcds.append(big_mesh)
    # o3d.visualization.draw_geometries(pcds)  

    # # breakpoint()

    # # Iterate through all images in the scene
    # for img in bpy.data.images:
    #     # Check if the image is packed
    #     if img.packed_file:
    #         # Unpack the image
    #         img.unpack()

    # for obj in bpy.data.objects:
    #     if "RPf" in obj.name:
    #         bpy.ops.object.select_all(action='DESELECT')
    #         bpy.data.objects[obj.name].select_set(True)
    #         filepath = os.path.join(solved_pieces_folder, f'piece_{obj.name}.obj')
    #         bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True, path_mode='COPY')


    # breakpoint()
    # bpy.ops.group.create(name="myGroup") # will not appear in outliner until objects are linked.
    # objects_to_add = "Cube1","Cube2","Cube3"
    # for name in objects_to_add:
    #     bpy.ops.object.select_name(name=name)
    #     bpy.ops.object.group_link(group="myGroup")
    #     print("finished with", solved_puzzle)

