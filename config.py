"""
config.py

This is the ONLY file that should change when the professor's GEE account
or dataset becomes available. Every other file reads from here and never
hardcodes a data source directly.

Today: uses your personal GEE account + public datasets (Sentinel-2, GMW).
Later: swap the four values below to point at the professor's project,
service account, and mangrove dataset. Nothing else in the app needs to change.
"""

# --- Earth Engine authentication ---
# Leave as None to use interactive personal-account login (ee.Authenticate()).
# When a service account is available, set this to the path of its JSON key
# and set GEE_SERVICE_ACCOUNT_EMAIL to the account's email address.


# GEE_SERVICE_ACCOUNT_EMAIL = None
# GEE_SERVICE_ACCOUNT_KEY_PATH = None



GEE_SERVICE_ACCOUNT_EMAIL = "mangrove-monitor-app@mangrove-monitor-501613.iam.gserviceaccount.com"
GEE_SERVICE_ACCOUNT_KEY_PATH = "key.json"


# The Cloud project registered for Earth Engine access.
# Swap this to the professor's project ID once you have it.
# GEE_PROJECT = "your-personal-project-id"

GEE_PROJECT = "mangrove-monitor-501613"

# --- Data sources ---
# Swap these to the professor's asset IDs once his data is available.
# Until then, these point at public datasets so the app is fully functional today.
SENTINEL2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
MANGROVE_BASELINE_ASSET = "public"  # placeholder flag, see data_sources.py

# --- Areas of interest ---
# Rough bounding boxes for known Nigerian mangrove sites. Replace/refine with
# the professor's precise site boundaries when available.
AOIS = {
    "Niger Delta (sample)": [5.4, 4.3, 6.4, 5.3],       # [minLon, minLat, maxLon, maxLat]
    "Ilaje, Ondo State": [4.6, 6.0, 5.2, 6.4],
    "Cross River Estuary": [8.2, 4.4, 8.9, 5.1],
}

# --- Display / labeling ---
# Purely cosmetic — lets the live map clearly show whether it's running on
# placeholder data or the professor's real dataset.
DATA_SOURCE_LABEL = "Public Sentinel-2 / Global Mangrove Watch (placeholder — awaiting professor's dataset)"
