import streamlit as st
import pandas as pd

st.set_page_config(page_title="Postgraduate Application Analyzer", layout="wide")

st.title("📊 Postgraduate Applicants Data Analyzer and Selection Process")

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
    # Remove the two first rows
    df_raw = df_raw.iloc[2:].reset_index(drop=True)
    # Remove the two last rows
    df_raw = df_raw.iloc[:-2].reset_index(drop=True)
    df = df_raw.copy()
    df.columns = [
        "Name", "National_ID", "Phone", "Email", "Status", "Program",
        "Semester", "Bachelor_Major", "Graduated_From", "GPA", "Tests_Taken",
        "Gender", "Aptitude_Score", "GPA_Normalized", "PSAU_Graduated"
    ]

    # Normalize fields
    df["GPA_Normalized"] = df["GPA"].apply(normalize_gpa)
    df["Aptitude_Score"] = pd.to_numeric(df["Aptitude_Score"], errors='coerce')
    # If "Tests_Taken" is empty or "N/A", set it to 0 and convert to numeric
    df["Tests_Taken"] = df["Tests_Taken"].replace({"": 0, "N/A": 0})
    df["Tests_Taken"] = pd.to_numeric(df["Tests_Taken"], errors='coerce').fillna(0)
    # Fill PSAU_Graduated to 100 if Graduated_From is "جامعة الأمير سطام بن عبدالعزيز" else 0
    df["PSAU_Graduated"] = df["Graduated_From"].apply(lambda x: 100 if x == "جامعة الأمير سطام بن عبدالعزيز" else 0)
    
    st.markdown("---")
    st.markdown("### 💾 Data Overview")
    # Add a search bar that search in selected columns
    search_term = st.text_input("🔎 Search", "")
    if search_term:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📖 Data Summary")

    col1, col2 = st.columns(2)
    # Display the total number of applicants
    
    with col1:
        st.markdown(f"**🔶 Total Applicants: {len(df)}**") 

        st.markdown("**🔶 Gender Distribution**")
        st.bar_chart(df["Gender"].value_counts())

        st.markdown("**🔶 Top 10 Programs**")
        st.dataframe(df["Program"].value_counts().head(10))

        st.markdown("**🔶 Top 20 Bachelor Majors**")
        st.dataframe(df["Bachelor_Major"].value_counts().head(10))

        st.markdown("**🔶 Top 20 Universities**")
        st.dataframe(df["Graduated_From"].value_counts().head(10))

    with col2:
        st.markdown("**🔶 GPA Distribution (Normalized to 5)**")
        st.dataframe(df["GPA_Normalized"].describe())
        st.line_chart(sorted(df["GPA_Normalized"].dropna()))
        
        st.markdown("**🔶 Aptitude Score Statistics**")
        st.dataframe(df["Aptitude_Score"].describe())
        st.line_chart(sorted(df["Aptitude_Score"].dropna()))

        st.markdown("**🔶 GPA vs Aptitude Score**")
        st.scatter_chart(df[["GPA_Normalized", "Aptitude_Score"]].dropna(), x="GPA_Normalized", y="Aptitude_Score")


    st.markdown("---")
    
    st.subheader("☑️ Filtered PG Program View")
    selected_program = st.selectbox("Select the PG Program", ["All"] + sorted(df["Program"].dropna().unique()))
    if selected_program != "All":
        st.dataframe(df[df["Program"] == selected_program])
    else:
        st.dataframe(df)
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
    st.markdown(f"### 📈 Satatistics for Selected Program: {selected_program}")
    df_filtered = df[df["Program"] == selected_program] if selected_program != "All" else df
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🔷 Total Applicants: {len(df_filtered)}**")

        st.markdown("**🔷 Filterd Gender Distribution**")
        st.bar_chart(df_filtered["Gender"].value_counts())

        st.markdown("**🔷 Filterd Top 20 Bachelor Majors**")
        st.dataframe(df_filtered["Bachelor_Major"].value_counts().head(10))

        st.markdown("**🔷 Filterd Top 20 Universities**")
        st.dataframe(df_filtered["Graduated_From"].value_counts().head(10))

    with col2:
        st.markdown("**🔷 Filterd GPA Distribution (Normalized to 5)**")
        st.dataframe(df_filtered["GPA_Normalized"].describe())
        st.line_chart(sorted(df_filtered["GPA_Normalized"].dropna()))

        st.markdown("**🔷 Filterd Aptitude Score Statistics**")
        st.dataframe(df_filtered["Aptitude_Score"].describe())
        st.line_chart(sorted(df_filtered["Aptitude_Score"].dropna()))

        st.markdown("**🔷 Filterd GPA vs Aptitude Score**")
        st.scatter_chart(df_filtered[["GPA_Normalized", "Aptitude_Score"]].dropna(), x="GPA_Normalized", y="Aptitude_Score")

    st.markdown("---")
    st.markdown(f"### ⚙️ Score Calculation: {selected_program}")

    st.markdown("#### 🔷 Select Considered Majors:")
    selected_majors = st.multiselect("Remove Excluded Majors", sorted(df_filtered["Bachelor_Major"].dropna().unique()), default=sorted(df_filtered["Bachelor_Major"].dropna().unique()))
    df_filtered = df_filtered[df_filtered["Bachelor_Major"].isin(selected_majors)]
    st.info(f"Total Applicants after filtering: {len(df_filtered)}")
    st.dataframe(df_filtered)

    st.markdown("#### 🔷 Select Considered Universities:")
    selected_universities = st.multiselect("Remove Excluded Universities", sorted(df_filtered["Graduated_From"].dropna().unique()), default=sorted(df_filtered["Graduated_From"].dropna().unique()))
    df_filtered = df_filtered[df_filtered["Graduated_From"].isin(selected_universities)]
    st.info(f"Total Applicants after filtering: {len(df_filtered)}")
    st.dataframe(df_filtered)
    
    st.markdown("#### 🔷 Score Calculation Formula:")
    gpa_rate = st.number_input("GPA Rate (0.3-1.0)", min_value=0.3, max_value=1.0, value=0.5, step=0.05)
    aptitude_rate = st.number_input("Aptitude Rate (0.3-0.5)",  min_value=0.3, max_value=0.5, value=0.5, step=0.05)
    tests_rate = st.number_input("English Rate (0.0-0.3)", min_value=0.0, max_value=0.3, value=0.0, step=0.05)
    graduate_from_rate = st.number_input("Rate (0.0-0.2)", min_value=0.0, max_value=0.2, value=0.0, step=0.05) if st.checkbox("Graduate from PSAU Rate?", value=False) else 0.0
    gpa_rate = round(gpa_rate, 2)
    aptitude_rate = round(aptitude_rate, 2)
    tests_rate = round(tests_rate, 2)
    graduate_from_rate = round(graduate_from_rate, 2)
    # assert that the sum of the rates is less than 1.0
    if gpa_rate + aptitude_rate + tests_rate + graduate_from_rate != 1.0:
        st.warning("##### ⚠️ Warning: The sum of the rates should be equal to 1.0")
    else:
        if graduate_from_rate > 0.0:
            st.info(f"##### Score = {gpa_rate} x GPA + {aptitude_rate} x Aptitude + {tests_rate} x English + {graduate_from_rate} x PSAU")
        else:
            st.info(f"##### Score = {gpa_rate} x GPA + {aptitude_rate} x Aptitude + {tests_rate} x English")
        # Calculate the score for each applicant
        df_filtered["Score"] = (df_filtered["GPA_Normalized"] * 20 * gpa_rate +
                                df_filtered["Aptitude_Score"] * aptitude_rate +
                                df_filtered["Tests_Taken"] * tests_rate +
                                df_filtered["PSAU_Graduated"] * graduate_from_rate)
        # Sort the applicants by score
        df_filtered = df_filtered.sort_values(by="Score", ascending=False)
        st.markdown("---")
        st.markdown(f"### 🏆 Selection Result: {selected_program}")
        # Display the top x applicants, x is given by the user
        top_x = st.number_input("Top X Applicants", min_value=1, max_value=len(df_filtered), value=10, step=1)
        st.markdown(f"#### ✅ Top {top_x} Applicants")
        st.dataframe(df_filtered.head(top_x)[["Name", "National_ID", "Gender", "Score", "GPA_Normalized", "Aptitude_Score", "Bachelor_Major", "Graduated_From",]])
        df_selected = df_filtered.head(top_x)[["Name", "National_ID","Gender", "Score", "GPA_Normalized", "Aptitude_Score", "Bachelor_Major", "Graduated_From",]]
        # Download button for the selected data
        selected_filename = f"selected_data_{selected_program}.xlsx"
        if st.button("Download Selected Applicants"):
            df_selected.to_excel(selected_filename, index=False)
            st.success(f"Selected data saved as {selected_filename}")
        st.markdown("#### ✅ Selected Applicants Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Slected Gender Distribution**")
            st.bar_chart(df_selected["Gender"].value_counts())

            st.markdown("**✅ Slected Top 20 Bachelor Majors**")
            st.dataframe(df_selected["Bachelor_Major"].value_counts().head(20))

            st.markdown("**✅ Slected Top 20 Universities**")
            st.dataframe(df_selected["Graduated_From"].value_counts().head(20))

            st.markdown("**✅ Slected Score Distribution**")
            st.dataframe(df_selected["Score"].describe())
            st.line_chart(sorted(df_selected["Score"].dropna()))
        with col2:
            st.markdown("**✅ Slected GPA Distribution (Normalized to 5)**")
            st.dataframe(df_selected["GPA_Normalized"].describe())
            st.line_chart(sorted(df_selected["GPA_Normalized"].dropna()))

            st.markdown("**✅ Slected Aptitude Score Statistics**")
            st.dataframe(df_selected["Aptitude_Score"].describe())
            st.line_chart(sorted(df_selected["Aptitude_Score"].dropna()))

            st.markdown("**✅ Slected GPA vs Aptitude Score**")
            st.scatter_chart(df_selected[["GPA_Normalized", "Aptitude_Score"]].dropna(), x="GPA_Normalized", y="Aptitude_Score")

        

st.markdown("---")
st.markdown("Made by Mahdi Khemakhem")
st.markdown("All rights not reserved 😎")