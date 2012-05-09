# TODO: include GPL header from demo
from dolfin import *
import matplotlib.pyplot as plt

def parse_boundaries(from_str):
    pass
    # s = from_str.replace('', '')

def make_mesh_and_funcspace(horiz, vert):
    """Creates mesh and defines function space."""
    mesh = UnitSquare(horiz, vert)
    V = VectorFunctionSpace(mesh, 'Lagrange', 1)
    return (mesh, V)

def boundaries(V, c, r):
    # Mark boundary subdomians
    left, right = compile_subdomains([
            "(std::abs(x[0])       < DOLFIN_EPS) && on_boundary",
            "(std::abs(x[0] - 1.0) < DOLFIN_EPS) && on_boundary"])

    # Define Dirichlet boundary (x = 0 or x = 1)
    bcl = DirichletBC(V, c, left)
    bcr = DirichletBC(V, r, right) # FIXME: just made it the same
    bcs = [bcl, bcr]

    return bcs

def get_body_force(x, y):
    """Body force per unit volume"""
    return Constant((x, y))
def get_traction_force(x, y):
    """Traction force on the boundary"""
    return Constant((x, y))

def hyper(mesh_dims=(4, 4), E=10.0, nu=0.3, B=(0.0, -0.5), T=(0.1, 0.0), c=Expression(("0.0", "0.0")), r=Expression(("0.0", "0.0"))):
    mesh, V = make_mesh_and_funcspace(mesh_dims[0], mesh_dims[1])

    du = TrialFunction(V)            # Incremental displacement
    v  = TestFunction(V)             # Test function
    u  = Function(V)                 # Displacement from previous iteration
    B  = Constant(B) # Body force per unit volume
    T  = Constant(T) # Traction force on the boundary

    # Kinematics
    I = Identity(V.cell().d)    # Identity tensor
    F = I + grad(u)             # Deformation gradient
    C = F.T*F                   # Right Cauchy-Green tensor

    # Invariants of deformation tensors
    Ic = tr(C)
    J  = det(F)

    mu, lmbda = Constant(E/(2*(1 + nu))), Constant(E*nu/((1 + nu)*(1 - 2*nu)))

    # Stored strain energy density (compressible neo-Hookean model)
    psi = (mu/2)*(Ic - 3) - mu*ln(J) + (lmbda/2)*(ln(J))**2

    # Total potential energy
    Pi = psi*dx - dot(B, u)*dx - dot(T, u)*ds

    # Compute first variation of Pi (directional derivative about u in the direction of v)
    F = derivative(Pi, u, v)

    # Compute Jacobian of F
    J = derivative(F, u, du)

    # Solve variational problem
    # Optimization options for the form compiler
    parameters["form_compiler"]["cpp_optimize"] = True
    ffc_options = {"optimize": True, \
               "eliminate_zeros": True, \
               "precompute_basis_const": True, \
               "precompute_ip_const": True}

    solve(F == 0, u, boundaries(V, c, r), J=J,
          form_compiler_parameters=ffc_options)

    return [mesh, u, V]

def do_plot(mesh, u, contours=10, axis=None):
    x = mesh.coordinates()[:,0]
    y = mesh.coordinates()[:,1]
    triangles = mesh.cells()
    z = u.vector().array()
    # hack, since u is 2x size
    z = z[0:x.shape[0]]

    if axis == None:
        axis = plt.gca()
    return axis.tricontourf(x, y, triangles, z, contours)

# scratch
# http://fenicsproject.org/documentation/dolfin/1.0.0/python/programmers-reference/functions/function/Function.html
# def plot_deformation(mesh, u):
# ux, uy = map(lambda sub: sub.vector().array(), u.split(deepcopy=True))
# coords = mesh.coordinates().copy()
# xold, yold = coords[:,0], coords[:,1]
# xnew, ynew = xold - ux, yold - uy

# plt.plot(xold, yold, 'k-', alpha=0.6)
# plt.plot(xnew, ynew, 'r-')

# vertices = [
#     (xold[0], yold[0]), # left, bot
#     (xold[-5], yold[-5]), # left, top
#     (xold[-1], yold[-1]), # right, top
#     (xold[4], yold[4]), # right, bot
#     # close?
#     (0.0, 0.0),
#    ]
# newverts = [
#     (xnew[0], ynew[0]), # left, bot
#     (xnew[-5], ynew[-5]), # left, top
#     (xnew[-1], ynew[-1]), # right, top
#     (xnew[4], ynew[4]), # right, bot
#     # close?
#     (0.0, 0.0),
#    ]

# def plot_box(vertices):
#     codes = [
#         Path.MOVETO,
#         Path.LINETO,
#         Path.LINETO,
#         Path.LINETO,
#         Path.CLOSEPOLY,
#         ]
#     path = Path(vertices, codes)
#     fig = plt.figure()
#     ax = fig.add_subplot(111)
#     patch = patches.PathPatch(path, facecolor='red', lw=2)
#     ax.add_patch(patch)
#     ax.set_xlim(-4,4)
#     ax.set_ylim(-4,4)
# plt.show()

if __name__ == '__main__':
    print "running defaults"
    exp = Expression(("0.0", "sin(x[0])"))
    mesh, u, V = hyper(r=exp)
    do_plot(mesh, u)
    plt.show()
