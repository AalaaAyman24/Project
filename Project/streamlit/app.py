import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io

# Step 1: Upload dataset
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Dataset Preview", df.head())

    # Step 2: Dataset Info and Summary
    st.header("1. Dataset Information and Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Basic Information")
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        st.text(info_str)
    with col2:
        st.subheader("Summary Statistics")
        st.write(df.describe())

    # Additional checks
    st.subheader("Additional Insights")
    st.write("### Columns with Constant Values:")
    constant_cols = [col for col in df.columns if df[col].nunique() == 1]
    st.write(constant_cols if constant_cols else "No constant columns found.")

    st.write("### Columns with High Cardinality:")
    high_cardinality_cols = [
        col for col in df.columns if df[col].nunique() > 0.9 * len(df)]
    st.write(
        high_cardinality_cols if high_cardinality_cols else "No high-cardinality columns found.")

    # Step 3: Data Analysis
    st.header("2. Data Analysis")
    st.subheader("Missing Values")
    missing_values = df.isnull().sum()
    st.write(missing_values[missing_values > 0])

    st.subheader("Outlier Detection (IQR Method)")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outliers = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_count = ((df[col] < (Q1 - 1.5 * IQR)) |
                         (df[col] > (Q3 + 1.5 * IQR))).sum()
        outliers[col] = outlier_count
    st.write("Outliers per column:", outliers)

    # Step 4: Advanced Preprocessing
    st.header("3. Data Preprocessing")
    st.subheader("Handling Missing Values")
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            st.write(f"Column '{col}' has missing values.")
            # التحقق من نوع العمود
            if df[col].dtype in [np.float64, np.int64]:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                has_outliers = ((df[col] < (Q1 - 1.5 * IQR))
                                | (df[col] > (Q3 + 1.5 * IQR))).any()

                if has_outliers:
                    st.warning(
                        f"Column '{col}' contains outliers. Using Mean may not be appropriate.")
                    fill_options = ["Median", "Mode", "Drop"]
                else:
                    fill_options = ["Mean", "Median", "Mode", "Drop"]
            else:
                fill_options = ["Mode", "Drop"]

            fill_method = st.radio(
                f"How to handle missing values in '{col}'?", fill_options, key=col)
            if fill_method == "Mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif fill_method == "Median":
                df[col].fillna(df[col].median(), inplace=True)
            elif fill_method == "Mode":
                df[col].fillna(df[col].mode()[0], inplace=True)
            elif fill_method == "Drop":
                df.dropna(subset=[col], inplace=True)

    st.subheader("Handling Categorical Data")
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        st.write(f"Encoding categorical column: '{col}'")
        df[col] = df[col].astype('category').cat.codes

    st.subheader("Duplicate Row Removal")
    duplicate_count = df.duplicated().sum()
    st.write(f"Number of duplicate rows: {duplicate_count}")
    if duplicate_count > 0:
        st.write("Removing duplicates...")
        df.drop_duplicates(inplace=True)

    # Step 5: Visualizations
    st.header("4. Data Visualization")
    st.subheader("Correlation Heatmap")
    corr_matrix = df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    st.subheader("Distribution Plots for Numeric Columns")
    for col in numeric_cols:
        fig, ax = plt.subplots()
        sns.histplot(df[col], kde=True, ax=ax)
        ax.set_title(f"Distribution of {col}")
        st.pyplot(fig)

    st.subheader("Boxplots for Numeric Columns")
    for col in numeric_cols:
        fig, ax = plt.subplots()
        sns.boxplot(x=df[col], ax=ax)
        ax.set_title(f"Boxplot of {col}")
        st.pyplot(fig)

    st.subheader("Pairplot for Numeric Columns")
    if len(numeric_cols) > 1:
        fig = sns.pairplot(df[numeric_cols])
        st.pyplot(fig)

    # Step 6: Download Cleaned Dataset
    st.header("5. Download Cleaned Dataset")
    cleaned_file = io.BytesIO()
    df.to_csv(cleaned_file, index=False)
    cleaned_file.seek(0)
    st.download_button(label="Download Cleaned Dataset",
                       data=cleaned_file,
                       file_name="cleaned_dataset.csv",
                       mime="text/csv")
else:
    st.info("Please upload a CSV file to start the preprocessing workflow.")
