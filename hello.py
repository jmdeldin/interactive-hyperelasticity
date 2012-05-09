from dolfin import Expression
import matplotlib.pyplot as plt
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
    mesh, u, V = hyper.hyper(mesh_dims=(usq_x, usq_y), E=E, nu=nu, B=B, T=T, c=c, r=r)
    return (mesh, u)

def plot_svg(mesh, u, contours):
    x = mesh.coordinates()[:,0]
    y = mesh.coordinates()[:,1]
    triangles = mesh.cells()
    z = u.vector().array()
    # hack, since u is 2x size
    z = z[0:x.shape[0]]

    plt.clf()
    plt.tricontourf(x,y,triangles,z)
    plt.colorbar()
    plt.savefig('static/plot.svg', bbox_inches='tight', transparent=True)

@app.route('/')
def index():
    return render_template('index.html', filename=FILENAME, _=DEFAULTS)

@app.route('/update_plot', methods=['POST'])
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
        plot_svg(mesh, u, posted['contours'])
        flash('Plot updated!', 'success')
    except IOError as (errno, errstr):
        flash('Unable to save SVG: %s' % errstr, 'error')

    return render_template('index.html', filename=FILENAME, _=posted)

if __name__ == '__main__':
    # host=0.0.0.0 lets this run on the network
    app.run(host='0.0.0.0')
