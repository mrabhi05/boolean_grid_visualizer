import numpy as np

grid_filename = 'grid.npy'
stl_filename = 'grid.stl'
cell_size = 1

def write_triangle_stl(f, vertices, face_normal):
    f.write(f'    facet normal {face_normal[0]} {face_normal[1]} {face_normal[2]}\n')
    f.write(f'        outer loop\n')
    f.write(f'            vertex {vertices[0][0]} {vertices[0][1]} {vertices[0][2]}\n')
    f.write(f'            vertex {vertices[1][0]} {vertices[1][1]} {vertices[1][2]}\n')
    f.write(f'            vertex {vertices[2][0]} {vertices[2][1]} {vertices[2][2]}\n')
    f.write(f'        endloop\n')
    f.write(f'    endfacet\n')

def write_cube_stl(f, cell, bbox):
    pts = []
    for i in range(2):
        for j in range(2):
            for k in range(2):
                pts.append([
                    bbox[0, 0] + ((cell[0] + i - 0.5) * cell_size),
                    bbox[0, 1] + ((cell[1] + j - 0.5) * cell_size),
                    bbox[0, 2] + ((cell[2] + k - 0.5) * cell_size),
                ])

    write_triangle_stl(f, [pts[0], pts[4], pts[1]], [0, -1, 0])
    write_triangle_stl(f, [pts[1], pts[4], pts[5]], [0, -1, 0])
    
    write_triangle_stl(f, [pts[6], pts[2], pts[7]], [0,  1, 0])
    write_triangle_stl(f, [pts[7], pts[2], pts[3]], [0,  1, 0])
    
    # --------------------------------------------------------#

    write_triangle_stl(f, [pts[2], pts[0], pts[3]], [-1, 0, 0])
    write_triangle_stl(f, [pts[3], pts[0], pts[1]], [-1, 0, 0])    
    
    write_triangle_stl(f, [pts[4], pts[6], pts[5]], [ 1, 0, 0])
    write_triangle_stl(f, [pts[5], pts[6], pts[7]], [ 1, 0, 0])
    
    # --------------------------------------------------------#

    write_triangle_stl(f, [pts[2], pts[6], pts[0]], [0, 0, -1])
    write_triangle_stl(f, [pts[0], pts[6], pts[4]], [0, 0, -1])

    write_triangle_stl(f, [pts[7], pts[3], pts[5]], [0, 0,  1])
    write_triangle_stl(f, [pts[5], pts[3], pts[1]], [0, 0,  1])
    
def main():
    grid = np.load(grid_filename)
    bbox = np.array([
        [-44.6405, -5.45846, -0.5715],
        [44.0995, 91.7702, 23.7998]
    ])
    filled_cells = np.column_stack(np.where(grid==1))
    with open(stl_filename, 'w') as f:
        f.write('solid grid\n')
        for cell in filled_cells:
            write_cube_stl(f, cell, bbox)
        f.write('endsolid\n')



if __name__ =='__main__':
    main()