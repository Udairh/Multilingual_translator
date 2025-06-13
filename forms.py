from flask_wtf import FlaskForm # type: ignore
from wtforms import TextAreaField, FileField, SelectField, SubmitField # type: ignore
from wtforms.validators import Optional # type: ignore

class TranslateForm(FlaskForm):
    text = TextAreaField("Text")
    file = FileField("Upload .txt", validators=[Optional()])
    target_lang = SelectField("Target Language", choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('hi', 'Hindi'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('zh', 'Chinese'),
        ('ru', 'Russian'),
        ('ar', 'Arabic')
    ])
    submit = SubmitField("Translate")