import os
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Ed's Closet Finder", layout="wide")

st.title("Ed's Closet Storage Finder")
st.caption("Search your stored clothing by item, size, color, or category. Photos + bin location.")

CSV_PATH = "inventory.csv"
PHOTOS_DIR = "photos"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH).fillna("")
    for col in df.columns:
        df[col] = df[col].astype(str)

    df["search_text"] = (
        df["item_id"] + " " +
        df["category"] + " " +
        df["subcategory"] + " " +
        df["size"] + " " +
        df["color"] + " " +
        df["brand"] + " " +
        df["description"] + " " +
        df["bin_id"] + " " +
        df["location"]
    ).str.lower()
    return df

df = load_data()

# Filters (phone friendly)
c1, c2, c3, c4 = st.columns(4)
with c1:
    category = st.selectbox("Category", ["(Any)"] + sorted(df["category"].unique().tolist()))
with c2:
    size = st.selectbox("Size", ["(Any)"] + sorted(df["size"].unique().tolist()))
with c3:
    color = st.selectbox("Color", ["(Any)"] + sorted(df["color"].unique().tolist()))
with c4:
    bin_id = st.selectbox("Bin", ["(Any)"] + sorted(df["bin_id"].unique().tolist()))

query = st.text_input("Search (e.g. 'black t-shirt L', 'navy blazer 42R')").strip().lower()

filtered = df.copy()
if category != "(Any)":
    filtered = filtered[filtered["category"] == category]
if size != "(Any)":
    filtered = filtered[filtered["size"] == size]
if color != "(Any)":
    filtered = filtered[filtered["color"] == color]
if bin_id != "(Any)":
    filtered = filtered[filtered["bin_id"] == bin_id]
if query:
    filtered = filtered[filtered["search_text"].str.contains(query, na=False)]

st.write(f"**Matches:** {len(filtered)}")

COLS = 3
items = filtered.to_dict(orient="records")

for i in range(0, len(items), COLS):
    cols = st.columns(COLS)
    for col, item in zip(cols, items[i:i+COLS]):
        with col:
            photo_file = item.get("photo_file", "")
            photo_path = os.path.join(PHOTOS_DIR, photo_file)

            if os.path.isfile(photo_path):
                img = Image.open(photo_path)
                st.image(img, use_container_width=True)
            else:
                st.warning(f"Missing photo: {photo_file}")

            st.markdown(f"**{item['item_id']}** — {item['category']} ({item['subcategory']})")
            st.text(f"Size: {item['size']} | Color: {item['color']}")
            st.text(f"Bin: {item['bin_id']} | Location: {item['location']}")
            if item.get("brand"):
                st.caption(f"Brand: {item['brand']}")
            if item.get("description"):
                st.caption(item["description"])
