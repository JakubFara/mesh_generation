import gmsh
import sys

gmsh.initialize()


h = 0.02
myhext = h
myhprecis = myhext/16.

L = 2.5
W = 0.41
cx = 0.2
cy = 0.2
L_struct = 0.35101
W_struct = 0.02
r = 0.05
eps = 0.0

factory = gmsh.model.geo

outer_points = [
   factory.add_point(0., 0., 0., myhext),
   factory.add_point(L, 0., 0., myhext),
   factory.add_point(L, W, 0., myhext),
   factory.add_point(0., W, 0., myhext)
]

outer_lines = [
   factory.add_line(outer_points[0], outer_points[1]),
   factory.add_line(outer_points[1], outer_points[2]),
   factory.add_line(outer_points[2], outer_points[3]),
   factory.add_line(outer_points[3], outer_points[0])
]

inner_points = [
    factory.add_point(cx, cy, 0., myhprecis, 21),
    factory.add_point(0.6 - L_struct, 0.19, 0., myhprecis, 22),
    factory.add_point(0.6 - L_struct, 0.19 + W_struct, 0., myhprecis, 23),
    factory.add_point(cx-r, cy, 0., myhprecis, 24),
    factory.add_point(0.6-eps, 0.19, 0., myhprecis),
    factory.add_point(0.6-eps, 0.19 + W_struct, 0., myhprecis),
    factory.add_point(0.6, 0.19+W_struct/2., 0, myhprecis),
]

# Gmsh provides other curve primitives than straight lines: splines, B-splines,
# circle arcs, ellipse arcs, etc. Here we define a new circle arc, starting at
# point 14 and ending at point 16, with the circle's center being the point 15:
# factory.addCircleArc(14, 15, 16, 3)
c1 = factory.addCircleArc(inner_points[2], inner_points[0], inner_points[3])
c2 = factory.addCircleArc(inner_points[3], inner_points[0], inner_points[1])
c3 = factory.addCircleArc(inner_points[2], inner_points[0], inner_points[1])
# FSI interface
interface_lines = [
    factory.add_line(inner_points[1], inner_points[4]),
    factory.add_line(inner_points[4], inner_points[6]),
    factory.add_line(inner_points[6], inner_points[5]),
    factory.add_line(inner_points[5], inner_points[2]),
]

# surface structure

loop1 = factory.add_curve_loop(outer_points)
loop2 = factory.add_curve_loop([c1, c2] + interface_lines)
loop3 = factory.add_curve_loop([c3] + interface_lines)
gmsh.model.geo.addPlaneSurface([loop1, loop2], 1)
gmsh.model.geo.addPlaneSurface([loop3], 2)

gmsh.model.geo.synchronize()
gmsh.model.addPhysicalGroup(1, [outer_lines[0], outer_lines[2]], 3)  # wall
gmsh.model.addPhysicalGroup(1, [outer_lines[1]], 2)  # outflow
gmsh.model.addPhysicalGroup(1, [outer_lines[3]], 1)  # inflow
gmsh.model.addPhysicalGroup(1, [c1, c2, c3], 4)  # inflow
gmsh.model.addPhysicalGroup(1, interface_lines, 5)  # interface

gmsh.model.geo.synchronize()

gmsh.model.mesh.generate(2)
# gmsh.model.mesh.generate(1)
# Write mesh data:
gmsh.write("data/turekhron.msh")

# Creates  graphical user interface
if 'close' not in sys.argv:
    gmsh.fltk.run()

# It finalize the Gmsh API
gmsh.finalize()
