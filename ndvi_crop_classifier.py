# ndvi_crop_classifier.py

import pandas as pd
import streamlit as st
from io import StringIO

# ---- App Title ----
st.set_page_config(page_title="NDVI Crop Classifier", page_icon="🌾", layout="centered")
st.title("🌾 NDVI-Based Crop Classification")
st.markdown("Upload your NDVI data in CSV format to classify different crop seasons.")

# ---- NDVI Classification Function ----
def classify_ndvi(df):
    """Classify NDVI data into crop seasons based on seasonal peak NDVI values."""
    results = []
    try:
        date_col = df.columns[0]  # Assume the first column is date
        for prop in df.columns[1:]:  # All other columns are properties
            values = df[prop]
            dates = pd.to_datetime(df[date_col], format='%d-%m-%Y')
            kharif = values[dates.dt.month.isin([7, 8, 9])].max()  # Jul-Sep
            rabi = values[dates.dt.month.isin([11, 12, 1, 2])].max()  # Nov-Feb
            zaid = values[dates.dt.month.isin([4, 5, 6])].max()  # Apr-Jun

            # Crop classification based on NDVI thresholds
            if values.max() <= 0.1:
                cls, val = "Water", 4
            elif 0.1 < values.max() < 0.3:
                cls, val = "Rangeland", 0
            else:
                if kharif >= 0.4 and zaid >= 0.4:
                    cls, val = "Kharif, Zaid", 8
                elif kharif >= 0.4 and rabi >= 0.35:
                    cls, val = "Kharif, Rabi", 2
                elif kharif >= 0.4:
                    cls, val = "Kharif Only", 1
                elif rabi >= 0.35:
                    cls, val = "Rabi Only", 6
                else:
                    cls, val = "Rangeland", 0

            results.append({
                'Property': prop,
                'Class Name': cls,
                'Value': val,
                'Kharif Peak NDVI': round(kharif, 3),
                'Rabi Peak NDVI': round(rabi, 3),
                'Zaid Peak NDVI': round(zaid, 3)
            })
    except Exception as e:
        st.error(f"Classification error: {e}")
        return pd.DataFrame()

    return pd.DataFrame(results)

# ---- File Upload Section ----
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file is not None:
    try:
        # Read uploaded CSV
        df = pd.read_csv(uploaded_file)
        st.success("✅ File Uploaded Successfully!")
        st.write("### Preview of Uploaded Data:")
        st.dataframe(df.head())

        # Perform classification
        result_df = classify_ndvi(df)

        if not result_df.empty:
            st.success("✅ NDVI Classification Completed!")
            st.write("### Classification Results:")
            st.dataframe(result_df)

            # Allow user to download result as CSV
            csv_download = result_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Classification Results",
                data=csv_download,
                file_name="ndvi_classification_results.csv",
                mime="text/csv"
            )

            # Visualize Classification
            st.write("### Crop Classification Visualization:")
            st.bar_chart(result_df.set_index('Property')['Value'])
        else:
            st.warning("⚠️ No results to display. Please check your input data.")

    except Exception as e:
        st.error(f"❌ Error processing the file: {e}")
else:
    st.info("📄 Please upload a CSV file to get started.")

# ---- Footer ----
st.markdown("---")
st.caption("Developed by Dr Sachchidanand Singh with ❤️ using Streamlit")
