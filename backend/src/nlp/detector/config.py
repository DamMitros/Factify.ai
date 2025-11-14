from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_DIR = ARTIFACT_DIR / "models"
REPORT_DIR = ARTIFACT_DIR / "reports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

NLP_MODEL_NAME = "roberta-base"
NUM_LABELS = 2

DEFAULT_DATA_PATH = DATA_DIR / "Training_Essay_Data.csv"
DEFAULT_MODEL_PATH = MODEL_DIR / "roberta_finetuned.pt"
DEFAULT_METRICS_PATH = REPORT_DIR / "metrics.json"
DEFAULT_CONFUSION_MATRIX_PATH = REPORT_DIR / "confusion_matrix.png"

MC_DROPOUT_ENABLED = True
MC_DROPOUT_PASSES = 16
MC_DROPOUT_RANDOM_SEED = 42

SEGMENT_WORD_TARGET = 50
SEGMENT_STRIDE_WORDS = 25
SEGMENT_MIN_WORDS = 10
SEGMENT_AI_THRESHOLD = 0.65
SEGMENT_HUMAN_THRESHOLD = 0.35

#Docelowo można by tutaj umieścić python-dotenv /tylko to chyba dopiero przy pełnej implementacji mikroserwisu