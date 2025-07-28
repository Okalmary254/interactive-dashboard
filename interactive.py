
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Data Visualizer", layout="wide")
st.title("📊 Interactive Dataset Visualizer")

st.markdown("Upload a CSV file and visualize it with customizable charts.")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()
else:
    st.info("Please upload a CSV file to continue.")
    st.stop()

# Chart selection
chart_type = st.selectbox(
    "Select Visualization Type",
    ["Line Plot", "Bar Plot", "Scatter Plot", "Box Plot", "Histogram", "Heatmap", "Pie Chart"]
)

all_columns = df.columns.tolist()

# Pie chart only needs one categorical column
if chart_type == "Pie Chart":
    pie_col = st.selectbox("Select column for Pie Chart (categorical preferred)", all_columns)
    plot_title = st.text_input("Plot Title", f"Pie Chart of {pie_col}")

    pie_data = df[pie_col].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    ax.set_title(plot_title)
    st.pyplot(fig)

else:
    # For other chart types
    x_axis = st.selectbox("Select X-axis", all_columns)
    y_axis = st.selectbox("Select Y-axis", all_columns)

    plot_title = st.text_input("Plot Title", f"My {chart_type}")
    x_label = st.text_input("X-axis Label", x_axis)
    y_label = st.text_input("Y-axis Label", y_axis)

    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == "Line Plot":
        sns.lineplot(data=df, x=x_axis, y=y_axis, ax=ax)
    elif chart_type == "Bar Plot":
        sns.barplot(data=df, x=x_axis, y=y_axis, ax=ax)
    elif chart_type == "Scatter Plot":
        sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax)
    elif chart_type == "Box Plot":
        sns.boxplot(data=df, x=x_axis, y=y_axis, ax=ax)
    elif chart_type == "Histogram":
        sns.histplot(data=df[y_axis], kde=True, ax=ax)
    elif chart_type == "Heatmap":
        numeric_df = df.select_dtypes(include='number')
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        plot_title = "Correlation Heatmap"
        x_label = ""
        y_label = ""

    ax.set_title(plot_title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    st.pyplot(fig)
