from datetime import datetime
from flask import Blueprint, jsonify, request
from keycloak_client import role_required, get_keycloak_admin
from common.python import db
from config import DB_NAME, COL_ANALYSIS_AI_TEXT, COL_ANALYSIS_AI_IMAGE, COL_ANALYSIS_MANIPULATION, COL_ANALYSIS_SOURCES, COL_USERS, COL_REPORTS_IMAGE, COL_REPORTS_NLP

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_system_stats():
    database = db.get_client().get_database(DB_NAME)

    return jsonify({
        "users": database[COL_USERS].count_documents({}),
        "text_analyses": database[COL_ANALYSIS_AI_TEXT].count_documents({}),
        "image_analyses": database[COL_ANALYSIS_AI_IMAGE].count_documents({}),
        "manipulation_analyses": database[COL_ANALYSIS_MANIPULATION].count_documents({}),
        "source_analyses": database[COL_ANALYSIS_SOURCES].count_documents({}),
        "status": "Healthy"
    })

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    database = db.get_client().get_database(DB_NAME)
    users = list(database[COL_USERS].find({}, {"_id": 0, "password": 0, "secret": 0}))
    return jsonify(users)

@admin_bp.route('/users/<user_id>/block', methods=['PUT'])
@role_required('admin')
def block_user(user_id):
    try:
        enabled = request.get_json().get("enabled", False)
        kc_admin = get_keycloak_admin()
        kc_admin.update_user(user_id=user_id, payload={"enabled": enabled})

        db.get_client().get_database(DB_NAME)[COL_USERS].update_one(
            {"keycloakId": user_id},
            {"$set": {"enabled": enabled, "updatedAt": datetime.utcnow()}}
        )

        return jsonify({"message": f"User {'enabled' if enabled else 'blocked'}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    try:
        kc_admin = get_keycloak_admin()
        kc_admin.delete_user(user_id=user_id)
        
        database = db.get_client().get_database(DB_NAME)
        result = database[COL_USERS].delete_one({"keycloakId": user_id})
        
        if result.deleted_count:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"message": "User deleted from Keycloak, but not found in local DB"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/nlp/reports', methods=['GET'])
@role_required('admin')
def get_nlp_reports():
    database = db.get_client().get_database(DB_NAME)
    reports = database[COL_REPORTS_NLP].find({}, {"report_id": 1, "created_at": 1, "_id": 0}).sort("created_at", -1)
    return jsonify(list(reports))

@admin_bp.route('/nlp/reports/<report_id>', methods=['GET'])
@role_required('admin')
def get_full_report(report_id):
    database = db.get_client().get_database(DB_NAME)
    report = database[COL_REPORTS_NLP].find_one({"report_id": report_id}, {"_id": 0})

    if report:
        return jsonify(report)
    return jsonify({"error": "Report not found"}), 404

@admin_bp.route('/image/reports', methods=['GET'])
@role_required('admin')
def get_image_reports():
    database = db.get_client().get_database(DB_NAME)
    reports = database[COL_REPORTS_IMAGE].find({}, {"report_id": 1, "created_at": 1, "_id": 0}).sort("created_at", -1)
    return jsonify(list(reports))

@admin_bp.route('/image/reports/<report_id>', methods=['GET'])
@role_required('admin')
def get_full_image_report(report_id):
    database = db.get_client().get_database(DB_NAME)
    report = database[COL_REPORTS_IMAGE].find_one({"report_id": report_id}, {"_id": 0})

    if report:
        return jsonify(report)
    return jsonify({"error": "Report not found"}), 404
