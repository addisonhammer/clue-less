import logging
import random

import flask
app = flask.Flask(__name__)

NAMES = (
    'Prof. Plum',
    'Mrs. White',
    'Col. Mustard',
    'Miss Scarlet',
    'Mrs. Peacock',
    'Mr. Green',
)

WEAPONS = (
    'Revolver',
    'Dagger',
    'Lead Pipe',
    'Rope',
    'Candlestick',
    'Wrench',
)

ROOMS = (
    'Study',
    'Hall',
    'Lounge',
    'Library',
    'Billiard Room',
    'Dining Room',
    'Ballroom',
    'Kitchen',
    'Conservatory',
)

@app.route('/')
def index():
    clue_url = flask.url_for('clue')
    return f'This is the index, try <a href="{clue_url}">Clue</a> instead'

@app.route('/clue', methods=['POST', 'GET'])
def clue():
    if flask.request.method == 'POST':
        logging.info('POST call, serving ACCUSE template')
        return flask.render_template(
            'clue.html.jinja',
            whodoneit=True,
            username=flask.request.form['username'],
            name=random.choice(NAMES),
            room=random.choice(ROOMS),
            weapon=random.choice(WEAPONS),
        )
    else:
        logging.info('GET call, serving GUESS template')
        return flask.render_template('clue.html.jinja', whodoneit=False)

if __name__ == '__main__':
    app.run()
    app.secret_key == u'yolo'