"""Forms for Flask Cafe."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, Optional, URL, Email, Length


class AddOrEditCafe(FlaskForm):
    """form for adding or editing cafe"""

    name = StringField(
        "Name",
        validators=[InputRequired()]
    )
    description = StringField(
        "Description",
        validators=[Optional()]
    )
    url = StringField(
        "URL",
        validators=[Optional(), URL()]
    )
    address = StringField(
        "Address",
        validators=[InputRequired()]
    )
    city_code = SelectField(
        "City code"
    )
    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()]
    )


class SignupForm(FlaskForm):
    """form for signing up user"""

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )
    first_name = StringField(
        "First name",
        validators=[InputRequired()]
    )
    last_name = StringField(
        "Last name",
        validators=[InputRequired()]
    )
    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )
    email = StringField(
        "Email",
        validators=[InputRequired(), Email()]
    )
    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()]
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)]
    )


class LogInForm(FlaskForm):
    """form for logging in user"""

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )


class ProfileEditForm(FlaskForm):
    """for for editing user information"""

    first_name = StringField(
        "First name",
        validators=[InputRequired()]
    )
    last_name = StringField(
        "Last name",
        validators=[InputRequired()]
    )
    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )
    email = StringField(
        "Email",
        validators=[InputRequired(), Email()]
    )
    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()]
    )
