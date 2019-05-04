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


@app.route('/alice_server_get_macaroon')
def alice_server_get_macaroon():
    m = Macaroon(
        location='alices-server.example.com',
        identifier='key-for-bob',
        key=keys['key-for-bob'])
    # you'll likely want to use a higher entropy source to generate this key
    caveat_key = 'randomKey'
    predicate = 'user = Alice'
    # send_to_auth(caveat_key, predicate)
    # identifier = recv_from_auth()
    identifier = 'key_pred_reminder'
    # location is unused
    m.add_third_party_caveat('http://auth-server.example.com/', caveat_key, identifier)
    serialized = m.serialize()
    resp = make_response(render_template("auth_demo.html", macaroon=m.inspect().replace("\n", "<br/>"),
                                         caveat_key=caveat_key, identifier=identifier))
    resp.set_cookie('macaroonCookie', serialized)
    return resp


"""
The service at ``http://auth-server.example.com/'' can authenticate that the user is Bob, and provide
proof that the caveat is satisfied, without revealing Bobs's identity.  Other
services can verify M and its associated discharge macaroon, without knowing the
predicates the third-parties verified."""


@app.route('/auth_server_login/<caveat_key>/<identifier>')
def auth_server_login(caveat_key, identifier):
    if caveat_key is None or caveat_key == "" or identifier is None or identifier == "":
        resp = make_response(render_template("auth_demo.html", result="No macaroon given"))
        return resp
    macaroon_cookie = request.cookies.get('macaroonCookie')
    m = Macaroon.deserialize(macaroon_cookie)
    dm = Macaroon(location='http://auth-server.example.com/', key=caveat_key, identifier=identifier)
    # dm = dm.add_first_party_caveat('time < 2020-01-01T00:00')
    serialized = dm.serialize()
    resp = make_response(render_template("auth_demo.html", macaroon=m.inspect().replace("\n", "<br/>"),
                                         discharge_macaroon=dm.inspect().replace("\n", "<br/>")))
    resp.set_cookie('macaroonDischargeCookie', serialized)
    return resp

@app.route('/access_service')
def access_service():
    macaroon_cookie = request.cookies.get('macaroonCookie')
    discharge_cookie = request.cookies.get('macaroonDischargeCookie')
    if macaroon_cookie is not None and macaroon_cookie != "" and discharge_cookie is not None and discharge_cookie != "":
        m = Macaroon.deserialize(macaroon_cookie)
        dm = Macaroon.deserialize(discharge_cookie)
        # Should be done on the client
        pm = m.prepare_for_request(dm)
        v = Verifier()
        try:
            verified = v.verify(
                m,
                keys[m.identifier],
                [pm]
            )
        except MacaroonInvalidSignatureException:
            verified = False
        if verified:
            resp = make_response(render_template("auth_demo.html", result="Successfull Authenticaton"))
        else:
            resp = make_response(render_template("auth_demo.html", result="Auth failed"))
        return resp
    else:
        resp = make_response(render_template("auth_demo.html", result="Couldn't get necessairy macaroons from cookies"))
        return resp

@app.route('/reset_cookies')
def reset_cookies():
    resp = make_response(render_template("auth_demo.html", result="Reset Cookies"))
    resp.set_cookie('macaroonCookie', "")
    resp.set_cookie('macaroonDischargeCookie', "")
    return resp


if __name__ == '__main__':
    app.run()
