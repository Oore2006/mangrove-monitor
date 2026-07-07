import ee

SERVICE_ACCOUNT = 'mangrove-monitor-app@mangrove-monitor-501613.iam.gserviceaccount.com'
KEY_PATH = 'key.json'
PROJECT_ID = 'mangrove-monitor-501613'

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(credentials, project=PROJECT_ID)

# Sanity check — should print metadata, not throw an auth error
info = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').limit(1).getInfo()
print("SUCCESS - Earth Engine responded:")
print(info['type'])