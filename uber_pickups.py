import streamlit as st
import pandas as pd
import kagglehub
import os
import pycountry
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

dataset = "starbucks/store-locations"
download_path = "data/"
api.dataset_download_files(dataset, path=download_path, unzip=True)
df = pd.read_csv(os.path.join(download_path, "starbucks_locations.csv"))

# -----------------------------
# 2️⃣ ตั้งค่า Streamlit Page
# -----------------------------
st.set_page_config(page_title="Starbucks Store Dashboard", layout="wide")
st.title("☕ Starbucks Store Locations Dashboard")

st.write(f"จำนวนข้อมูลทั้งหมด: **{len(df)} สาขา**")
st.write("เลือกประเทศและเมืองเพื่อดูตำแหน่งสาขา Starbucks บนแผนที่ 🌍")

# -----------------------------
# 3️⃣ แปลงรหัสประเทศเป็นชื่อเต็ม
# -----------------------------
def get_country_name(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code

if "Country" in df.columns:
    df["Country Name"] = df["Country"].apply(get_country_name)
else:
    st.error("ไม่พบคอลัมน์ 'Country' ใน dataset")

# -----------------------------
# 4️⃣ ฟิลเตอร์ Country และ City
# -----------------------------
st.subheader("🗺️ แผนที่แสดงตำแหน่งร้าน Starbucks")

# Country dropdown พร้อมตัวเลือก "ทั้งหมด"
country_options = sorted(df["Country Name"].dropna().unique())
country_options = ["ทั้งหมด"] + country_options
country = st.selectbox("เลือกประเทศ (Country)", country_options)

# กรองข้อมูลตาม Country
filtered_df = df.copy()
if country != "ทั้งหมด":
    filtered_df = filtered_df[df["Country Name"] == country]

# City dropdown พร้อมตัวเลือก "ทั้งหมด"
city_options = sorted(filtered_df["City"].dropna().unique())
city = st.selectbox("เลือกเมือง (City)", ["ทั้งหมด"] + city_options)
if city != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df["City"] == city]

st.write(f"พบทั้งหมด **{len(filtered_df)} สาขา** ใน {country}{' - ' + city if city != 'ทั้งหมด' else ''}")

# -----------------------------
# 5️⃣ Search box สำหรับชื่อสาขา
# -----------------------------
search_name = st.text_input("ค้นหาชื่อสาขา")
if search_name:
    filtered_df = filtered_df[filtered_df["Store Name"].str.contains(search_name, case=False, na=False)]
    st.write(f"พบ **{len(filtered_df)} สาขา** ตามคำค้น '{search_name}'")

# -----------------------------
# 6️⃣ แสดงแผนที่
# -----------------------------
if {"Latitude", "Longitude"}.issubset(filtered_df.columns):
    # ลบแถวที่ไม่มีค่าพิกัด
    map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])

    st.write(f"จำนวนสาขาที่มีพิกัดจริง: **{len(map_df)} สาขา**")

    if len(map_df) == 0:
        st.warning("ไม่มีข้อมูลพิกัดสำหรับประเทศ/เมืองที่เลือก")
    else:
        st.map(map_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
else:
    st.warning("ไม่พบข้อมูลพิกัด (Latitude/Longitude) ใน dataset")

# -----------------------------
# 7️⃣ แสดงตารางข้อมูลเพิ่มเติม
# -----------------------------
st.subheader("📋 รายละเอียดสาขา Starbucks ตามฟิลเตอร์")

columns_to_show = ["Store Name", "Phone Number", "Street Address", "City", "Country Name"]

# ตรวจสอบว่าคอลัมน์มีอยู่จริง
columns_to_show = [col for col in columns_to_show if col in filtered_df.columns]

if len(filtered_df) > 0:
    st.dataframe(filtered_df[columns_to_show].reset_index(drop=True))
else:
    st.warning("ไม่มีข้อมูลสาขาตามฟิลเตอร์ที่เลือก")

