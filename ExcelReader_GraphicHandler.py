import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Zeitreihen-Analyse Tool")

uploaded_file = st.file_uploader("Lade eine CSV- oder Excel-Datei hoch", type=["csv", "xlsx"])
if uploaded_file:
    # Datei je nach Typ einlesen
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    # Zeitspalten erkennen
    time_candidates = []
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='raise')
            time_candidates.append(col)
        except:
            continue

    if not time_candidates:
        st.error("Keine Zeitspalte erkannt. Bitte stelle sicher, dass eine Spalte gültige Datumswerte enthält.")
    else:
        x_col = st.selectbox("Wähle die Zeitspalte (x-Achse)", time_candidates)

        # Nur numerische Spalten für y
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_cols:
            st.error("Keine numerischen Spalten gefunden für die y-Achse.")
        else:
            y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)

            if y_cols:
                fig = px.line(df, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")
                st.plotly_chart(fig, use_container_width=True)
