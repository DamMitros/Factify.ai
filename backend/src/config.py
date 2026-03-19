import os

GLOBAL_PATH_PREFIX = os.getenv("BACKEND_GLOBAL_PATH_PREFIX", "/api")

MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")

DB_NAME = "factify"

COL_POSTS = "posts"
COL_COMMENTS = "comments"
COL_USERS = "users"
# COL_ANALYSIS_AI_TEXT = "analysis_ai_text"
# COL_ANALYSIS_AI_IMAGE = "analysis_ai_image"
COL_ANALYSIS_AI_TEXT = "analysis" #TYMCZASOWE
COL_ANALYSIS_AI_IMAGE = "image_analysis" #TYMCZASOWE
COL_ANALYSIS_MANIPULATION = "analysis_manipulation"
COL_ANALYSIS_SOURCES = "analysis_sources"
COL_CRON_TASKS = "cron_tasks"
