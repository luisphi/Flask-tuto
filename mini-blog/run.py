from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from werkzeug.urls import url_parse

# MIS CLASES
from forms import SignupForm, PostForm, LoginForm
from models import users, get_user, User

app = Flask(__name__)
#PARA USARLO EN FORMULARIOS API KEY
app.config['SECRET_KEY'] = '8352b5ddff72a1bd3fab8f89910b693d925154ef'

#INSTANCIA PARA USAR SESIONES DE USUARIOS Y PODER AUTENTICARLOS
login_manager = LoginManager(app)

#SIRVE PARA MOSTRAR UNA PANTALLA EN CASO DE NO TENER ACCESO A UNA PAGINA
login_manager = LoginManager(app)
login_manager.login_view = "login"
###################################

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None
###################################    

posts = []
@app.route("/")
def index():
    ### CAPTURAR DATOS ENVIADOS DESDE LA URL ### http://127.0.0.1:8000/?page=4&list=10
    page = request.args.get('page', 1)
    list = request.args.get('list', 20)
    print('Los datos son:', page, list); 

    print(users)

    return render_template("index.html", post=posts)

@app.route("/p/<string:slug>/")
def show_post(slug):
    return render_template("post_view.html", slug_title=slug)

@app.route("/admin/post/", methods=["POST","GET"], defaults={'post_id': None})
@app.route("/admin/post/<int:post_id>/", methods=["POST", "GET"])
@login_required
def post_form(post_id):
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        title_slug = form.title_slug.data
        content = form.content.data
        post = {'title': title, 'title_slug': title_slug, 'content': content}
        posts.append(post) #AGREGAR A LA LISTA EL POST

        return redirect(url_for('index'))

    return render_template("admin/post_form.html", form=form)

#PARA CAPTURAR INFORMACION DE UN FORMULARIO
@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = SignupForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Creamos el usuario y lo guardamos
        user = User(len(users) + 1, name, email, password)
        users.append(user)
        # Dejamos al usuario logueado
        login_user(user, remember=True)

        next = request.args.get('next', None) #ACCION PARA HACER LUEGO DE ENVIAR EL FORMULARIO
        if next:
            return redirect(next)
        return redirect(url_for('index'))

    # EN CASO DE SOLO CAPTURAR LOS DATOS DEL FORMULARIO SIN UNA
    # if request.method == 'POST':
    #     name = request.form['name']
    #     email = request.form['email']
    #     password = request.form['password']        

    return render_template("signup_form.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data) #METODO PROPIO DE LA LIBRERIA

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login_form.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=8000)