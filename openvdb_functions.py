import pyopenvdb as vdb
import numpy as np
import base64
import os
import sys



if __name__ == '__main__':

    points_filepath = sys.argv[1]
    triangles_filepath = sys.argv[2]
    half_width_filepath = sys.argv[3]
    grid_size_filepath = sys.argv[4]
    grid_output_filepath = sys.argv[5]


    points = np.load(points_filepath, allow_pickle=True)
    triangles = np.load(triangles_filepath, allow_pickle=True)
    half_width = np.load(half_width_filepath, allow_pickle=True)
    grid_size = np.load(grid_size_filepath, allow_pickle=True)

    half_width = float(half_width)
    
    points = points.astype(np.float)
    triangles = triangles.astype(np.float)


    points_bytes = points.tobytes()
    points_dtype = points.dtype.name
    points_shape = points.shape

    triangles_bytes = triangles.tobytes()
    triangles_dtype = triangles.dtype.name
    triangles_shape = triangles.shape


    points_bytes = bytes(points_bytes)
    triangles_bytes = bytes(triangles_bytes)
    points = np.frombuffer(points_bytes, dtype=points_dtype).reshape(points_shape)
    triangles = np.frombuffer(triangles_bytes, dtype=triangles_dtype).reshape(triangles_shape)



    grid_vdb = vdb.FloatGrid()
    grid_vdb = grid_vdb.createLevelSetFromPolygons(points, triangles, halfWidth=half_width)
    grid_data_float = np.ndarray((grid_size[0], grid_size[1], grid_size[2]), float)
    grid_data_float.fill(0)
    grid_vdb.copyToArray(grid_data_float)

    np.save(grid_output_filepath,grid_data_float)