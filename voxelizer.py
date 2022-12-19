import numpy as np
import json
import sys
import os
from obj_loader import ObjLoader
from subprocess import Popen, PIPE
from datetime import datetime
import base64
import copy
from itertools import product
import traceback

# sys.path += [ os.path.join(os.path.dirname(os.path.dirname(__file__)), 'call_python_version') ]
# import call_python_version as cpv


class GridOptions:
    def __init__(
        self, unit_scale=1, cell_size=1.00, half_width=None, 
        save_to_file=True, output_file_formats={ 'categorical': ['npy'] },
        grid_types=['categorical'], cell_category_levels= 6
    ):
        self.unit_scale = unit_scale
        self.cell_size = cell_size
        self.half_width = cell_size/2 if half_width is None else half_width
        self.grid_types = grid_types
        self.save_to_file = save_to_file
        self.output_file_formats = output_file_formats
        self.cell_category_levels = cell_category_levels

        

class Voxelizer:
    def __init__(self):
        self._grid_size = None
        self.grid = {}

        

    def load_grid(self, grid_file_names, bbox=None, options=GridOptions()):
        self.options = options
        if bbox is not None:
            self._bbox_org = bbox
        for item in self.options.grid_types:
            self.grid[item] = np.load(grid_file_names[item])
        self._grid_size = self.grid[self.options.grid_types[0]].shape
        return

    def create_grid(self, input_file, options=GridOptions(), category_level=1):
        self.options = options

        self._openvdbscript_filepath = '/mnt/d/CCTech/GDPipes/design-explorer-server/libraries/voxelizer/openvdb_functions.py' # Needs to be changed later
        
        
        self._points_filepath = os.path.join(os.path.dirname(__file__), 'grid_data/points.npy')
        self._triangles_filepath = os.path.join(os.path.dirname(__file__), 'grid_data/triangles.npy')
        self._half_width_filepath = os.path.join(os.path.dirname(__file__), 'grid_data/half_width.npy')
        self._grid_size_filepath = os.path.join(os.path.dirname(__file__), 'grid_data/grid_size.npy')

        self._grid_output_filepath = os.path.join(os.path.dirname(__file__), 'grid_data/grid_output.npy')


        mesh_data = ObjLoader(input_file)
        self._points_org = mesh_data.vertices
        self._triangles = mesh_data.faces

        self._bbox_org = np.array([ np.amin(self._points_org, axis=0), np.amax(self._points_org, axis=0) ])
        points = self._points_org - self._bbox_org[0]
        points *= self.options.unit_scale
        bbox = np.array([ np.amin(points, axis=0), np.amax(points, axis=0) ])

        points /= self.options.cell_size
        self._grid_size = np.ceil( (bbox[1] - bbox[0])/self.options.cell_size )
        
        self._grid_size = self._grid_size.astype(int)
        print('grid_size', self._grid_size)

       
        np.save(self._points_filepath, points)
        np.save(self._triangles_filepath, self._triangles)
        np.save(self._half_width_filepath, self.options.half_width)
        np.save(self._grid_size_filepath, self._grid_size)
       

        cmd_list_openvdb = [
                        'python2.7',
                        '-u',
                        self._openvdbscript_filepath,
                        self._points_filepath,
                        self._triangles_filepath,
                        self._half_width_filepath,
                        self._grid_size_filepath,
                        self._grid_output_filepath
                        ]

        v = Popen(cmd_list_openvdb, stdout=PIPE)


        lines = []
        time_last = datetime.now()
        while v.poll() == None:
            line = v.stdout.readline()
            if not line:
                break
            line = line.decode('utf-8').rstrip()
            print(line)
            lines.append(line)
            time_now = datetime.now()
            time_diff = time_now - time_last
            if time_diff.seconds > 1:
                #self._job_cb.cbfn_eval_progress(lines)
                lines = []
                time_last = datetime.now()

        ret_code = v.wait()
        if ret_code == 0:
            grid_output = np.load(self._grid_output_filepath, allow_pickle=True)

        else:
            raise Exception('Exception occurred in running pyopenvdb, return code is:', ret_code)

        
        self.grid['float'] =  grid_output 
        if 'bool' in self.options.grid_types:
            self.grid['bool'] = np.where(abs(self.grid['float']) != self.options.half_width, True, False)
        if 'categorical' in self.options.grid_types:
            self.grid['categorical'] = np.where(abs(self.grid['float'] - self.options.half_width) > 1e-6, category_level, 0)

        np.save("/mnt/d/CCTech/GDPipes/design-explorer-server-1/worker/data/grid_0_5.npy",self.grid['categorical'])

        if self.options.save_to_file:
            working_dir = os.path.dirname(input_file)
            filename_wo_ext = os.path.join(working_dir, os.path.splitext(os.path.basename(input_file))[0])
            for key, val in self.options.output_file_formats.items():
                for item in val:
                    filename = f'{filename_wo_ext}_grid_{key}_{self.options.cell_size}.{item}'
                    if item == 'npy':
                        np.save(filename, self.grid[key])
                    elif item == 'json':
                        with open(filename, 'w') as f:
                            json.dump(self.grid[key].tolist(), f)
                    elif item == 'stl':
                        self._grid_to_stl(key, filename)
        return

    def _grid_to_stl(self, grid_type, filename_obj):
        grid = self.grid[grid_type]
        size = self.options.cell_size / self.options.unit_scale
        bb_min = self._bbox_org[0]
        if grid_type == 'categorical':
            filled_idx_list = np.argwhere(grid==1)
        else:
            raise Exception('Not implemented')
        
        v_list = []
        tn_list = [
            [-1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, -1.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ]
        for i in range(len(filled_idx_list)):
            loc_v_list = []
            for x in range(2):
                for y in range(2):
                    for z in range(2):
                        loc_v_list.append([
                            bb_min[0] + ((filled_idx_list[i][0] + x - 0.5) * size),
                            bb_min[1] + ((filled_idx_list[i][1] + y - 0.5) * size), 
                            bb_min[2] + ((filled_idx_list[i][2] + z - 0.5) * size),
                        ])
            
            v_list.append(loc_v_list[ 0 ])
            v_list.append(loc_v_list[ 3 ])
            v_list.append(loc_v_list[ 2 ])
            v_list.append(loc_v_list[ 0 ])
            v_list.append(loc_v_list[ 1 ])
            v_list.append(loc_v_list[ 3 ])

            v_list.append(loc_v_list[ 0 ])
            v_list.append(loc_v_list[ 4 ])
            v_list.append(loc_v_list[ 5 ])
            v_list.append(loc_v_list[ 0 ])
            v_list.append(loc_v_list[ 5 ])
            v_list.append(loc_v_list[ 1 ])

            v_list.append(loc_v_list[ 0 ])
            v_list.append(loc_v_list[ 6 ])
            v_list.append(loc_v_list[ 4 ])
            v_list.append(loc_v_list[ 0 ])
            v_list.append(loc_v_list[ 2 ])
            v_list.append(loc_v_list[ 6 ])

            v_list.append(loc_v_list[ 1 ])
            v_list.append(loc_v_list[ 5 ])
            v_list.append(loc_v_list[ 7 ])
            v_list.append(loc_v_list[ 1 ])
            v_list.append(loc_v_list[ 7 ])
            v_list.append(loc_v_list[ 3 ])

            v_list.append(loc_v_list[ 4 ])
            v_list.append(loc_v_list[ 6 ])
            v_list.append(loc_v_list[ 7 ])
            v_list.append(loc_v_list[ 4 ])
            v_list.append(loc_v_list[ 7 ])
            v_list.append(loc_v_list[ 5 ])

            v_list.append(loc_v_list[ 2 ])
            v_list.append(loc_v_list[ 3 ])
            v_list.append(loc_v_list[ 7 ])
            v_list.append(loc_v_list[ 2 ])
            v_list.append(loc_v_list[ 7 ])
            v_list.append(loc_v_list[ 6 ])

        with open(filename_obj, 'w') as f:
            f.write('solid name\n')
            for i in range(0, len(v_list), 3):
                f.write(f'facet normal 0.0 0.0 1.0\n')
                f.write('    outer loop\n')
                f.write(f'        vertex {v_list[i][0]} {v_list[i][1]} {v_list[i][2]}\n')
                f.write(f'        vertex {v_list[i+1][0]} {v_list[i+1][1]} {v_list[i+1][2]}\n')
                f.write(f'        vertex {v_list[i+2][0]} {v_list[i+2][1]} {v_list[i+2][2]}\n')
                f.write('    endloop\n')
                f.write('endfacet\n')
            f.write('endsolid name')

    def points_to_cells(self, pts):
        cell_size = self.options.cell_size / self.options.unit_scale
        pts_length = pts - (self._bbox_org[0] - cell_size/2)
        cell_list = np.floor(pts_length / cell_size).astype(int)
        return cell_list

    def cells_to_points(self, cells):
        cell_size = self.options.cell_size / self.options.unit_scale
        pts = self._bbox_org[0] + (cells * cell_size)
        return pts

    ''' Categorical Grid Functions '''

    def update_cells(self, cells, fill=True, category_level=2):
        if len(cells) != 0:
            fill_val = category_level if fill else 0
            self.grid['categorical'][cells[:,0], cells[:,1], cells[:,2]] = fill_val

    def fill_cells(self, cells, category_level=2):
        cells_cpy=np.copy(cells)
        count = 0
        for i,cell in enumerate(cells_cpy):
            if self.grid['categorical'][tuple(cell)] == 4:
                cells = np.delete(cells, i-count,axis=0)
                count= count + 1 
        self.update_cells(cells, category_level=2)

    def unfill_cells(self, cells):
        self.update_cells(cells, fill=False)

    def unfill_category(self, category_level=2):
        self.grid['categorical'][np.where(self.grid['categorical'] == category_level)] = 0
    
    def fill_the_surrounding_for_cell(self, cell, direction, tillLevel=0, isPlanarFill=True):
        indexes_tobe_changed = []
        temp_cleared_direction = copy.deepcopy(direction)
        for idx, cell_value in enumerate(direction):
            if cell_value == 0:
                indexes_tobe_changed.append(idx)
            else:
                temp_cleared_direction[idx] = 0

        possible_dir_set_values = []
        possible_vars_in_dir = [0]
        for level in range(1, tillLevel+1):
            possible_vars_in_dir.append(level)
            possible_vars_in_dir.append(-level)
        
        possible_vars_in_dir = set(possible_vars_in_dir)
        possible_dir_set_values = list(product(possible_vars_in_dir, repeat=2))

        new_dir_set = []
        if isPlanarFill:
            for dir_values in possible_dir_set_values:
                new_dir = np.copy(temp_cleared_direction)
                for idx, index in enumerate(indexes_tobe_changed):
                    new_dir[index] = dir_values[idx]
                    
                new_dir_set.append(new_dir)
        else:
            # TODO - write code for cube fill
            pass

        for dirtn in new_dir_set:
            new_cell = cell + dirtn
            if self.grid['categorical'][tuple(new_cell)] == 0:
                self.grid['categorical'][tuple(new_cell)] = 3

    def _fill_port_beginnings(self, piping_input, catalog):
        try:
            for idx, port in enumerate(piping_input['port_set_cells']):
                riser_length = piping_input['port_set_gland_length'][idx] + piping_input['port_set_ext_len'][idx]
                riser_cell_count = np.floor(riser_length / self.options.cell_size).astype(int)
                increment_by = 1
                incremented_port = port + np.array([0,0,0])
                grid_1d_len, grid_2d_len, grid_3d_len = self.grid['categorical'].shape

                for index in range(riser_cell_count + 1):
                    isBreakeTheLoop = False
                    if incremented_port[0] < grid_1d_len and incremented_port[1] < grid_2d_len and incremented_port[2] < grid_3d_len:
                        if index < riser_cell_count:
                            self.grid['categorical'][tuple(incremented_port)] = 3
                            self.fill_the_surrounding_for_cell(incremented_port, piping_input['port_set_directions'][idx], 1, True)
                        else:
                            self.grid['categorical'][tuple(incremented_port)] = 4
                    else:
                        isBreakeTheLoop = True

                    if isBreakeTheLoop:
                        decremented_port = incremented_port - piping_input['port_set_directions'][idx]
                        self.grid['categorical'][tuple(decremented_port)] = 4
                        break
                    incremented_port = incremented_port + piping_input['port_set_directions'][idx]
        except:
            traceback.print_exc()
    
    def _create_and_fill_prev_paths(self,pathData):
        try:
            pathlist_to_persist=[]
            for pipe in pathData:
                Pipe = [] 
                for branch in pipe:
                    Branch=[]
                    for indx,cell in enumerate(branch[:-1]):
                        start_cell =  self.points_to_cells(cell)
                        end_cell = self.points_to_cells(branch[indx+1])
                        direction = np.subtract(end_cell,start_cell)
                        direction = direction / np.linalg.norm(direction)
                        end_cell_temp = np.subtract(end_cell,direction).astype(int)  
                        while not np.array_equal(end_cell_temp,start_cell):
                            self.grid['categorical'][tuple(start_cell)] = 1
                            # print(start_cell.tolist())
                            start_cell = np.add(start_cell,direction).astype(int)
                            Branch.append(start_cell)
                    Pipe.append(np.array(Branch))
                pathlist_to_persist.append(Pipe)            
            return np.array(pathlist_to_persist)                      
        except:
            traceback.print_exc()
            return False
        

