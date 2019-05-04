from flask import Flask, render_template, make_response, request, redirect, url_for
from pymacaroons import Macaroon, Verifier
from pymacaroons.exceptions import MacaroonInvalidSignatureException
app = Flask(__name__)

# Keys for signing macaroons are associated with some identifier for later
# verification. This could be stored in a database, key value store,
# memory, etc.
keys = {
    'key-for-bob': 'asdfasdfas-a-very-secret-signing-key'
}



@app.route('/')
def start():
    return render_template('auth_demo.html')


@app.route('/get_macaroon')
def get_macaroon():
    m = Macaroon(
        location='cool-picture-service.example.com',
        identifier='key-for-bob',
        key=keys['key-for-bob'])
    # Add a caveat for the target service
    m.add_first_party_caveat('view_pictures = True')
    # Get the key from auth server
    m.add_third_party_caveat(location="cool", key="test", key_id=0)
    serialized = m.serialize()
    images = [True, True, True]
    resp = make_response(render_template("auth_demo.html", macaroon=m.inspect().replace("\n","<br/>")))
    resp.set_cookie('macaroonCookie', serialized)
    return resp

if __name__ == '__main__':
    app.run()