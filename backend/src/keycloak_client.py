from keycloak import KeycloakOpenID, KeycloakAdmin
import os
from jose import jwt, JWTError, ExpiredSignatureError
from flask import jsonify,request, g
import functools
from typing import Optional


KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "https://keycloak:8443/")
KEYCLOAK_REALM= os.getenv("KEYCLOAK_REALM", "factify.ai")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "frontend")
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USERNAME", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")

keycloak_openid = KeycloakOpenID(
    server_url = KEYCLOAK_SERVER_URL,
    client_id = KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    verify=False
)

def get_keycloak_admin():
    return KeycloakAdmin(
        server_url=KEYCLOAK_SERVER_URL,
        username=KEYCLOAK_ADMIN_USER,
        password=KEYCLOAK_ADMIN_PASSWORD,
        realm_name=KEYCLOAK_REALM,
        user_realm_name='master',
        verify=False
    )

_PUBLIC_KEY: Optional[str] = None

def require_auth_optional(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        g.user = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            decoded_token, error_response, status_code = _decode_token(token)
            if decoded_token:
                g.user = decoded_token
        return f(*args, **kwargs)
    return wrapper


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


def _decode_token(token: str):
    try:
        public_key = _get_public_key()
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=KEYCLOAK_CLIENT_ID,
        )
        return decoded, None, None
    except ExpiredSignatureError:
        return None, jsonify({"message": "Session expired"}), 401
    except JWTError as e:
        return None, jsonify({"message": "Token is invalid", "error": str(e)}), 401


def require_auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token is missing"}), 401

        token = auth_header.split(" ")[1]
        decoded, err_response, status = _decode_token(token)
        
        if err_response:
            return err_response, status

        g.user = decoded
        return f(*args, **kwargs)
    
    return wrapper


def role_required(role_name: str):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "Token is missing"}), 401

            token = auth_header.split(" ")[1]
            decoded, err_response, status = _decode_token(token)
            
            if err_response:
                return err_response, status

            roles = decoded.get("realm_access", {}).get("roles", [])
            if role_name not in roles:
                return jsonify({"message": f"Role '{role_name}' required"}), 403

            g.user = decoded
            return f(*args, **kwargs)
        
        return wrapper
    return decorator







