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
@app.route('/login')
def login():
    return render_template('login.html', name="Name")


@app.route('/home', methods=["POST"])
def photo_album_login():
    login_successful = True
    if login_successful:
        m = Macaroon(
            location='cool-picture-service.example.com',
            identifier='key-for-bob',
            key=keys['key-for-bob'])
        # Add a caveat for the target service
        m.add_first_party_caveat('view_pictures = True')
        serialized = m.serialize()
        images = [True, True, True]
        resp = make_response(render_template("home.html", showimages=True, images=images, macaroon=m.inspect().replace("\n","<br/>")))
        resp.set_cookie('macaroonCookie', serialized)
        return resp
    else:
        return redirect(url_for("login"))


@app.route('/home', methods=["GET"])
def photo_album():
    macaroonCookie = request.cookies.get('macaroonCookie')
    if macaroonCookie is not None and macaroonCookie != "":
        m = Macaroon.deserialize(macaroonCookie)
        v = Verifier()
        v.satisfy_exact('view_pictures = True')
        try:
            verified = v.verify(
                m,
                keys[m.identifier]
            )
        except MacaroonInvalidSignatureException:
            verified = False
        images = [True, True, True]
        resp = make_response(render_template("home.html", showimages=verified, images=images, macaroon=m.inspect().replace("\n", "<br/>")))
        return resp
    else:
        return redirect(url_for("login"))


@app.route('/home/<int:picture_id>/<macaroon>', methods=["Get"])
def access_picture_with_macaroon(picture_id, macaroon):

    m = Macaroon.deserialize(macaroon)
    v = Verifier()
    v.satisfy_exact('view_pictures = True')
    v.satisfy_exact('picture_id = ' + str(picture_id))
    try:
        verified = v.verify(
            m,
            keys[m.identifier]
        )
    except MacaroonInvalidSignatureException:
        verified = False
    images = [False, False, False]
    images[picture_id] = True
    resp = make_response(render_template("home.html", showimages=verified, images=images, macaroon=m.inspect().replace("\n","<br/>")))
    return resp

@app.route('/set_invalid_macaroon', methods=["Get"])
def set_invalid_macaroon():
    resp = make_response(render_template("login.html"))
    # Created with macaroons.io
    resp.set_cookie('macaroonCookie', 'MDAxMmxvY2F0aW9uIHRlc3QKMDAxYmlkZW50aWZpZXIga2V5LWZvci1ib2IKMDAyZnNpZ25hdHVyZSArjUVl9NsMLDQQDA69BkEPzhujgcOB77L5wp4vs-HuRwo')
    return resp

@app.route('/share_picture/<int:picture_id>')
def share_picture(picture_id):
    macaroon_cookie = request.cookies.get('macaroonCookie')
    if macaroon_cookie is not None and macaroon_cookie != "":
        # Adding the caveat could be done on the client
        m = Macaroon.deserialize(macaroon_cookie)
        m.add_first_party_caveat('picture_id = ' + str(picture_id))
        serialized = m.serialize()
        link = "http://127.0.0.1:5000/home/" + str(picture_id) + "/" + serialized
        resp = make_response(render_template("share_link.html", link=link, macaroon=serialized))
        return resp
    else:
        return redirect(url_for("login"))


@app.route('/set_as_cookie/<macaroon>')
def set_cookie(macaroon):
    resp = make_response("<a href='../home'>Go to photo album</a>")
    resp.set_cookie('macaroonCookie', macaroon)
    return resp


@app.route('/get-macaroon-from-cookie')
def get_cookie():
    macaroonCookie = request.cookies.get('macaroonCookie')
    return macaroonCookie;

if __name__ == '__main__':
    app.run()