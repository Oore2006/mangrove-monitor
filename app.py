"""
app.py

The live feed frontend. Run with: streamlit run app.py

This file is intentionally thin — it only handles layout and user interaction.
All Earth Engine logic lives in data_sources.py, and all source/AOI
configuration lives in config.py, so this file should rarely need to change.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium

import config
import data_sources

st.set_page_config(page_title="Nigeria Mangrove Live Monitor", layout="wide")

st.title("Nigeria Mangrove Monitoring — Live Feed")
st.caption(
    "Prototype live feed for satellite-based mangrove monitoring. "
    "This first version proves the map + data pipeline works end to end."
)

# --- Sidebar controls ---
st.sidebar.header("Controls")

aoi_choice = st.sidebar.selectbox("Site (area of interest)", list(config.AOIS.keys()))

layer_choice = st.sidebar.radio(
    "Layer",
    ["True color", "Vegetation health (NDVI)", "Water / mangrove boundary (NDWI)"],
)

st.sidebar.divider()
st.sidebar.markdown("**Data source**")
st.sidebar.info(config.DATA_SOURCE_LABEL)

# --- Earth Engine initialization (cached so it only runs once per session) ---
@st.cache_resource
def init_ee():
    data_sources.initialize_earth_engine()
    return True

@st.cache_data(ttl=3600)  # refresh hourly — matches realistic satellite revisit cadence
def load_layer_data(aoi_key):
    return data_sources.get_mangrove_layer(aoi_key)


try:
    init_ee()
    layer_data = load_layer_data(aoi_choice)
    ee_ready = True
except Exception as e:
    ee_ready = False
    st.error(
        "Could not connect to Earth Engine. This usually means authentication "
        "hasn't been set up yet — see the README for the one-time setup steps."
    )
    st.exception(e)

# --- Map ---
if ee_ready:
    lon, lat = layer_data["centroid"]
    fmap = folium.Map(location=[lat, lon], zoom_start=10, tiles="CartoDB positron")

    url_map = {
        "True color": ("true_color_url", "True color (Sentinel-2)"),
        "Vegetation health (NDVI)": ("ndvi_url", "NDVI"),
        "Water / mangrove boundary (NDWI)": ("ndwi_url", "MNDWI"),
    }
    url_key, layer_name = url_map[layer_choice]

    folium.TileLayer(
        tiles=layer_data[url_key],
        attr="Google Earth Engine",
        name=layer_name,
        overlay=True,
    ).add_to(fmap)

    folium.LayerControl().add_to(fmap)

    st_folium(fmap, width=None, height=600)

    st.caption(
        f"Showing: {layer_choice} — {aoi_choice}. "
        "Refreshes hourly with the latest available cloud-filtered Sentinel-2 pass."
    )
else:
    st.info("Fix the connection issue above, then reload the page.")