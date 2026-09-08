from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, URLField, ValidationError
from wtforms.validators import AnyOf, DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
from models import User


msg_required ="ველის შევსება აუცილებელია."
msg_email = "შეიყვანეთ კორექტული ელ.ფოსტის მისამართი."
msg_len = "ველის სიგრძე უნდა იყოს მინიმუმ %(min)s და მაქსიმუმ %(max)s სიმბოლო."
msg_phone = "ტელეფონის ნომერი უნდა იწყებოდეს მინიმუმ %(min)s და მაქსიმუმ %(max)s."
msg_select = "არასწორი არჩევანი."
msg_confirm = "პაროლები არ არის იდენტური."


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(message=msg_required), Email(message=msg_email), Length(max=120, message=msg_len)],
                         render_kw={"placeholder": "name@example.com"})                                                   
    password = PasswordField('Password', validators=[DataRequired(message=msg_required), Length(min=6, message=msg_len)],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Full Name / Username', validators=[DataRequired(message=msg_required), Length(min=2, max=100)],
                           render_kw={"placeholder": "Full Name / Username"})
    email = StringField('Email Address', validators=[DataRequired(message=msg_required), Email(message=msg_email), Length(max=120, message=msg_len)],
                        render_kw={"placeholder": "name@example.com"})
    gender = SelectField('Gender', 
        choices=[('','Select gender'),('m', 'Male'), ('f', 'Female')],
        default='',validators=[DataRequired(message=msg_required),AnyOf(['m', 'f'], message=msg_select)])
    password = PasswordField('Password', validators=[DataRequired(message=msg_required), Length(min=6, max=255, message=msg_len)],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message=msg_required), EqualTo('password', message=msg_confirm)],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')
    
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('მომხმარებელი ასეთი ელ.ფოსტით უკვე არსებობს.')
    
class IngredientForm(FlaskForm):
    class Meta:
        csrf = False
    name = StringField('Ingredient Name', validators=[DataRequired(message=msg_required), Length(max=150, message=msg_len)])
    amount = StringField('Amount', validators=[DataRequired(message=msg_required), Length(max=50, message=msg_len)])

class RecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired(message=msg_required), Length(max=150, message=msg_len)])
    category = SelectField('Category', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('dessert', 'Dessert'),
        ('vegan', 'Vegan')
    ], validators=[DataRequired(message=msg_required)])
    prep_time = StringField('Prep & Cook Time', validators=[DataRequired(message=msg_required),Length(max=50, message=msg_len)])
    servings = IntegerField('Servings', validators=[DataRequired(message=msg_required)])
    image_url = URLField('Image URL', validators=[DataRequired(message=msg_required), Length(max=255, message=msg_len)])
    youtube_url = URLField('YouTube Video URL', validators=[Length(max=255, message=msg_len)])
    short_desc = TextAreaField('Short Description', validators=[DataRequired(message=msg_required), Length(max=300, message=msg_len)])
    ingredients = FieldList(FormField(IngredientForm), min_entries=1, max_entries=20)
    full_recipe = TextAreaField('Full Recipe / Instructions', validators=[DataRequired(message=msg_required)])
    submit = SubmitField('Publish Recipe')
    


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message=msg_required), Length(min=2, max=100, message=msg_len)])
    email = StringField('Email Address', validators=[DataRequired(message=msg_required), Email(message=msg_email),Length(max=120, message=msg_len)])
    gender = SelectField('Gender', 
        choices=[('','Select gender'),('m', 'Male'), ('f', 'Female')],
        default='',validators=[DataRequired(message=msg_required),AnyOf(['m', 'f'], message=msg_select)])
    profile_image = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Save Changes')