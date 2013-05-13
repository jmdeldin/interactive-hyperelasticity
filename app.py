import os

from dolfin import Expression
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np

from config import *
import hyper

def solve(opts):
    """Solves the hyperelastic problem based on a dictionary of values"""
    usq_x, usq_y = opts['usq_x'], opts['usq_y']
    E = opts['modulus']
    nu = opts['poisson']
    B = (opts['body_x'], opts['body_y'])
    T = (opts['traction_x'], opts['traction_y'])
    c = Expression((opts['left_x'], opts['left_y']))
    r = Expression((opts['right_x'], opts['right_y']))
    print E
    mesh, u, V = hyper.hyper(mesh_dims=(usq_x, usq_y), E=E, nu=nu, B=B, T=T, c=c, r=r)
    return (mesh, u)

def plot_svg(mesh, u, contours, usq_x, usq_y):
    # split u into X and Y dim arrays
    ux, uy = map(lambda sub: sub.vector().array(), u.split(deepcopy=True))
    coords = mesh.coordinates().copy()
    xold, yold = coords[:,0], coords[:,1]
    xnew, ynew = xold - ux, yold - uy

    plt.clf()
    # size -- dpi => num px
    fig = plt.figure(figsize=(10,10), dpi=96)
    ax1 = fig.add_subplot(211)
    # fig.subplots_adjust(hspace=0.3, wspace=0.3)

    # triangle plot
    triangles = mesh.cells()
    z = u.vector().array()
    # hack, since u is 2x size
    z = z[0:xold.shape[0]]

    tri = ax1.tricontourf(xold, yold, triangles, z, contours)
    fig.colorbar(tri, ax=ax1, orientation='vertical')
    plt.title('Solution')
    # deformation plot
    ax2 = fig.add_subplot(223)
    ax2.plot(xold, yold, 'ko-', label='original')
    ax2.plot(xnew, ynew, 'ro-', alpha=0.6, label='deformed')
    stackx = np.vstack([xold, xnew])
    stacky = np.vstack([yold, ynew])
    minx = np.min(stackx)-0.25
    maxx = np.max(stackx)+0.25
    miny = np.min(stacky)-0.25
    maxy = np.max(stacky)+0.25
    ax2.set_xlim([minx, maxx])
    ax2.set_ylim([miny, maxy])
    ax2.legend(loc='lower left', prop={'size': 7}, ncol=2)
    plt.title('Deformed Outline')

    # shapes
    left_bound_idx = -usq_x - 1 # e.g., 4 => 5
    print left_bound_idx
    right_bound_idx = usq_x
    print right_bound_idx
    old_vertices = [
        (xold[0], yold[0]), # left, bot
        (xold[left_bound_idx], yold[left_bound_idx]), # left, top
        (xold[-1], yold[-1]), # right, top
        (xold[right_bound_idx], yold[right_bound_idx]), # right, bot
        (0.0, 0.0), # close
        ]
    new_vertices = [
        (xnew[0], ynew[0]), # left, bot
        (xnew[left_bound_idx], ynew[left_bound_idx]), # left, top
        (xnew[-1], ynew[-1]), # right, top
        (xnew[right_bound_idx], ynew[right_bound_idx]), # right, bot
        (0.0, 0.0), # close
        ]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY,
        ]
    old_path = Path(old_vertices, codes)
    new_path = Path(new_vertices, codes)
    ax3 = fig.add_subplot(224)
    ax3.add_patch(patches.PathPatch(old_path, facecolor='black', alpha=0.4, lw=2))
    ax3.add_patch(patches.PathPatch(new_path, facecolor='red', alpha=0.4, lw=2))
    ax3.set_xlim([minx, maxx])
    ax3.set_ylim([miny, maxy])
    plt.title('Deformed Shape')

    if os.path.isfile('static/plot.png'):
        os.rename('static/plot.png', 'static/last_plot.png')
    plt.savefig('static/plot.png', bbox_inches='tight', transparent=True)

@app.route('/')
def index():
    return render_template('index.html', filename=FILENAME, _=DEFAULTS)

@app.route('/update_plot', methods=['POST', 'GET'])
def update_plot():
    get_float = lambda key: request.form.get(key, DEFAULTS[key], type=float)
    get_str   = lambda key: request.form.get(key, DEFAULTS[key], type=str)
    posted               = DEFAULTS.copy()
    posted['usq_x']      = int(get_float('usq_x'))
    posted['usq_y']      = int(get_float('usq_y'))
    posted['modulus']    = get_float('modulus')
    posted['poisson']    = get_float('poisson')
    posted['body_x']     = get_float('body_x')
    posted['body_y']     = get_float('body_y')
    posted['traction_x'] = get_float('traction_x')
    posted['traction_y'] = get_float('traction_y')
    posted['left_x']     = get_str('left_x')
    posted['left_y']     = get_str('left_y')
    posted['right_x']    = get_str('right_x')
    posted['right_y']    = get_str('right_y')
    posted['contours']   = int(get_float('contours'))

    try:
        mesh, u = solve(posted)
    except Exception as ex:
        flash('DOLFIN Error: %s' % ex, 'error')
        return render_template('index.html', filename=FILENAME, _=posted)

    try:
        plot_svg(mesh, u, posted['contours'], posted['usq_x'], posted['usq_y'])
        flash('Plot updated!', 'success')
    except IOError as (errno, errstr):
        flash('Unable to save SVG: %s' % errstr, 'error')

    return render_template('index.html', filename=FILENAME, last_file='last_plot.png', _=posted)

if __name__ == '__main__':
    # host=0.0.0.0 lets this run on the network
    app.run(host='0.0.0.0')
