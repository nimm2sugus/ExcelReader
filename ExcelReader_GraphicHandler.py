import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Zeitreihen-Analyse Tool")

uploaded_file = st.file_uploader("Lade eine CSV-Datei hoch", type=["csv"])
if uploaded_file:
    try:
        # Versuch mit utf-8
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        try:
            # Wenn das fehlschlägt, versuche ISO-8859-1
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
        except Exception as e:
            st.error(f"Fehler beim Einlesen der Datei: {e}")
            st.stop()

    # Konvertiere alle Spalten, die wie Zeit aussehen, in datetime
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

        # Für y nur numerische Spalten
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_cols:
            st.error("Keine numerischen Spalten gefunden für y-Achse.")
        else:
            y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)

            if y_cols:
                fig = px.line(df, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")
                st.plotly_chart(fig, use_container_width=True)
