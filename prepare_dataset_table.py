import os 
import natsort
import pandas as pd
import shutil 

root_path = '/home/lucap/code/RePair_3D_new' #'/media/lucap/big_data/datasets/repair/ground_truth'
solved_puzzles_pieces = os.path.join(root_path, 'PUZZLES', 'SOLVED')
solved_puzzles_images = os.path.join(root_path, 'PUZZLES_2D_scale3', 'SOLVED')

output_folder = os.path.join(root_path, 'DATABASE')
vis_subfolder = os.path.join(output_folder, 'VIS_2D_REFERENCE_IMAGES')
os.makedirs(vis_subfolder, exist_ok=True)

list_of_solved_puzzles_unsorted = [sp for sp in os.listdir(solved_puzzles_pieces) if os.path.isdir(os.path.join(solved_puzzles_pieces, sp))]
list_of_solved_puzzles = natsort.natsorted(list_of_solved_puzzles_unsorted)

print(f"Found {len(list_of_solved_puzzles)} solved puzzles")
for nn, pf in enumerate(list_of_solved_puzzles):
    print(f"{nn}: {pf}")

puzzles_table = pd.DataFrame()
names = []
repair_nomenclature = []
fuchs_nomenclature = []
images = []
descriptions = []
decor = []
archeological_info = []
motives_visible = []

fragments_table = pd.DataFrame()
frags_ids = []
frags_rp_names = []
frags_groups = []
frags_puzzles = []
frags_motives = []
frags_weights = []
frags_notes = []


# motives_table = pd.DataFrame()
# motive_name = []
# motive_code = []
# motive_image = []
# motive_decor = []

for solved_puzzle_folder in list_of_solved_puzzles:
    names.append(solved_puzzle_folder)
    rp_group = solved_puzzle_folder.split("RP")[-1][1:]
    repair_nomenclature.append(rp_group)
    fuchs_nomenclature.append("")
    images.append("")
    descriptions.append("")
    decor.append("")
    archeological_info.append("")
    motives_visible.append("")
    puzzle_folder_full_path = os.path.join(solved_puzzles_pieces, solved_puzzle_folder)
    # copy image 
    shutil.copy2(os.path.join(solved_puzzles_images, solved_puzzle_folder, 'adjacency_preview.png'), os.path.join(vis_subfolder, f"{solved_puzzle_folder}.png"))
    # iterate over each fragment
    list_of_fragments_unsorted = [of for of in os.listdir(puzzle_folder_full_path) if of.endswith('obj')]
    list_of_fragments = natsort.natsorted(list_of_fragments_unsorted)
    for fragment_path in list_of_fragments:
        fragment_name = fragment_path.split(".")[0]
        frags_rp_names.append(fragment_name)
        frags_ids.append(fragment_name.split("_")[-1])
        frags_groups.append(rp_group)
        frags_puzzles.append(solved_puzzle_folder)
        frags_motives.append("")
        frags_weights.append("")
        frags_notes.append("")


puzzles_table['Name'] = names
puzzles_table['RePAIR'] = repair_nomenclature
puzzles_table['Fuchs'] = fuchs_nomenclature
puzzles_table['Image'] = images
puzzles_table['Description'] = descriptions
puzzles_table['Decor'] = decor
puzzles_table['Archeological Information'] = archeological_info
puzzles_table['Motives'] = motives_visible
puzzles_table.to_csv(os.path.join(output_folder, 'puzzles.csv'))

fragments_table['ID'] = frags_ids
fragments_table['RPF'] = frags_rp_names
fragments_table['Group'] = frags_groups
fragments_table['Puzzle'] = frags_puzzles
fragments_table['Motives'] = frags_motives
fragments_table['Weight'] = frags_weights
fragments_table['Note'] = frags_notes
fragments_table.to_csv(os.path.join(output_folder, 'fragments.csv'))
