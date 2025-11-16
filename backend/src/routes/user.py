from flask import Blueprint, jsonify,g
from keycloak_client import require_auth


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
#rozszerz o pobieranie danych z bazy keycloakowej