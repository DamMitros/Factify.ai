import os, json, base64, pandas as pd

from datetime import datetime
from common.python.db import get_database
from config import DB_NAME, COL_REPORTS_IMAGE, COL_REPORTS_NLP, NLP_REPORTS_DIR, IMAGE_REPORTS_DIR

def _image_to_base64(image_path):
  if not os.path.exists(image_path):
    return "Image has not been included in the report."
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def _read_json(filepath):
  if not os.path.exists(filepath):
    return "Report data not found."
  with open(filepath, "r", encoding="utf-8") as f:
    return json.load(f)
  
def _csv_to_dict(filepath):
  if not os.path.exists(filepath):
    return "Report data not found."
  df = pd.read_csv(filepath).where(pd.notnull, None)
  return df.to_dict(orient="records")

def sync_nlp_report(database):
  number_of_reports = database[COL_REPORTS_NLP].count_documents({})
  founded_reports = 0

  if os.path.exists(NLP_REPORTS_DIR):
    for report_id in os.listdir(NLP_REPORTS_DIR):
      report_path = os.path.join(NLP_REPORTS_DIR, report_id)
            
      if os.path.isdir(report_path):
        report_data = {
          "report_id": report_id,
          "metrics": _read_json(os.path.join(report_path, "metrics.json")),
          "params": _read_json(os.path.join(report_path, "params.json")),
          "dataset_stats": _read_json(os.path.join(report_path, "dataset_stats.json")),
          "calibration": _read_json(os.path.join(report_path, "calibration.json")),
          "calibration_metrics": _read_json(os.path.join(report_path, "calibration_metrics.json")),
          "confusion_matrix_base64": _image_to_base64(os.path.join(report_path, "confusion_matrix.png")),
          "fails": _csv_to_dict(os.path.join(report_path, "fails.csv")),
          "last_synced": datetime.utcnow()
        }

        database[COL_REPORTS_NLP].update_one(
          {"report_id": report_id},
          {"$set": report_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
          upsert=True
        )
        founded_reports += 1
  print(f"[AI TEXT] In DB used to be {number_of_reports} NLP reports, now there are {founded_reports} synced from files.")

def sync_image_report(database):
  number_of_reports = database[COL_REPORTS_IMAGE].count_documents({})
  founded_reports = 0

  if os.path.exists(IMAGE_REPORTS_DIR):
    for report_id in os.listdir(IMAGE_REPORTS_DIR):
      report_path = os.path.join(IMAGE_REPORTS_DIR, report_id)

      if os.path.isdir(report_path):
        report_data = {
          "report_id": report_id,
          "metrics": _read_json(os.path.join(report_path, "classification_report.json")),
          "confusion_matrix_base64": _image_to_base64(os.path.join(report_path, "confusion_matrix.png")),
          "last_synced": datetime.utcnow()
        }
        
        database[COL_REPORTS_IMAGE].update_one(
          {"report_id": "best_model_metrics"},
          {"$set": report_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
          upsert=True
        )
        founded_reports += 1
  print(f"[AI IMAGE] In DB used to be {number_of_reports} Image reports, now there are {founded_reports} synced from files.")

def sync_all_reports():
  database = get_database(DB_NAME)
  sync_nlp_report(database)
  sync_image_report(database)
