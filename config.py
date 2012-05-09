import os

from flask import *

app = Flask(__name__)
app.debug = True

# import os; os.urandom(24)
app.secret_key = '\xcb\x0e={\xa6\x83y1\x04\x87T\x01\xe7\xa2\xc2\xa0\x8e\xc8\xc6\xa5\x84\x18\xaa\x9a'

FILENAME = 'plot.png'

DEFAULTS = {
    'usq_x':      '10',
    'usq_y':      '10',
    'modulus':    '10.0',
    'poisson':    '0.3',
    'body_x':     '0.0',
    'body_y':     '-0.5',
    'traction_x': '0.1',
    'traction_y': '0.0',
    'contours':   '100',
    'left_x':     '0.0',
    'left_y':     '0.0',
    'right_x':    '0.0',
    'right_y':    'sin(pi) + x[0]',
}

# Enable cache-busting static files on dev
# http://flask.pocoo.org/snippets/40/
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
