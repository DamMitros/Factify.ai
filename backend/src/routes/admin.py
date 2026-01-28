import os, json, pandas as pd
from datetime import datetime
from flask import Blueprint, jsonify, send_file, request
from keycloak_client import role_required, get_keycloak_admin
from common.python import db

admin_bp = Blueprint('admin', __name__)
NLP_REPORTS_DIR = os.path.join(os.getcwd(), "nlp", "artifacts", "reports")
IMAGE_REPORTS_DIR = os.path.join(os.getcwd(), "image_detection", "artifacts", "reports")

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_system_stats():
    client = db.get_client()
    db_main = client.get_database("factify_ai")
    db_img = client.get_database("factify")

    return jsonify({
        "users": db_main.users.count_documents({}),
        "text_analyses": db_main.text_analysis_logs.count_documents({}),
        "image_analyses": db_img.image_analysis.count_documents({}),
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

        synced = 0
        for kc_user in kc_users:
            data = {
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
                {"$set": data, "$setOnInsert": {"createdAt": datetime.utcnow()}},
                upsert=True
            )
            if result.upserted_id or result.modified_count:
                synced += 1

        return jsonify({
            "message": f"Synced {synced} users from Keycloak",
            "total": len(kc_users)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users/<user_id>/block', methods=['PUT'])
@role_required('admin')
def block_user(user_id):
    try:
        enabled = request.get_json().get("enabled", False)
        kc_admin = get_keycloak_admin()
        kc_admin.update_user(user_id=user_id, payload={"enabled": enabled})

        db.get_client().get_database("factify_ai").users.update_one(
            {"keycloakId": user_id},
            {"$set": {"enabled": enabled, "updatedAt": datetime.utcnow()}}
        )

        return jsonify({"message": f"User {'enabled' if enabled else 'blocked'}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users/<user_id>/history', methods=['GET'])
@role_required('admin')
def get_user_history(user_id):
    database = db.get_client().get_database("factify_ai")
    history = list(
        database.text_analysis_logs
        .find({"user_id": user_id})
        .sort("timestamp", -1)
        .limit(20)
    )
    for h in history:
        h["_id"] = str(h["_id"])
    return jsonify(history)


@admin_bp.route('/users/<email>', methods=['DELETE'])
@role_required('admin')
def delete_user(email):
    db_main = db.get_client().get_database("factify_ai")
    result = db_main.users.delete_one({"email": email})
    return (
        jsonify({"message": "User deleted"}),
        200
    ) if result.deleted_count else (
        jsonify({"error": "User not found"}),
        404
    )

@admin_bp.route('/nlp/reports', methods=['GET'])
@role_required('admin')
def list_nlp_reports():
    return jsonify([
        d for d in os.listdir(NLP_REPORTS_DIR)
        if os.path.isdir(os.path.join(NLP_REPORTS_DIR, d))
    ]) if os.path.exists(NLP_REPORTS_DIR) else jsonify([])


@admin_bp.route('/nlp/metrics', methods=['GET'])
@role_required('admin')
def get_nlp_metrics():
    report_id = request.args.get("report_id")
    path = os.path.join(NLP_REPORTS_DIR, report_id, "metrics.json") if report_id \
        else os.path.join(NLP_REPORTS_DIR, "metrics.json")

    return jsonify(json.load(open(path))) if os.path.exists(path) \
        else (jsonify({"error": "Metrics not found"}), 404)


@admin_bp.route('/nlp/confusion_matrix', methods=['GET'])
@role_required('admin')
def get_nlp_confusion_matrix():
    report_id = request.args.get("report_id")
    path = os.path.join(NLP_REPORTS_DIR, report_id, "confusion_matrix.png") if report_id \
        else os.path.join(NLP_REPORTS_DIR, "confusion_matrix.png")

    return send_file(path, mimetype="image/png") if os.path.exists(path) \
        else (jsonify({"error": "Matrix not found"}), 404)


@admin_bp.route('/nlp/failures', methods=['GET'])
@role_required('admin')
def get_nlp_failures():
    report_id = request.args.get("report_id")
    path = os.path.join(NLP_REPORTS_DIR, report_id, "fails.csv") if report_id \
        else os.path.join(NLP_REPORTS_DIR, "mc_dropout_train2", "fails.csv")

    if not os.path.exists(path):
        return jsonify({"error": "Failures not found"}), 404

    df = pd.read_csv(path).where(pd.notnull, None)
    return jsonify(df.to_dict(orient="records"))

@admin_bp.route('/image/logs', methods=['GET'])
@role_required('admin')
def get_image_logs():
    db_img = db.get_client().get_database("factify")
    logs = list(db_img.image_analysis.find().sort("timestamp", -1).limit(50))
    for l in logs:
        l["_id"] = str(l["_id"])
    return jsonify(logs)


@admin_bp.route('/image/metrics', methods=['GET'])
@role_required('admin')
def get_image_metrics():
    path = os.path.join(IMAGE_REPORTS_DIR, "classification_report_best.json")
    return jsonify(json.load(open(path))) if os.path.exists(path) \
        else (jsonify({"error": "Image metrics not found"}), 404)


@admin_bp.route('/image/confusion_matrix', methods=['GET'])
@role_required('admin')
def get_image_confusion_matrix():
    path = os.path.join(IMAGE_REPORTS_DIR, "confusion_matrix_best.png")
    return send_file(path, mimetype="image/png") if os.path.exists(path) \
        else (jsonify({"error": "Confusion matrix not found"}), 404)

@admin_bp.route('/logs', methods=['GET'])
@role_required('admin')
def get_logs():
    db_main = db.get_client().get_database("factify_ai")
    logs = list(db_main.text_analysis_logs.find().sort("timestamp", -1).limit(50))
    for l in logs:
        l["_id"] = str(l["_id"])
    return jsonify(logs)
