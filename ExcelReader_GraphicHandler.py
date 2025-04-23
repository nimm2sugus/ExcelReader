import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Zeitreihen-Analyse Tool")

uploaded_file = st.file_uploader("Lade eine CSV-Datei hoch", type=["csv"])
if uploaded_file:
    try:
        # Versuche gängige Trennzeichen automatisch zu erkennen
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=None, engine='python')
    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
        st.stop()

    # Versuche, erste Spalte explizit als Zeit zu parsen
    df.columns = df.columns.str.strip()  # Spaltennamen säubern
    first_col = df.columns[0]

    try:
        df[first_col] = df[first_col].astype(str).str.replace(" Uhr", "", regex=False).str.strip()
        df[first_col] = pd.to_datetime(df[first_col], format="%d.%m.%Y, %H:%M", errors='raise')
    except Exception as e:
        st.error(f"Zeitspalte konnte nicht geparst werden: {e}")
        st.stop()

    x_col = first_col

    # Numerische Spalten für Y-Achse ermitteln
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        st.error("Keine numerischen Spalten für die y-Achse gefunden.")
    else:
        y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)

        if y_cols:
            fig = px.line(df, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")
            st.plotly_chart(fig, use_container_width=True)
