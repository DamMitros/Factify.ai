from flask import Blueprint, jsonify,g, request
from keycloak_client import require_auth
from datetime import datetime
from common.python.db import get_database
from config import DB_NAME, COL_USERS

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
        users_collection = get_database(DB_NAME)[COL_USERS]
        keycloak_id = g.user.get("sub")

        update_data = {
            "username": g.user.get("preferred_username"),
            "email": g.user.get("email"),
            "firstName": g.user.get("given_name"),
            "lastName": g.user.get("family_name"),
            "updatedAt": datetime.utcnow(),
            "enabled": g.user.get("enabled", True)
        }

        result = users_collection.update_one(
            {"keycloakId": keycloak_id},
            {
                "$set": update_data,
                "$setOnInsert": {"createdAt": datetime.utcnow(), "keycloakId": keycloak_id}
            },
            upsert=True
        )

        if result.upserted_id:
            return jsonify({
                "message": "User registered successfully", 
                "userMongoId": str(result.upserted_id)
            }), 201
        else:
            return jsonify({"message": "User updated/synced in database"}), 200

    except Exception as e:
        return jsonify({"message": f"Registration failure {str(e)}"}), 500


