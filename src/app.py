"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['POST'])
def create_user():
    #se debe pasar la información a formato json
    request_body=request.json

    # se verifica si el usuario ya existe
    user_info_query=User.query.filter_by(email=request_body["email"]).first()

    #Condicional, para crear el usuario si este no existe (verificado en query anterior)
    if user_info_query is None:
        user = User(
            name=request_body["name"],
            surname=request_body["surname"],
            email=request_body["email"], 
            password=request_body["password"])
        db.session.add(user)
        db.session.commit()
        response_body = {
            "msg": "Usuario creado correctamente", 
        }
        return jsonify(response_body), 200
    
    else: 
        return jsonify("El usuario ya existe"), 400
        
@app.route('/user', methods=['GET'])
def all_users_info():
    #Query para regresar la info de todos los user
    users_query=User.query.all()
    result=list(map(lambda item: item.serialize(), users_query))
    
    response_body = {
        "msg": "OK",
        "result":result
    }

    return jsonify(response_body), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):

    #Query para regresar la info de user especifico
    user_info_query = User.query.filter_by(id=user_id).first()
        
    response_body = {
        "msg": "OK",
        "result":user_info_query.serialize()
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
