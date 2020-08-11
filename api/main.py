from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db.database import SQLALCHEMY_DATABASE_URL
from models import ProteinModel, BindingSiteModel, GeneModel
from routes import genomic
from db.database import db

app = Flask(__name__)
#TODO URI vs URL
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
#TODO remove in production
app.config['DEBUG'] = True
#Sectet key is needed because of forms https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
app.config['SECRET_KEY'] = 'muchos gracios'
# db = SQLAlchemy(app)
db.init_app(app)
#TODO migrations?

app.register_blueprint(genomic)

if __name__ == '__main__':
   app.run()