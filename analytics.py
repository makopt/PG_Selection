import streamlit as st
import pandas as pd

st.set_page_config(page_title="Postgraduate Application Analyzer", layout="wide")

st.title("📊 Postgraduate Applicants Data Analyzer")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

# This function normalizes GPA values to a percentage scale (0-5)
# If GPA/5, remove the string /5 then convert to float 
# If GPA/4, remove the string /4, multipling by 5/4 then convert to float 
# If GPA/100, remove the string /100, multipling by 5/100 then convert to float
def normalize_gpa(gpa_str):
    if isinstance(gpa_str, str):
        gpa_str = gpa_str.strip()
        n_gpa = None
        if "/5" in gpa_str: # Convert GPA/5 to two decimal float
            n_gpa = float(gpa_str.replace("/5", "").strip())
        elif "/4" in gpa_str:
            n_gpa = float(gpa_str.replace("/4", "").strip()) * (5 / 4)
        elif "/100" in gpa_str:
            n_gpa = float(gpa_str.replace("/100", "").strip()) * (5 / 100)
        n_gpa = round(n_gpa, 2) if n_gpa is not None else None
        if n_gpa > 5 or n_gpa < 0:
            return None
        return n_gpa
    return None
if uploaded_file:
    df_raw = pd.read_excel(uploaded_file, sheet_name=0)

    # Assume first row is actual column names
    df = df_raw.iloc[1:].copy()
    df.columns = df_raw.iloc[0]
    df = df.dropna(how="all")
    
    # Get the columns names from the first row and set them as the new header
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.reset_index(drop=True)
    

    # Normalize fields
    df["GPA_Normalized"] = df["GPA"].apply(normalize_gpa)
    df["Aptitude_Score"] = pd.to_numeric(df["Aptitude_Score"], errors='coerce')

    st.markdown("---")
    st.markdown("### 📊 Data Overview")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Data Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔹 Gender Distribution**")
        st.bar_chart(df["Gender"].value_counts())

        st.markdown("**🔹 Top 10 Programs**")
        st.dataframe(df["Program"].value_counts().head(10))

        st.markdown("**🔹 Top 20 Bachelor Majors**")
        st.dataframe(df["Bachelor_Major"].value_counts().head(10))

        st.markdown("**🔹 Top 20 Universities**")
        st.dataframe(df["Graduated_From"].value_counts().head(10))

    with col2:
        st.markdown("**🔹 GPA Distribution (Normalized to 5)**")
        st.dataframe(df["GPA_Normalized"].describe())
        st.line_chart(df["GPA_Normalized"].dropna())

        st.markdown("**🔹 Aptitude Score Statistics**")
        st.dataframe(df["Aptitude_Score"].describe())
        st.line_chart(df["Aptitude_Score"].dropna())

        st.markdown("**🔹 GPA vs Aptitude Score**")
        st.scatter_chart(df[["GPA_Normalized", "Aptitude_Score"]].dropna(), x="GPA_Normalized", y="Aptitude_Score")


    st.markdown("---")
    
    st.subheader("🔍 Filtered View")
    selected_program = st.selectbox("Filter by Program", ["All"] + sorted(df["Program"].dropna().unique()))
    if selected_program != "All":
        st.dataframe(df[df["Program"] == selected_program])
    else:
        st.dataframe(df)

    st.markdown("---")
    # Write the selected program in markdown
    st.markdown(f"### 📊 Filtered Data for Program: {selected_program}")
    # Display filtered data summary like Data Summary done for the whole data
    df_filtered = df[df["Program"] == selected_program] if selected_program != "All" else df
    col1, col2 = st.columns(2)
   
    with col1:
        st.markdown("**🔹 Filterd Gender Distribution**")
        st.bar_chart(df_filtered["Gender"].value_counts())


    # Download button for the filtered data
    if selected_program != "All":
        filtered_filename = f"filtered_data_{selected_program}.xlsx"
    else:
        filtered_filename = "filtered_data_all.xlsx"
    if st.button("Download Filtered Data"):
        df_filtered = df[df["Program"] == selected_program] if selected_program != "All" else df
        df_filtered.to_excel(filtered_filename, index=False)
        st.success(f"Filtered data saved as {filtered_filename}")
    
    


st.markdown("---")
st.markdown("Made with ❤️ by Mahdi Khemakhem")