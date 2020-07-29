from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from db.models import Protein, BindingSite, Gene
from db.database import SQLALCHEMY_DATABASE_URL

app = Flask(__name__)
#TODO URI vs URL
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
db = SQLAlchemy(app)
#TODO migrations?


#SQLAlchemy models converted to Flask-sqlalchemy models TODO: unite models? we need the query atribute https://docs.sqlalchemy.org/en/13/orm/query.html
class ProteinModel(db.Model, Protein):
   def serialize(self):
      return {
         'protein_name':self.protein_name,
         'protein_id':self.protein_id,
         'uniport_url':self.uniprot_url
      }
class BindingSiteModel(db.Model, BindingSite):
   pass
class GeneModel(db.Model, Gene):
   pass


@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/db')
def db_endpoint():
   # return {"result": [pro.protein_name for pro in ProteinModel.query.all()]}
   return jsonify([log.serialize() for log in ProteinModel.query.all()])

@app.route('/protein')
def protein_by_name():
   requested_name = request.args.get('protein_name', default="", type=str)
   result = ProteinModel.query.filter(ProteinModel.protein_name == requested_name)
   return jsonify([log.serialize() for log in result])

if __name__ == '__main__':
   app.run()