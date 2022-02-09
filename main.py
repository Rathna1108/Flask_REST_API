# from flask import Flask
# app= Flask(__name__)

# @app.route('/')
# def index():
#   return "<h1>Welcome to CodingX</h1>"

import datetime
import hashlib
from flask import Flask,request,jsonify
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, JWTManager,jwt_required,get_jwt_identity

from os import environ 

PORT = environ.get('PORT')
FLASK_PORT = environ.get('FLASK_PORT')
print(PORT, FLASK_PORT)




app = Flask(__name__)

client = MongoClient("mongodb+srv://m001-student:m001-mongodb-basics@sandbox.yikjx.mongodb.net/test?retryWrites=true&w=majority")
db = client["newdb"]
user_collection = db["post"]


jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Airtel@1'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
 

# homepage
@app.route('/')
def hello():
    return "hello world! Welcome user...." 


#user_registration page
@app.route('/api/v1/users', methods = ["POST"])
def register():

    new_user = request.get_json()
    new_user['password'] = hashlib.sha256(new_user['password'].encode("utf_8")).hexdigest()
    doc = user_collection.find_one({'username':new_user['username']})

    if not doc:
        user_collection.insert_one(new_user)
        return jsonify({'msg':'user created successfully'}),201
    else:
        return jsonify({'msg':'user already exists'}),409


# user_signin page
@app.route('/api/v1/login', methods=["POST"])
def login():

    login_details = request.get_json()
    user_from_db = user_collection.find_one({'username':login_details['username']})

    if user_from_db:
        encrypted_password = hashlib.sha256(login_details['password'].encode('utf-8')).hexdigest()
        
        if encrypted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['username'])
            return jsonify(access_token = access_token),200


    return jsonify({'msg':'username or password are incorrect'}),401


# user_profile page
@app.route('/api/v1/user', methods=["GET"])
@jwt_required()
def profile():

    create_user = get_jwt_identity()

    user_from_db = user_collection.find_one({'username': create_user})

    if user_from_db:

        del user_from_db['_id'],user_from_db['password']
        return jsonify({'profile':user_from_db}),200

    else:
         return jsonify({'msg':'profile not found'}), 404  

#update password
@app.route('/api/v1/password_update', methods=["PUT"])
def update_pwd():

    update_details = request.get_json()
    encrypt_pwd = hashlib.sha256(update_details['password'].encode('utf-8')).hexdigest()
    user_from_db = user_collection.find_one({'username':update_details['username']})

    if user_from_db:
        updated_pwd = encrypt_pwd
        user_collection.update_one({'username':user_from_db['username']},{'$set':{'password':updated_pwd}})

        return jsonify({'msg':'Password updated successfully'}),200
    else:

        return jsonify({'msg':'cannot updated password'}),401   


#delete user
@app.route('/api/v1/<username>', methods=["DELETE"])
def delete_user(username):
    user_collection.delete_one({'username':username})
    return jsonify({'msg':'user deleted successfully'}),200

    

# if __name__ == '__main__':
#     app.run(debug = True)