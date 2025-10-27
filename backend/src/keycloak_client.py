from keycloak import KeycloakOpenID
import os
from jose import jwt, JWTError, ExpiredSignatureError
from flask import jsonify,request
import functools
from typing import Optional


KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://keycloak:8080/")
KEYCLOAK_REALM= os.getenv("KEYCLOAK_REALM", "factify.ai")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "frontend")

keycloak_openid = KeycloakOpenID(
    server_url = KEYCLOAK_SERVER_URL,
    client_id = KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM
)


_PUBLIC_KEY: Optional[str] = None


def _get_public_key() -> str:
    global _PUBLIC_KEY
    if _PUBLIC_KEY:
        return _PUBLIC_KEY
    raw = keycloak_openid.public_key()
    if not raw:
        raise RuntimeError("Keycloak public key not available")
    if raw.startswith("-----BEGIN"):
        _PUBLIC_KEY = raw
    else:
        _PUBLIC_KEY = f"-----BEGIN PUBLIC KEY-----\n{raw}\n-----END PUBLIC KEY-----"
    return _PUBLIC_KEY


def verify_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, jsonify({"message": "Token is missing"}), 401

    token = auth_header.split(" ")[1]

    try:
        public_key = _get_public_key()
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=KEYCLOAK_CLIENT_ID, 
        )

        request.user = decoded
        return decoded, None, None

    except ExpiredSignatureError:
        return None, jsonify({"message": "Session expired"}), 401
    except JWTError as e:
        return None, jsonify({"message": "Token is invalid", "error": str(e)}), 401



def role_required(role_name):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            decoded_token, err_response, status = verify_token()
            if err_response:
                return err_response, status

            roles = decoded_token.get("realm_access", {}).get("roles", [])
            if role_name not in roles:
                return jsonify({"message": f"Role '{role_name}' required"}), 403

            request.user = decoded_token
            return f(*args, **kwargs)
        return wrapper
    return decorator





