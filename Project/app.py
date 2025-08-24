from flask import Flask
from controllers.main_controller import main_routes
from models.user_model import init_db

app = Flask(__name__, template_folder="views")


app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "home4321"
app.config["MYSQL_DB"] = "metrorail_db"
app.secret_key = "home4321"


init_db(app)


app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True, port=9224)
