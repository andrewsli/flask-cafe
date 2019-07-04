"""Data models for Flask Cafe"""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()


class City(db.Model):
    """Cities for cafes."""

    def __repr__(self):
        return f'<City code={self.code} name="{self.name}">'

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )

    @classmethod
    def cities(cls):
        """returns a list of tuples of every city in database"""
        return [(c.code, c.name) for c in City.query.all()]


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default="/static/images/default-cafe.jpg",
    )

    city = db.relationship("City", backref='cafes')

    liking_users = db.relationship(
        "User",
        secondary="likes"
        )

    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'


class User(db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    admin = db.Column(
        db.Boolean,
        nullable=False,
    )

    email = db.Column(
        db.Text,
        nullable=False,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default="/static/images/default-pic.png",
    )

    hashed_password = db.Column(
        db.Text,
        nullable=False,
    )

    liked_cafes = db.relationship(
        "Cafe",
        secondary="likes"
    )

    def get_full_name(self):
        """returns 'first_name last_name'"""
        return f"{self.first_name} {self.last_name}"

    def likes_cafe(self, cafe_id):
        """returns T/F if user likes/doesn't like the cafe"""
        for cafe in self.liked_cafes:
            if cafe.id == cafe_id:
                return True
        return False
        # return any(cafe.id == cafe_id for cafe in self.liked_cafes:)

    @classmethod
    def register(
        cls,
        username,
        first_name,
        last_name,
        description,
        email,
        password,
        admin=False,
        image_url="/static/images/default-pic.png"
    ):
        """return user with hashed password"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(
            username=username,
            hashed_password=hashed_utf8,
            admin=admin,
            email=email,
            first_name=first_name,
            last_name=last_name,
            description=description,
            image_url=image_url,
        )

    @classmethod
    def authenticate(cls, username, pwd):
        """return user if valid user, else return False"""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.hashed_password, pwd):
            return u
        else:
            return False


class Like(db.Model):
    """middle table linking liker User to liked Cafe"""

    __tablename__ = "likes"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    )

    cafe_id = db.Column(
        db.Integer,
        db.ForeignKey("cafes.id"),
        primary_key=True
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
