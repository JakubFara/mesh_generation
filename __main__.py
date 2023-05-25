from generate_mesh import MeshLoader


def cibule_fsi():
    cell_type = 'triangle'
    filename = 'gmsh/data/cibule_fsi_mesh.msh'
    name = 'cibule_fsi'
    mesh_loader = MeshLoader(filename, cell_type)
    mesh_loader.save_data(f'data/{name}.h5')


def sphere_in_cube():
    cell_type = 'tetra'
    filename = 'gmsh/data/sphere_in_cube.msh'
    name = 'sphere_in_cube'
    mesh_loader = MeshLoader(filename, cell_type)
    mesh_loader.save_data(f'data/{name}.h5')


def turekhron():
    cell_type = 'triangle'
    filename = 'gmsh/data/turekrhon.msh'
    name = 'turekhron'
    mesh_loader = MeshLoader(filename, cell_type)
    mesh_loader.save_data(f'data/{name}.h5')


if __name__ == "__main__":
    cibule_fsi()
    sphere_in_cube()
    turekhron()
