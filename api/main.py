from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db.config import SECRET_KEY, SQLALCHEMY_DATABASE_URL
from models import ProteinModel, BindingSiteModel, GeneModel
from routes import genomic
from db.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
#TODO remove in production
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = SECRET_KEY
db.init_app(app)
app.register_blueprint(genomic)

if __name__ == '__main__':
   app.run()