"""Flask App for Flask Cafe."""


from flask import Flask, render_template, request, flash, jsonify
from flask import redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Cafe, City, User, Like

from sqlalchemy.exc import IntegrityError

from secrets import FLASK_SECRET_KEY

from forms import AddOrEditCafe, SignupForm, LogInForm, ProfileEditForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///flaskcafe'
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)


#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


#######################################
# homepage

@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# cafes


@app.route('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
    )


@app.route('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Handle form for adding cafe. Redirects to cafe details
    on successful submit or renders form
    """
    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
    )


@app.route('/cafes/new', methods=["GET", "POST"])
def add_cafe():
    """Show form for adding cafe."""

    form = AddOrEditCafe()

    cities = City.cities()
    form.city_code.choices = cities

    if form.validate_on_submit():
        cafe = Cafe(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            address=form.address.data,
            city_code=form.city_code.data,
            image_url=form.image_url.data
        )

        db.session.add(cafe)
        db.session.commit()
        flash(f"{cafe.name} added!", "success")
        return redirect(f"/cafes/{cafe.id}")

    else:
        return render_template("/cafe/add-form.html", form=form)


@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    """Handle form for editing cafe. Redirects to cafe details
    on successful submit or renders form
    """

    cafe = Cafe.query.get(cafe_id)

    form = AddOrEditCafe(obj=cafe)

    cities = City.cities()
    form.city_code.choices = cities

    if form.validate_on_submit():
        cafe.name = form.name.data
        cafe.description = form.description.data
        cafe.url = form.url.data
        cafe.address = form.address.data
        cafe.city_code = form.city_code.data
        cafe.image_url = form.image_url.data

        db.session.commit()
        flash(f"{cafe.name} edited!", "success")
        return redirect(f"/cafes/{cafe.id}")

    else:
        return render_template("/cafe/edit-form.html", form=form, cafe=cafe)


#######################################
# Signup, login, and logout

@app.route('/signup', methods=["GET", "POST"])
def signup_user():
    """Handle form for signing up users. On successful submit,
    adds user, logs them in, and redirects them to cafe list
    with flashed message. Or renders form.
    """

    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data

        # checks if username is already taken
        if User.query.filter_by(username=username).first():
            flash(f"{username} is already taken.")
            return render_template("/auth/signup-form.html", form=form)

        user = User.register(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            description=form.description.data,
            email=form.email.data,
            image_url=form.image_url.data,
            password=form.password.data
        )

        db.session.add(user)
        db.session.commit()

        do_login(user)
        flash(f"You are signed up and logged in.", "success")
        return redirect("/cafes")

    else:
        return render_template("/auth/signup-form.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Handle form for logging in users. On successful submit,
    logs user in, and redirects them to cafe list
    with flashed message. Or renders form.
    """

    form = LogInForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            do_login(user)
            flash(f"Hello, {user.get_full_name()}!")
            return redirect("/cafes")
        else:
            form.username.errors = ["Invalid credentials"]

    return render_template("/auth/login-form.html", form=form)


@app.route('/logout', methods=["POST"])
def logout():
    """logs out user and redirects them to homepage with flashed message"""

    do_logout()
    flash("You have successfully logged out.", "success")
    return redirect("/")


#######################################
# profiles

@app.route('/profile')
def user_details():
    """send user to login page if not logged in. show profile page"""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG)
        return redirect('/login')

    return render_template('/profile/detail.html', user=g.user)


@app.route('/profile/edit', methods=["GET", "POST"])
def edit_user():
    """Process profile edit. On successful submit, redirects to
    profile page with flashed message. Or shows form."""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG)
        return redirect('/login')

    user = User.query.get(session[CURR_USER_KEY])

    form = ProfileEditForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.description = form.description.data
        user.email = form.email.data
        user.image_url = form.image_url.data

        db.session.commit()
        flash("Profile edited.", "success")
        return redirect("/profile")

    else:
        return render_template("/profile/edit-form.html", form=form)


#######################################
# likes API

@app.route('/api/likes')
def user_likes_cafe():
    """expects query with cafe_id, returns JSON {"likes": True/False} depending
    on whether the user has liked the cafe"""

    cafe_id = int(request.args["cafe_id"])

    if not g.user:
        return jsonify({"error": "Not logged in"})

    return jsonify({
        "likes": g.user.likes_cafe(cafe_id),
        })


@app.route('/api/like', methods=["POST"])
def like_cafe():
    """adds like with current user id and posted cafe id
    """
    cafe_id = int(request.json["cafe_id"])

    if not g.user:
        return jsonify({"error": "Not logged in"})

    like = Like(user_id=g.user.id, cafe_id=cafe_id)

    db.session.add(like)
    db.session.commit()

    return jsonify({"liked": cafe_id})


@app.route('/api/unlike', methods=["POST"])
def unlike_cafe():
    """removes like with current user id and posted cafe id"""
    cafe_id = int(request.json["cafe_id"])

    if not g.user:
        return jsonify({"error": "Not logged in"})
    like = Like.query.filter_by(user_id=g.user.id, cafe_id=cafe_id).first()
    db.session.delete(like)
    db.session.commit()

    return jsonify({"unliked": cafe_id})
