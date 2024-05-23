import bpy 
import os, json, sys 
import pandas as pd 
import random
import string
import numpy as np 

def generate_unique_random_strings(n, length):
    # Define the pool of characters
    chars = string.ascii_letters + string.digits 
    # Initialize an empty set to store the generated strings
    unique_strings = set()
    # Initialize an empty list to store the unique strings
    unique_random_strings = []

    while len(unique_random_strings) < n:
        # Generate a random string of the specified length
        random_string = ''.join(random.choice(chars) for _ in range(length))
        # Check if the generated string is not in the set of unique strings
        if random_string not in unique_strings:
            # Add the generated string to the set of unique strings
            unique_strings.add(random_string)
            # Add the generated string to the list of unique random strings
            unique_random_strings.append(random_string)

    return unique_random_strings

# Example usage: Generate 5 unique random strings, each of length 10
n = 150
length = 6
unique_random_strings = generate_unique_random_strings(n, length)
for i, stringc in enumerate(unique_random_strings, start=1):
    print(f"Unique random string {i}: {stringc}")
assert(len(unique_random_strings) == len(np.unique(unique_random_strings))), 'DOUBLED!'


n = 200
length = 6
unique_random_strings_I = generate_unique_random_strings(n, length)
for i, stringc in enumerate(unique_random_strings_I, start=1):
    print(f"Unique random string {i}: {stringc}")
assert(len(unique_random_strings_I) == len(np.unique(unique_random_strings_I))), 'DOUBLED!'

#root_path = '/home/palma/Unive/RePAIR/Datasets/RePAIR_dataset/ground_truth' 
root_path = '/media/lucap/big_data/datasets/repair/ground_truth'
solved_puzzles = os.path.join(root_path, 'DONE')
solved_puzzles_gt = os.path.join(root_path, 'RPobj_json')
os.makedirs(solved_puzzles_gt, exist_ok=True)

list_of_solved_puzzles = [sp for sp in os.listdir(solved_puzzles) if sp.endswith('blend')]
print("Found:", len(list_of_solved_puzzles), " puzzles")
#list_of_solved_puzzles.sort()

groups2obj_dict = pd.DataFrame()
frag_names = []
frags_id = []
objs = []
objs_names = []
objs_names_rs = []
groups = []
isolated = []
isolated_groups = [62, 73, 74, 75]
skip = [76]
obj_counter = 0
isolated_counter = 0

for group_num in range(92):

    if group_num > 0 and group_num not in isolated_groups and group_num not in skip:
        solved_puzzle = f"group_{group_num}_DONE.blend"
        
        print(f"GT of {solved_puzzle}")
        gt_dict = {}
        filepath=os.path.join(solved_puzzles, solved_puzzle)
        if os.path.exists(filepath):
            bpy.ops.wm.open_mainfile(filepath=filepath)
            bpy.data.use_autopack = True
            bpy.context.scene.unit_settings.scale_length = 0.001
            bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
            collections = bpy.data.collections 
            print("collections:", len(collections))
            for collection in collections:
                print("collections:", (collection.name))
            # if len(collections) < 2:
            #     obj_counter += 1
            #     target_gt_path = os.path.join(solved_puzzles_gt, f"RPobj_{obj_counter:04d}.json")
            #     for obj in bpy.data.objects:
            #         if "RPf" in obj.name:
            #             loc = obj.location 
            #             rot_euleRPf_00004r = obj.rotation_euler
            #             rot_quat = rot_euler.to_quaternion()
            #             gt_piece = {
            #                 'location': [loc[0], loc[1], loc[2]],
            #                 'rotation_euler': [rot_euler.x, rot_euler.y, rot_euler.z],
            #                 'rotation_quaternion': [rot_quat[0], rot_quat[1], rot_quat[2], rot_quat[3]]
            #             }
            #             gt_dict[f"{obj.name}"] = gt_piece
            #             frag_names.append(obj.name)
            #             frags_id.append(f"{obj.name[4:]}")
            #             objs.append(obj_counter)
            #             groups.append(group_num)

            #     print(f"saving obj{obj_counter} from group{group_num}")
            #     with open(target_gt_path, 'w') as jtp:
            #         json.dump(gt_dict, jtp, indent=3)
            # else:
            for collection in collections:
                gt_dict = {}
                if "O" in collection.name or collection.name == "Collection": 
                    if len(collection.all_objects) > 0:
                        obj_counter += 1
                        json_name_v1 = f"RPobj_g{group_num}_o{obj_counter:04d}.json"
                        target_gt_path = os.path.join(solved_puzzles_gt, json_name_v1)
                        json_name_rs = f"__RP_g{group_num}_o_{unique_random_strings[obj_counter]}.json"
                        target_gt_path_rs = os.path.join(solved_puzzles_gt, json_name_rs)
                        for obj in collection.all_objects:
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
                                frag_names.append(obj.name)
                                frags_id.append(f"{obj.name[4:]}")
                                objs.append(obj_counter)
                                objs_names.append(json_name_v1)
                                objs_names_rs.append(json_name_rs)
                                groups.append(group_num)
                                isolated.append(0)

                        print(f"saving obj{obj_counter} from group{group_num}")
                        if obj_counter < group_num:
                            print("WARNING! What happened?")
                        with open(target_gt_path, 'w') as jtp:
                            json.dump(gt_dict, jtp, indent=3)
                        with open(target_gt_path_rs, 'w') as jtp:
                            json.dump(gt_dict, jtp, indent=3)

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
                            gt_dict[f"{obj.name}"] = gt_piece
                            frag_names.append(obj.name)
                            frags_id.append(f"{obj.name[4:]}")
                            objs.append(obj_counter)
                            objs_names.append(json_name_v1)
                            objs_names_rs.append(json_name_rs)
                            groups.append(group_num)
                            isolated.append(1)

                            json_name_v1 = f"RPobj_g{group_num}_i{isolated_counter:04d}.json"
                            target_gt_path = os.path.join(solved_puzzles_gt, json_name_v1)
                            json_name_rs = f"__RP_g{group_num}_i_{unique_random_strings_I[isolated_counter]}.json"
                            target_gt_path_rs = os.path.join(solved_puzzles_gt, json_name_rs)
                            
                            print(f"saving isolated fragment n. {isolated_counter} from group{group_num}")
                            
                            with open(target_gt_path, 'w') as jtp:
                                json.dump(gt_dict, jtp, indent=3)
                            with open(target_gt_path_rs, 'w') as jtp:
                                json.dump(gt_dict, jtp, indent=3)
        else:
            print(f"Group {group_num} should be there but not found!")
    else:
        print(f"Group {group_num} not found or not to be used!")

groups2obj_dict['pieces_names'] = frag_names
groups2obj_dict['pieces_id'] = frags_id
groups2obj_dict['object'] = objs
groups2obj_dict['object_name'] = objs_names
groups2obj_dict['object_name_random'] = objs_names_rs
groups2obj_dict['object'] = objs
groups2obj_dict['group'] = groups
groups2obj_dict['isolated'] = isolated
groups2obj_dict.to_csv(os.path.join(root_path, "groups2objects.csv"))
