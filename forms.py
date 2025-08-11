from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, URLField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', 
                              validators=[DataRequired(), EqualTo('password')])

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    content = TextAreaField('Content', widget=TextArea())
    category = SelectField('Category', choices=[
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('desktop', 'Desktop Application'),
        ('data', 'Data Science'),
        ('ai', 'AI/Machine Learning'),
        ('other', 'Other')
    ])
    tags = StringField('Tags (comma-separated)')
    image = FileField('Project Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    demo_url = URLField('Demo URL', validators=[Optional()])
    github_url = URLField('GitHub URL', validators=[Optional()])
    is_published = BooleanField('Publish immediately')
    is_featured = BooleanField('Feature on homepage')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=10, max=1000)])

class AboutForm(FlaskForm):
    content = TextAreaField('About Me Content', validators=[DataRequired()], widget=TextArea())
