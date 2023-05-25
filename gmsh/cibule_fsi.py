import gmsh
import sys
from cibuleshape import Shape_New
import numpy as np


# Initialize gmsh:
gmsh.initialize()

lev = 2
R = 0.016  # 0.020
lc = 3e-4
if lev == 1:
    lc = 6e-4
    num = 60
elif lev == 2:
    lc = 3e-4
    num = 80
# Create mesh
Len = 0.022
Len_sin = 0.012
Win = 0.012
Wout = 0.013  # 0.013
valve_start = 0.0092
valve_end = 0.0096
dy_valve = 0.001
dx_valve = 0.001
size_valve = 0.002
# R = float(sys.argv[1])

dx = 0.0005

cibule = Shape_New(Len, Len_sin, Win, Wout, R, dx)

zz = np.linspace(-Len_sin, Len_sin+dx, num=num)
rr = np.array([cibule.shape(z) for z in zz])

# points
p1x = Win
p1y = -Len + valve_end

p3x = Win
p3y = -Len + valve_start

points_outer = [
    gmsh.model.geo.add_point(0, -Len, 0, lc),
    gmsh.model.geo.add_point(Win, -Len, 0, lc),
    gmsh.model.geo.add_point(Win + size_valve, -Len, 0, lc),
    gmsh.model.geo.add_point(Win + size_valve, p3y, 0, lc),
    gmsh.model.geo.add_point(Win + size_valve, p1y, 0, lc),
]
for i, p in enumerate(zz):
    points_outer.append(
        gmsh.model.geo.add_point(rr[i] + size_valve, zz[i], 0, lc)
    )

# points.append(gmsh.model.geo.add_point(Wout, Len, 0, lc))
points_outer.extend([
    gmsh.model.geo.add_point(Wout + size_valve, Len, 0, lc),
    gmsh.model.geo.add_point(Wout, Len, 0, lc),
    gmsh.model.geo.add_point(0, Len, 0, lc)
])

# lines
lines_outer = []
point0 = points_outer[0]
for point in points_outer[1:]:
    lines_outer.append(gmsh.model.geo.add_line(point0, point))
    point0 = point
lines_outer.append(gmsh.model.geo.add_line(point0, points_outer[0]))


points_inner = [
    points_outer[0],
    points_outer[1],
    gmsh.model.geo.add_point(p3x, p3y, 0, lc),
    gmsh.model.geo.add_point(p1x, p1y, 0, lc),
]
for i, p in enumerate(zz):
    points_inner.append(gmsh.model.geo.add_point(rr[i], zz[i], 0, lc))

# points.append(gmsh.model.geo.add_point(Wout, Len, 0, lc))
points_inner.extend([
    # gmsh.model.geo.add_point(Wout, Len, 0, lc),
    points_outer[-2],
    points_outer[-1]
])

# lines
lines_inner = [lines_outer[0]]
point0 = points_inner[1]
for point in points_inner[2: -1]:
    lines_inner.append(gmsh.model.geo.add_line(point0, point))
    point0 = point
# lines_inner.append(gmsh.model.geo.add_line(point0, points_inner[0]))
lines_inner.append(lines_outer[-2])
lines_inner.append(lines_outer[-1])
face_outer = gmsh.model.geo.add_curve_loop(lines_outer)
# face_outer = gmsh.model.geo.add_curve_loop(lines_outer)
face_inner = gmsh.model.geo.addCurveLoop(lines_inner)

gmsh.model.geo.addPlaneSurface([face_inner, face_outer], 2)
gmsh.model.geo.addPlaneSurface([face_inner], 1)


# gmsh.model.addPhysicalGroup(1, [face_valve], 3)
gmsh.model.geo.synchronize()
gmsh.model.addPhysicalGroup(1, [lines_outer[0]], 1)  # inflow
gmsh.model.addPhysicalGroup(1, [lines_outer[1]], 2)  # inflow wall
gmsh.model.addPhysicalGroup(1, lines_inner[1: -2], 3)  # interface
gmsh.model.addPhysicalGroup(1, [lines_inner[-2]], 4)  # outflow wall
gmsh.model.addPhysicalGroup(1, [lines_inner[-1]], 5)  # outflow wall
gmsh.model.addPhysicalGroup(1, [lines_outer[-3]], 6)  # outflow wall
gmsh.model.geo.synchronize()

gmsh.model.addPhysicalGroup(2, [2], 2)
gmsh.model.addPhysicalGroup(2, [1], 1)
gmsh.model.geo.synchronize()
# gmsh.model.geo.synchronize()
# Generate mesh:
# gmsh.model.mesh.generate(1)

gmsh.model.mesh.generate(2)
# gmsh.model.mesh.generate(1)
# Write mesh data:
gmsh.write("data/cibule_fsi_mesh.msh")

# Creates  graphical user interface
if 'close' not in sys.argv:
    gmsh.fltk.run()

# It finalize the Gmsh API
gmsh.finalize()
