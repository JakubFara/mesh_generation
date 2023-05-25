import meshio
import numpy as np
import warnings
from dolfin import MPI


class MeshLoader():
    def __init__(self, filename: str, cell_type: str = 'triangle', comm=None):
        """
        This class is designed to create dolfin:Mesh from .msh mesh.
        Arguments:
            filename: str: Name of the file. Has to be in format .msh.
            cell_tyle: str: It works only for triangle mesh.
        """
        self.filename = filename
        self.cell_type = cell_type
        if cell_type == 'triangle':
            self.dim = 2
        else:
            self.dim = 3
        self.msh = meshio.read(filename)
        # get data of meshes
        self.triangle_data, self.line_data, self.vertex_data = self.data()
        self.triangle_cells, self.line_cells, self.vertex_cells = self.cells()
        # load xdmf meshes
        self.dolfin_mesh = self._load_dolfin_mesh()
        self.dolfin_line_mesh = self._load_line_dolfin_mesh()
        self.dolfin_vertex_mesh = self._load_vertex_dolfin_mesh()
        if comm is None:
            self.comm = MPI.comm_world
        else:
            self.comm = comm

    def _load_dolfin_mesh(self):
        if len(self.triangle_data) != 0:
            triangle_mesh = meshio.Mesh(
                points=self.msh.points[:, :self.dim],
                cells={self.cell_type: self.triangle_cells},
                cell_data={
                    "name_to_read": [self.triangle_data],
                }
            )
        else:
            triangle_mesh = meshio.Mesh(
                points=self.msh.points[:, :self.dim],
                cells={self.cell_type: self.triangle_cells},
            )

        meshio.write("cache/mesh.xdmf", triangle_mesh)
        from dolfin import XDMFFile, Mesh
        triangle_dolfin_mesh = Mesh()
        with XDMFFile("cache/mesh.xdmf") as infile:
            infile.read(triangle_dolfin_mesh)
        return triangle_dolfin_mesh

    def _load_line_dolfin_mesh(self):
        if len(self.line_cells) != 0:
            line_mesh = meshio.Mesh(
                points=self.msh.points[:, :self.dim],
                cells={'line': self.line_cells},
                cell_data={
                    "name_to_read": [self.line_data],
                }
            )
            from dolfin import XDMFFile, Mesh
            meshio.write("cache/line_mesh.xdmf", line_mesh)
            line_dolfin_mesh = Mesh()
            with XDMFFile("cache/line_mesh.xdmf") as infile:
                infile.read(line_dolfin_mesh)
            return line_dolfin_mesh
        return None

    def _load_vertex_dolfin_mesh(self):
        if len(self.vertex_cells) != 0:
            vertex_mesh = meshio.Mesh(
                points=self.msh.points[:, :self.dim],
                cells={'vertex': self.vertex_cells},
                cell_data={
                    "name_to_read": [self.vertex_data],
                }
            )
            from dolfin import XDMFFile, Mesh
            meshio.write("cache/vertex_mesh.xdmf", vertex_mesh)
            vertex_dolfin_mesh = Mesh()
            with XDMFFile("cache/line_mesh.xdmf") as infile:
                infile.read(vertex_dolfin_mesh)
            return vertex_dolfin_mesh
        return None

    def get_mesh_function(self, dim: int):
        if dim == self.dim:
            return self.cell_label()
        if dim == 1:
            return self.facet_label()

    def cell_label(self):
        from dolfin import XDMFFile, MeshValueCollection, cpp
        mvc = MeshValueCollection("size_t", self.dolfin_mesh, self.dim)
        # meshio.write("cache/mesh.xdmf", self.xdmf_mesh)
        with XDMFFile(self.comm, "cache/mesh.xdmf") as infile:
            infile.read(mvc, "name_to_read")
        mf = cpp.mesh.MeshFunctionSizet(self.dolfin_mesh, mvc)
        return mf

    def facet_label(self):
        if self.dolfin_line_mesh:
            from dolfin import XDMFFile, MeshValueCollection, cpp
            mvc = MeshValueCollection("size_t", self.dolfin_mesh, self.dim - 1)
            # meshio.write("cache/line_mesh.xdmf", self.xdmf_line_mesh)
            with XDMFFile(self.comm, "cache/line_mesh.xdmf") as infile:
                infile.read(mvc, "name_to_read")
            mf = cpp.mesh.MeshFunctionSizet(self.dolfin_mesh, mvc)
            return mf
        else:
            warnings.warn('No facet markers!')
            return None

    def vertex_label(self):
        if self.dolfin_line_mesh:
            from dolfin import XDMFFile, MeshValueCollection, cpp
            mvc = MeshValueCollection("size_t", self.dolfin_mesh, 0)
            # meshio.write("cache/line_mesh.xdmf", self.xdmf_line_mesh)
            with XDMFFile(self.comm, "cache/vertex_mesh.xdmf") as infile:
                infile.read(mvc, "name_to_read")
            mf = cpp.mesh.MeshFunctionSizet(self.dolfin_mesh, mvc)
            return mf
        else:
            warnings.warn('No facet markers!')
            return None

    def data(self):
        vertex_data = []
        line_data = []
        triangle_data = []
        cell_data_dict = self.msh.cell_data_dict["gmsh:physical"]
        for key in cell_data_dict.keys():
            if key == "vertex":
                if len(vertex_data) == 0:
                    vertex_data = cell_data_dict[key]
                else:
                    vertex_data = np.vstack(
                        [
                            vertex_data,
                            cell_data_dict[key]
                        ]
                    )
            if key == "line":
                if len(line_data) == 0:
                    line_data = cell_data_dict[key]
                else:
                    line_data = np.vstack(
                        [
                            line_data,
                            cell_data_dict[key]
                        ]
                    )
            elif key == self.cell_type:
                if len(triangle_data) == 0:
                    triangle_data = cell_data_dict[key]
                else:
                    triangle_data = np.vstack(
                        [
                            triangle_data,
                            cell_data_dict[key]
                        ]
                    )
        return triangle_data, line_data, vertex_data

    def cells(self):
        vertex_cells = []
        line_cells = []
        triangle_cells = []
        for cell in self.msh.cells:
            if cell.type == self.cell_type:
                if len(triangle_cells) == 0:
                    triangle_cells = cell.data
                else:
                    triangle_cells = np.vstack([triangle_cells, cell.data])
            elif cell.type == "line":
                if len(line_cells) == 0:
                    line_cells = cell.data
                else:
                    line_cells = np.vstack([line_cells, cell.data])
            elif cell.type == "vertex":
                if len(vertex_cells) == 0:
                    vertex_cells = cell.data
                else:
                    vertex_cells = np.vstack([vertex_cells, cell.data])
        return triangle_cells, line_cells, vertex_cells

    def save_data(self, name: str = 'mesh.h5'):
        facet_marker = self.facet_label()
        cell_marker = self.cell_label()
        from dolfin import HDF5File, MPI
        with HDF5File(MPI.comm_world, name, 'w') as hfile:
            hfile.write(self.dolfin_mesh, '/mesh')
            hfile.write(cell_marker, '/cell_marker')
            if facet_marker:
                hfile.write(facet_marker, '/facet_marker')
