import sys
import gmsh

r = 0.2
gmsh.initialize()
dim = 3

# Choose if Gmsh output is verbose
gmsh.option.setNumber("General.Terminal", 0)
model = gmsh.model()
model.add("Sphere")
model.setCurrent("Sphere")

# Generate a mesh using Gmsh
model.add("Sphere minus box")
model.setCurrent("Sphere minus box")

sphere_dim_tags = model.occ.addSphere(0.5, 0.5, 0.5, r, 5)
box_dim_tags = model.occ.addBox(0, 0, 0, 1, 1, 1)
model_dim_tags = model.occ.cut([(3, box_dim_tags)], [(
    3, sphere_dim_tags)], removeObject=True, removeTool=False)[0][0][1]

model.occ.synchronize()

model.addPhysicalGroup(3, [sphere_dim_tags], tag=2)
model.addPhysicalGroup(3, [model_dim_tags], tag=1)
# model.addPhysicalGroup(3, [3], tag=1)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.1)
model.setPhysicalName(3, 2, "Sphere volume")

model.mesh.generate(dim=3)

gmsh.write("data/sphere_in_cube.msh")

# Inspect the log:
log = gmsh.logger.get()
print("Logger has recorded " + str(len(log)) + " lines")
gmsh.logger.stop()

# Launch the GUI to see the results:
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
