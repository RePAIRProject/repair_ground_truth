import open3d as o3d
import numpy as np
import os
import argparse
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

def get_angles(n):
    theta_x = np.arcsin(n[1] / np.linalg.norm(np.asarray([n[1], n[2]])))
    theta_y = np.arcsin(n[0] / np.linalg.norm(np.asarray([n[0], n[2]])))
    return theta_x, theta_y, 0

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

def get_rotation_angles(obj_path):
    
    pcl = o3d.io.read_point_cloud(obj_path)
    # segment plane (it should be the top surface)
    plane_model, inliers = pcl.segment_plane(distance_threshold=0.2,
                                            ransac_n=5,
                                            num_iterations=1000)
    # we take the mean value of the normals of the plane
    inlier_cloud = pcl.select_by_index(inliers)
    #inlier_cloud.paint_uniform_color([1.0, 0, 0])
    #outlier_cloud = pcl.select_by_index(inliers, invert=True)
    inlier_cloud.estimate_normals()
    normal_vector = np.mean(
        np.asarray(inlier_cloud.normals), axis=0)

    a_x, a_y, a_z = get_angles(normal_vector)

    return a_x, a_y, a_z
