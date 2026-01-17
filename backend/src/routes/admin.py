import os, json, pandas as pd
from datetime import datetime
from flask import Blueprint, jsonify, send_file, request
from keycloak_client import role_required, get_keycloak_admin
from common.python import db

admin_bp = Blueprint('admin', __name__)
ARTIFACTS_DIR = os.path.join(os.getcwd(), "nlp", "artifacts", "reports")

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_system_stats():
    database = db.get_client().get_database("factify_ai")
    users_count = database.users.count_documents({})
    text_analysis_count = database.text_analysis_logs.count_documents({})
    image_analysis_count = database.image_analysis_logs.count_documents({})

    return jsonify({
        "users": users_count,
        "text_analyses": text_analysis_count,
        "image_analyses": image_analysis_count,
        "status": "Healthy"
    })

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    database = db.get_client().get_database("factify_ai")
    users = list(database.users.find({}, {"_id": 0, "password": 0, "secret": 0}))
    return jsonify(users)

@admin_bp.route('/users/sync', methods=['POST'])
@role_required('admin')
def sync_users():
    try:
        kc_admin = get_keycloak_admin()
        kc_users = kc_admin.get_users({})
        
        database = db.get_client().get_database("factify_ai")
        users_collection = database.users
        
        synced_count = 0
        for kc_user in kc_users:
            user_data = {
                "keycloakId": kc_user.get("id"),
                "username": kc_user.get("username"),
                "email": kc_user.get("email"),
                "firstName": kc_user.get("firstName"),
                "lastName": kc_user.get("lastName"),
                "enabled": kc_user.get("enabled", True),
                "updatedAt": datetime.utcnow()
            }

            result = users_collection.update_one(
                {"keycloakId": kc_user.get("id")},
                {"$set": user_data, "$setOnInsert": {"createdAt": datetime.utcnow()}},
                upsert=True
            )
            if result.upserted_id or result.modified_count > 0:
                synced_count += 1
                
        return jsonify({"message": f"Synced {synced_count} users from Keycloak", "total": len(kc_users)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users/<user_id>/block', methods=['PUT'])
@role_required('admin')
def block_user(user_id):
    try:
        kc_admin = get_keycloak_admin()
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        kc_admin.update_user(user_id=user_id, payload={"enabled": enabled})
        database = db.get_client().get_database("factify_ai")
        database.users.update_one(
            {"keycloakId": user_id},
            {"$set": {"enabled": enabled, "updatedAt": datetime.utcnow()}}
        )
        
        return jsonify({"message": f"User {'enabled' if enabled else 'blocked'} successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users/<user_id>/history', methods=['GET'])
@role_required('admin')
def get_user_history(user_id):
    try:
        print(f"Fetching history for user_id: {user_id}")
        database = db.get_client().get_database("factify_ai")
        history = list(database.text_analysis_logs.find({"user_id": user_id}).sort("timestamp", -1).limit(20))
        print(f"Found {len(history)} logs for user_id: {user_id}")
        for item in history:
            item['_id'] = str(item['_id'])
        return jsonify(history), 200
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users/<email>', methods=['DELETE'])
@role_required('admin')
def delete_user(email):
    database = db.get_client().get_database("factify_ai")
    result = database.users.delete_one({"email": email})
    if result.deleted_count > 0:
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"error": "User not found"}), 404

@admin_bp.route('/nlp/reports', methods=['GET'])
@role_required('admin')
def list_nlp_reports():
    reports = []
    if os.path.exists(ARTIFACTS_DIR):
        for name in os.listdir(ARTIFACTS_DIR):
            if os.path.isdir(os.path.join(ARTIFACTS_DIR, name)):
                reports.append(name)
    return jsonify(reports)

@admin_bp.route('/nlp/metrics', methods=['GET'])
@role_required('admin')
def get_nlp_metrics():
    report_id = request.args.get('report_id')
    if report_id:
        metrics_path = os.path.join(ARTIFACTS_DIR, report_id, "metrics.json")
    else:
        metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
        
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Metrics not found"}), 404

@admin_bp.route('/nlp/confusion_matrix', methods=['GET'])
@role_required('admin')
def get_confusion_matrix():
    report_id = request.args.get('report_id')
    if report_id:
        matrix_path = os.path.join(ARTIFACTS_DIR, report_id, "confusion_matrix.png")
    else:
        matrix_path = os.path.join(ARTIFACTS_DIR, "confusion_matrix.png")
        
    if os.path.exists(matrix_path):
        return send_file(matrix_path, mimetype='image/png')
    return jsonify({"error": "Confusion matrix not found"}), 404

@admin_bp.route('/nlp/failures', methods=['GET'])
@role_required('admin')
def get_nlp_failures():
    report_id = request.args.get('report_id')
    if report_id:
        fails_path = os.path.join(ARTIFACTS_DIR, report_id, "fails.csv")
    else:
        fails_path = os.path.join(ARTIFACTS_DIR, "mc_dropout_train2", "fails.csv")
        
    if os.path.exists(fails_path):
        try:
            df = pd.read_csv(fails_path)
            df = df.where(pd.notnull(df), None)
            return jsonify(df.to_dict(orient='records'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Failures report not found"}), 404

@admin_bp.route('/logs', methods=['GET'])
@role_required('admin')
def get_logs():
    database = db.get_client().get_database("factify_ai")
    logs = list(database.text_analysis_logs.find().sort("timestamp", -1).limit(50))
    for log in logs:
        log['_id'] = str(log['_id'])
    return jsonify(logs)
