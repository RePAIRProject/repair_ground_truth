import open3d as o3d
import numpy as np
import os, argparse
import vedo as vd

def transform_mesh(m):
    cm = m.centerOfMass()
    m.shift(-cm)
    elli = vd.pcaEllipsoid(m, pvalue=0.5)

    ax1 = vd.versor(elli.axis1)
    ax2 = vd.versor(elli.axis2)
    ax3 = vd.versor(elli.axis3)

    # the transposed matrix is already the inverse
    T = np.array([ax1, ax2, ax3])

    return m.applyTransform(T, reset=True)  # <-- I had to enable reset


def get_R_x(n):
    R_x = np.zeros((3, 3))
    theta = np.arcsin(n[1] / np.linalg.norm(np.asarray([n[1], n[2]])))
    # print(f"rotating {theta} on yz plane")
    R_x[0, 0] = 1
    R_x[1, 1] = np.cos(theta)
    R_x[1, 2] = - np.sin(theta)
    R_x[2, 2] = np.cos(theta)
    R_x[2, 1] = np.sin(theta)
    return R_x


def get_R_y(n):
    R_y = np.zeros((3, 3))
    theta = np.arcsin(n[0] / np.linalg.norm(np.asarray([n[0], n[2]])))
    # print(f"rotating {theta} on xz plane")
    R_y[1, 1] = 1
    R_y[0, 0] = np.cos(theta)
    R_y[0, 2] = np.sin(theta)
    R_y[2, 2] = np.cos(theta)
    R_y[2, 0] = - 1 * np.sin(theta)
    return R_y


def align_face_up(mesh, n, mean_point):
    """
    We want the piece with the flat surface (from normal n)
    looking "up" in the z-axis and in the origin (0, 0, 0).
    So rotation in z is not needed (we don't have yet a solution)
    We just want on xz and yz plane so set it flat
    """
    # move to origin
    mesh.translate(-mean_point)

    # first on yz plane (around x-axis)
    Rx = get_R_x(n)
    mesh.transform(matrix_3x3_to_4x4(Rx))

    # then on xz plane (around y-axis)
    Ry = get_R_y(n)
    mesh.transform(matrix_3x3_to_4x4(Ry))

    # no return, the mesh is transformed

def matrix_3x3_to_4x4(m):

    T = np.zeros((4, 4))
    T[:3, :3] = m
    T[3, 3] = 1
    return T


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Preparing the fragments for manual ground truth: moving them to origin and aligning them with the flat surface facing up')
    parser.add_argument('-m', '--method', type=str, default='open3d',
                        help='method to rotate the pcl. "open3d" segment the largest plane and align that, "vedo" aligns based on pca ellipsoid of the fragment')
    parser.add_argument('-d', '--dataset_folder', type=str, default='',
                        help='root folder of the dataset. Here the absolute path should be used')
    parser.add_argument('-g', '--group', type=int, default=15, help='group number. it will be appended to the root path (after `processed` to find the correct group folder)')
    parser.add_argument('-o', '--output_folder', type=str, default='facing_up',
                        help='name of the folder where to save files (appended to the root folder)')
    parser.add_argument('-v', '--visualize', action='store_true', default=False, help='show pointclouds (original and rotated)')

    args = parser.parse_args()
    print("#" * 40)
    print(f"using {args.method} method")
    print(f"on group {args.group}")

    if args.dataset_folder == '':
        print("\nWarning: no dataset folder given (run with `-d` or `--dataset_folder` to give), so using the default")
        repair_dataset_folder = '/home/palma/Unive/RePAIR/Datasets/RePAIR_dataset'
        print("dataset_folder:", repair_dataset_folder)
    else:
        repair_dataset_folder = args.dataset_folder
    group = args.group
    group_folder = os.path.join(repair_dataset_folder, f'group_{group}')
    input_folder = os.path.join(group_folder, 'processed')
    output_folder = os.path.join(group_folder, args.output_folder)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    print('use --help to check other options')
    print("#" * 40)

    if args.method == 'vedo':
        pcds = vd.load(os.path.join(group_folder, input_folder, "*.ply"))

    for file in os.listdir(input_folder):
        if file[-4:] == '.ply':

            print("\nworking on", file[:-4])
            facing_up_path = os.path.join(output_folder, f'{file[:-4]}_fup.ply')

            ## USING OPEN3D to segment plane and rotate the fragment
            if args.method == 'open3d':
                # pointcloud is used for segmenting the plane
                pcl = o3d.io.read_point_cloud(os.path.join(input_folder, file))
                # mesh is used for saving for better visualization in Blender
                mesh = o3d.io.read_triangle_mesh(os.path.join(input_folder, file))
                # segment plane (it should be the top surface)
                plane_model, inliers = pcl.segment_plane(distance_threshold=0.2,
                                                     ransac_n=5,
                                                     num_iterations=1000)
                # we take the mean value of the normals of the plane
                inlier_cloud = pcl.select_by_index(inliers)
                #inlier_cloud.paint_uniform_color([1.0, 0, 0])
                #outlier_cloud = pcl.select_by_index(inliers, invert=True)
                inlier_cloud.estimate_normals()
                normal_vector = np.mean(np.asarray(inlier_cloud.normals), axis=0)
                # also the mean point to move the fragment to the origin
                mean_point = np.mean(np.asarray(pcl.points), axis=0)
                # rotate with z facing up
                align_face_up(mesh, normal_vector, mean_point)

                if args.visualize:
                    o3d.visualization.draw_geometries([pcl, pcl_facing_up])


                o3d.io.write_triangle_mesh(facing_up_path, mesh)


            else:
                ## using vedo to create ellipsoid around the fragment and
                pcd = vd.Mesh(os.path.join(input_folder, file))
                m_aligned = transform_mesh(pcd)
                if args.visualize:
                    vd.show(m_aligned, axes=8).close()
                vd.write(m_aligned, facing_up_path)

            print("saved in:", facing_up_path)

    print('\nDone - files in:', output_folder)
