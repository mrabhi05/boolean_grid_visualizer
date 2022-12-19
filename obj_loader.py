import numpy as np

class ObjLoader(object):
    def __init__(self, fileName):
        self.vertices = []
        self.faces = []
        ##
        try:
            f = open(fileName)
            for line in f:
                if line[:2] == "v ":
                    index1 = line.find(" ") + 1
                    index2 = line.find(" ", index1 + 1)
                    index3 = line.find(" ", index2 + 1)

                    vertex = [float(line[index1:index2]), float(line[index2:index3]), float(line[index3:-1])]
                    # vertex = (round(vertex[0], 2), round(vertex[1], 2), round(vertex[2], 2))
                    self.vertices.append(vertex)

                elif line[0] == "f":
                    line_data = line.replace("//", "/").rstrip().split(' ')[1:]
                    face = []
                    for item in line_data:
                        face.append(int(item.split('/')[0])-1)
                    self.faces.append(face)

            f.close()
            self.vertices = np.array(self.vertices)
            self.faces = np.array(self.faces)
        except IOError:
            print(".obj file not found.")