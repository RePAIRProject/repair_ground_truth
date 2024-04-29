import bpy 
import os, json 

root_path = '/media/lucap/big_data/datasets/repair/ground_truth'
solved_puzzles = os.path.join(root_path, 'DONE')
solved_puzzles_gt = os.path.join(root_path, 'gt_json')
os.makedirs(solved_puzzles_gt, exist_ok=True)

list_of_solved_puzzles = [sp for sp in os.listdir(solved_puzzles) if sp.endswith('blend')]
print("Found:", list_of_solved_puzzles)

for solved_puzzle in list_of_solved_puzzles:
    
    gt_dict = {}
    gt_2D_dict = {}
    bpy.ops.wm.open_mainfile(filepath=os.path.join(solved_puzzles, solved_puzzle))
    bpy.data.use_autopack = True
    bpy.context.scene.unit_settings.scale_length = 0.001
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

    for obj in bpy.data.objects:
        #breakpoint()
        if "RPf" in obj.name:
            loc = obj.location 
            rot_euler = obj.rotation_euler
            rot_quat = rot_euler.to_quaternion()
            gt_piece = {
                'location': [loc[0], loc[1], loc[2]],
                'rotation_euler': [rot_euler.x, rot_euler.y, rot_euler.z],
                'rotation_quaternion': [rot_quat[0], rot_quat[1], rot_quat[2], rot_quat[3]]
            }
            gt_dict[f"{obj.name}"] = gt_piece

    target_gt_path = os.path.join(solved_puzzles_gt, f"{solved_puzzle.split('.')[0][:-5]}.json")
    with open(target_gt_path, 'w') as jtp:
        json.dump(gt_dict, jtp, indent=3)

    bpy.ops.group.create(name="myGroup") # will not appear in outliner until objects are linked.
objects_to_add = "Cube1","Cube2","Cube3"
for name in objects_to_add:
    bpy.ops.object.select_name(name=name)
    bpy.ops.object.group_link(group="myGroup")
    print("finished with", solved_puzzle)

