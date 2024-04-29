import open3d as o3d 
import argparse

def main(args):

    root_folder = args.root 
    json_path = args.json 
    with open(json_path, 'r') as jp:
        gt = json.load(jp)
    
    for gtk in gt.keys():
        obj_path = os.path.join(root_folder, f"{gtk}.obj")
        mesh = o3d.io.read_triangle_mesh(obj_path)
        # move to the origin 
        mesh.translate()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Reconstruct a puzzle using open3d given GT')  # add some discription
    parser.add_argument('-r', '--root', type=str, default='', help='puzzle root folder')  
    parser.add_argument('-j', '--json', type=str, default='', help='json ground truth file')  
    args = parser.parse_args()

    main(args)