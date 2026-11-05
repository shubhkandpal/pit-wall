"""Project-wide settings: where files live, which seasons we use, API limits."""

from pathlib import Path

# Folders (all under the repo's data/ folder, which git ignores)
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
DB_PATH = DATA_DIR / "pitwall.duckdb"

# Seasons
YEARS = (2023, 2024, 2025, 2026)
TRAIN_YEARS = (2023, 2024, 2025)
HOLDOUT_YEAR = 2026  # never look at this season until PREDICTION.md is committed

# OpenF1 API
API_BASE = "https://api.openf1.org/v1"
MIN_SECONDS_BETWEEN_CALLS = 2.5  # free tier: 30 requests a minute, so stay under that
MAX_RETRIES = 5
REQUEST_TIMEOUT = 30  # seconds
