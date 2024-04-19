import bpy
import os 
from pieces_utils import *

root_path = '/media/lucap/big_data/datasets/repair/'
target_gt_folder = os.path.join(root_path, 'ground_truth')
os.makedirs(target_gt_folder, exist_ok=True)
# for blender
filepath = os.path.join(target_gt_folder, 'setup.blend')
bpy.ops.wm.open_mainfile(filepath=filepath)
bpy.data.use_autopack = True
bpy.context.scene.unit_settings.scale_length = 0.001
bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
grid_size = 250
for group in range(90):
    
    group_path = os.path.join(root_path, f'group_{group}')
    processed_folder = os.path.join(group_path, 'processed')
    #prepared_folder = os.path.join(group_path, 'facing_up')

    # Remove all default objects
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)

    if os.path.exists(processed_folder):
        print("Working on group", group)
        files = os.listdir(processed_folder)
        obj_meshes_list = [file for file in files if file.endswith('.obj')]
        print(obj_meshes_list)
        num_pieces = len(obj_meshes_list)
        on_axis = np.ceil(np.sqrt(num_pieces)).astype(int)
        x_ = np.linspace(-grid_size, grid_size, on_axis)
        y_ = np.linspace(-grid_size, grid_size, on_axis)
        # xv, yv = np.meshgrid(x_, y_)
        counter = 0 
        for obj_mesh in obj_meshes_list:
            # print(obj_mesh)
            # breakpoint()
            a_x, a_y, a_z = get_rotation_angles(os.path.join(processed_folder, f"{obj_mesh[:-4]}.ply"))
            bpy.ops.wm.obj_import(filepath=os.path.join(processed_folder, obj_mesh), up_axis='Z')
            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
            #bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
            #obj = bpy.context.object
            bpy.context.object.location = (x_[counter // on_axis], y_[counter % on_axis], 0)
            bpy.context.object.rotation_euler = (a_x, a_y, a_z)
            counter += 1
        
        # Specify the path where you want to save the new .blend file        
        save_path = os.path.join(target_gt_folder, f"group_{group}_TODO.blend")
        bpy.ops.wm.save_mainfile(filepath=save_path)
        #breakpoint()
  
# Save the current Blender session as a .blend file
