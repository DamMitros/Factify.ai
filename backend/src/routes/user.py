from flask import Blueprint, jsonify,g, request
from keycloak_client import require_auth
from datetime import datetime
from common.python.db import get_database



user_bp = Blueprint("user", __name__)

@user_bp.route("/profile", methods=["GET"])
@require_auth
def get_user_data():

    return jsonify({
        "username":g.user.get("preferred_username"),
        "name": g.user.get("name"),
        "email": g.user.get("email"),
        "roles": g.user.get("realm_access",{}).get("roles",[])
    }), 200 
#rozszerz o pobieranie danych z bazy mongo



@user_bp.route("/register", methods=["PUT"])
@require_auth
def register_user_in_mongodb():
    try:

        users_collection = get_database("factify_ai")["users"]

        keycloak_id = g.user.get("sub")

        existing_user = users_collection.find_one({"keycloakId": keycloak_id})
        if existing_user:
            return jsonify({"message": "User already registered in database"}), 200 #idempodentny ehh nw czy to git
        
        user_object = {
            "keycloakId": keycloak_id, # bedzie i id z mongo i keycloak id narazie
            "username": g.user.get("preferred_username"),
            "email": g.user.get("email"),
            "firstName": g.user.get("given_name"),
            "lastName": g.user.get("family_name"),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            #do dodania nw np liczba analiz, preferencje whatever
        }

        result = users_collection.insert_one(user_object)
            
        return jsonify({
            "message": "User registered successfully",
            "userMongoId": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"message": f"Registration failure {str(e)}"}), 500


