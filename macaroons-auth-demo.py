from flask import Flask, render_template, make_response, request, redirect, url_for
from pymacaroons import Macaroon, Verifier
from pymacaroons.exceptions import MacaroonInvalidSignatureException

app = Flask(__name__)

# Keys for signing macaroons are associated with some identifier for later
# verification. This could be stored in a database, key value store,
# memory, etc.
alice_server_keys = {
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
        key=alice_server_keys['key-for-bob'])
    # should be random
    caveat_key = 'randomKey'
    predicate = 'Bob'
    identifier = auth_server_get_identifier(caveat_key, predicate)
    # location is unused
    m.add_third_party_caveat('http://auth-server.example.com/', caveat_key, identifier)
    serialized = m.serialize()
    resp = make_response(render_template("auth_demo.html", macaroon=m.inspect().replace("\n", "<br/>"),
                                         caveat_key=caveat_key, identifier=identifier))
    resp.set_cookie('macaroonCookie', serialized)
    return resp


@app.route('/alice_server_access_service')
def alice_server_access_service():
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
                alice_server_keys[m.identifier],
                [pm]
            )
        except MacaroonInvalidSignatureException:
            verified = False
        if verified:
            resp = make_response(render_template("auth_demo.html", result="Successful Authentication"))
        else:
            resp = make_response(render_template("auth_demo.html", result="Auth failed"))
        return resp
    else:
        resp = make_response(render_template("auth_demo.html", result="Couldn't get necessary macaroons from cookies"))
        return resp


# These would be stored in a db
auth_server_users = [{"name": "Bob", "caveat_key": "", "identifier": ""}]


def auth_server_get_identifier(caveat_key, user_name):
    for user in auth_server_users:
        if user["name"] == user_name:
            user["caveat_key"] = caveat_key
            user["identifier"] = "bob_identifier"
            return user["identifier"]


"""
The service at ``http://auth-server.example.com/'' can authenticate that the user is Bob, and provide
proof that the caveat is satisfied, without revealing Bobs's identity.  Other
services can verify M and its associated discharge macaroon, without knowing the
predicates the third-parties verified.
"""


@app.route('/auth_server_login', methods=["Post"])
def auth_server_login():
    user_name = request.form['username']
    for user in auth_server_users:
        if user["name"] == user_name and user["identifier"] != "":
            dm = Macaroon(location='http://auth-server.example.com/',
                          key=user["caveat_key"],
                          identifier=user["identifier"])
            # dm = dm.add_first_party_caveat('time < 2020-01-01T00:00')
            serialized = dm.serialize()
            resp = make_response(render_template("auth_demo.html",
                                                 discharge_macaroon=dm.inspect().replace("\n", "<br/>")))
            resp.set_cookie('macaroonDischargeCookie', serialized)
            return resp
    resp = make_response(render_template("auth_demo.html", result="Auth failed"))
    return resp


@app.route('/reset_cookies_auth_server')
def reset_cookies_auth_server():
    resp = make_response(render_template("auth_demo.html", result="Reset Cookies"))
    resp.set_cookie('macaroonCookie', "")
    resp.set_cookie('macaroonDischargeCookie', "")
    auth_server_users = [{"name": "Bob", "caveat_key": "", "identifier": ""}]
    return resp


if __name__ == '__main__':
    app.run()
