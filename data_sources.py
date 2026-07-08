"""
data_sources.py

All Earth Engine calls live here: authentication, pulling imagery, and
computing the indices used to identify mangrove extent and health.

Nothing here should know or care whether the underlying data is the public
placeholder or the professor's dataset — that decision is made entirely in
config.py.
"""

import json
import ee
import datetime
import config
import streamlit as st

def initialize_earth_engine():
    if "gee_service_account" in st.secrets:
        # Deployed on Streamlit Cloud — credentials come from secrets, not a file
        info = dict(st.secrets["gee_service_account"])
        credentials = ee.ServiceAccountCredentials(info["client_email"], key_data=json.dumps(info))
        ee.Initialize(credentials, project=config.GEE_PROJECT)
    elif config.GEE_SERVICE_ACCOUNT_EMAIL and config.GEE_SERVICE_ACCOUNT_KEY_PATH:
        # Local development — credentials come from key.json
        credentials = ee.ServiceAccountCredentials(
            config.GEE_SERVICE_ACCOUNT_EMAIL, config.GEE_SERVICE_ACCOUNT_KEY_PATH
        )
        ee.Initialize(credentials, project=config.GEE_PROJECT)
    else:
        ee.Initialize(project=config.GEE_PROJECT)



def get_aoi_geometry(bbox):
    """Converts a [minLon, minLat, maxLon, maxLat] list into an ee.Geometry."""
    return ee.Geometry.Rectangle(bbox)


# def get_latest_sentinel2_composite(aoi, days_back=30, cloud_threshold=20):
#     """
#     Returns the most recent, cloud-filtered Sentinel-2 composite for the
#     given area of interest.

#     days_back: how far back to search for usable imagery. Mangrove coastal
#     scenes are frequently cloudy, so 30 days gives Earth Engine enough
#     candidate images to build a clean composite. Widen this if a site
#     consistently comes back empty.
#     """
#     end = ee.Date(datetime.datetime.now(datetime.timezone.utc))
#     start = end.advance(-days_back, "day")

#     collection = (
#         ee.ImageCollection(config.SENTINEL2_COLLECTION)
#         .filterBounds(aoi)
#         .filterDate(start, end)
#         .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
#     )

#     composite = collection.median().clip(aoi)
#     return composite

#google images cannot displayed with this function, so I will comment it out and use the function below instead

def get_latest_sentinel2_composite(aoi, days_back=30, cloud_threshold=20):
    """
    Returns the most recent, cloud-filtered Sentinel-2 composite for the
    given area of interest. Automatically widens the search window if the
    initial window has no usable imagery — common for coastal/mangrove
    sites with persistent cloud cover.
    """
    end = ee.Date(datetime.datetime.now(datetime.timezone.utc))
    start = end.advance(-days_back, "day")

    collection = (
        ee.ImageCollection(config.SENTINEL2_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
    )

    count = collection.size().getInfo()

    if count == 0:
        # Widen to 90 days and drop the strict cloud cutoff — just take
        # the clearest images available in that longer window instead.
        start = end.advance(-90, "day")
        collection = (
            ee.ImageCollection(config.SENTINEL2_COLLECTION)
            .filterBounds(aoi)
            .filterDate(start, end)
            .sort("CLOUDY_PIXEL_PERCENTAGE")
            .limit(10)
        )
        count = collection.size().getInfo()

    if count == 0:
        raise ValueError(
            "No Sentinel-2 imagery found for this AOI in the last 90 days. "
            "Try a different site, or double-check the AOI coordinates in config.py."
        )

    composite = collection.median().clip(aoi)
    return composite

def compute_indices(image):
    """
    Adds NDVI (vegetation health) and NDWI/MNDWI (water/mangrove boundary)
    bands to a Sentinel-2 image.

    Sentinel-2 band reference used here:
      B3 = green, B4 = red, B8 = near-infrared, B11 = short-wave infrared
    """
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
    return image.addBands([ndvi, ndwi, mndwi])


def get_map_tile_url(image, vis_params):
    """
    Generates a tile URL for a processed image so a Streamlit/Leaflet/folium
    map can display it as a layer, the same way it would display Google Maps
    base tiles.
    """
    map_id_dict = ee.Image(image).getMapId(vis_params)
    return map_id_dict["tile_fetcher"].url_format


def get_mangrove_layer(aoi_key):
    """
    Top-level convenience function the Streamlit app calls: given an AOI
    name from config.AOIS, returns ready-to-display tile URLs for the
    true-color composite and the NDVI/NDWI overlays.
    """
    bbox = config.AOIS[aoi_key]
    aoi = get_aoi_geometry(bbox)

    composite = get_latest_sentinel2_composite(aoi)
    processed = compute_indices(composite)

    true_color_vis = {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000}
    ndvi_vis = {"bands": ["NDVI"], "min": -0.2, "max": 0.8,
                "palette": ["#8B4513", "#F5DEB3", "#9ACD32", "#006400"]}
    ndwi_vis = {"bands": ["MNDWI"], "min": -0.5, "max": 0.5,
                "palette": ["#8B4513", "#F5DEB3", "#87CEEB", "#00008B"]}

    return {
        "true_color_url": get_map_tile_url(processed, true_color_vis),
        "ndvi_url": get_map_tile_url(processed, ndvi_vis),
        "ndwi_url": get_map_tile_url(processed, ndwi_vis),
        "centroid": aoi.centroid().coordinates().getInfo(),
    }
