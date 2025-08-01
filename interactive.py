import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

st.set_page_config(page_title="Data Visualizer+", layout="wide")
st.title("📊 Advanced Interactive Dataset Visualizer & Cleaner")

st.markdown("""
Upload a **CSV**, **Excel (.xlsx)**, or **Stata (.dta)** file to:
- Automatically clean and explore your dataset
- Visualize trends with interactive charts
- Export cleaned dataset and charts
""")

uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "dta"])

def load_data(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            xls = pd.ExcelFile(file)
            sheet = st.selectbox("Select Excel sheet", xls.sheet_names)
            return pd.read_excel(xls, sheet_name=sheet)
        elif file.name.endswith(".dta"):
            return pd.read_stata(file)
        else:
            st.error("Unsupported file format.")
            return None
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def clean_data(df):
    cleaned_df = df.copy()
    for col in cleaned_df.columns:
        if cleaned_df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)
            elif pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
            else:
                cleaned_df[col].fillna(cleaned_df[col].mode()[0], inplace=True)
    return cleaned_df

def get_table_download_link(df, filename="cleaned_data.csv"):
    csv = df.to_csv(index=False).encode()
    b64 = base64.b64encode(csv).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Cleaned CSV</a>'

def get_image_download_link(buf, filename="chart.png"):
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'<a href="data:image/png;base64,{b64}" download="{filename}">Download Chart Image</a>'

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.success("File uploaded successfully!")
        st.write("### Preview of Original Data")
        st.dataframe(df.head())

        st.markdown("### Dataset Summary")
        st.write("**Shape:**", df.shape)
        st.write("**Column Types:**")
        st.dataframe(df.dtypes.rename("Data Type"))

        st.markdown("### Missing Values")
        st.dataframe(df.isnull().sum().rename("Missing Values"))

        enable_cleaning = st.checkbox("🧹 Enable Auto-Cleaning (fill missing values)", value=True)

        if enable_cleaning:
            df_cleaned = clean_data(df)
            st.write("### Cleaned Dataset Preview")
            st.dataframe(df_cleaned.head())

            # Download cleaned dataset
            st.markdown(get_table_download_link(df_cleaned), unsafe_allow_html=True)
        else:
            df_cleaned = df

        st.markdown("---")

        # Column filtering
        st.subheader("Select Columns to Work With")
        selected_columns = st.multiselect("Choose columns to include", df_cleaned.columns.tolist(), default=df_cleaned.columns.tolist())
        df_filtered = df_cleaned[selected_columns]
        st.write("Filtered Data:")
        st.dataframe(df_filtered.head())

        st.markdown("---")
        st.subheader("Visualizations")

        chart_type = st.selectbox(
            "Select Visualization Type",
            ["Line Plot", "Bar Plot", "Scatter Plot", "Box Plot", "Histogram", "Heatmap", "Pie Chart"]
        )

        all_columns = df_filtered.columns.tolist()

        buf = io.BytesIO()  # for chart export

        if chart_type == "Pie Chart":
            pie_col = st.selectbox("Select column for Pie Chart (categorical preferred)", all_columns)
            plot_title = st.text_input("Plot Title", f"Pie Chart of {pie_col}")
            pie_data = df_filtered[pie_col].value_counts()

            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            ax.set_title(plot_title)
            st.pyplot(fig)
            fig.savefig(buf, format="png")
        
        else:
            x_axis = st.selectbox("Select X-axis", all_columns)
            y_axis = st.selectbox("Select Y-axis", all_columns)

            plot_title = st.text_input("Plot Title", f"My {chart_type}")
            x_label = st.text_input("X-axis Label", x_axis)
            y_label = st.text_input("Y-axis Label", y_axis)

            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "Line Plot":
                sns.lineplot(data=df_filtered, x=x_axis, y=y_axis, ax=ax)
            elif chart_type == "Bar Plot":
                sns.barplot(data=df_filtered, x=x_axis, y=y_axis, ax=ax)
            elif chart_type == "Scatter Plot":
                sns.scatterplot(data=df_filtered, x=x_axis, y=y_axis, ax=ax)
            elif chart_type == "Box Plot":
                sns.boxplot(data=df_filtered, x=x_axis, y=y_axis, ax=ax)
            elif chart_type == "Histogram":
                sns.histplot(data=df_filtered[y_axis], kde=True, ax=ax)
            elif chart_type == "Heatmap":
                numeric_df = df_filtered.select_dtypes(include='number')
                corr = numeric_df.corr()
                sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                plot_title = "Correlation Heatmap"
                x_label = ""
                y_label = ""

            ax.set_title(plot_title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            st.pyplot(fig)
            fig.savefig(buf, format="png")

        # Export chart
        st.markdown(get_image_download_link(buf), unsafe_allow_html=True)

else:
    st.info("Please upload a dataset to begin.")
