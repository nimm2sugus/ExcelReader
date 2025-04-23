import streamlit as st
import pandas as pd
import plotly.express as px

# Layout auf "wide" setzen
st.set_page_config(layout="wide")

st.title("Zeitreihen-Analyse Tool")

uploaded_file = st.file_uploader("Lade eine CSV- oder Excel-Datei hoch", type=["csv", "xlsx"])
if uploaded_file:
    # Datei laden
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    # Vorschau & Datentypen
    st.subheader("Vorschau der Daten")
    st.dataframe(df.head(), use_container_width=True)
    st.caption("Datentypen:")
    st.write(df.dtypes)

    # Zeitspalten erkennen
    time_candidates = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            time_candidates.append(col)

    # Auswahl für x-Achse (Zeit)
    if time_candidates:
        x_col = st.selectbox("Wähle die Zeitspalte (x-Achse)", time_candidates)
    else:
        x_col = None
        st.warning("Keine Zeitspalte erkannt. Die Datei wird ohne Zeitachse geplottet.")

    # Numerische Spalten erkennen (robust!)
    numeric_cols = []
    for col in df.columns:
        # Versuch Konvertierung
        numeric_series = pd.to_numeric(df[col], errors="coerce")
        if numeric_series.notna().sum() > 0:
            numeric_cols.append(col)

    # Zeitspalten rausfiltern aus den numerischen
    numeric_cols = [col for col in numeric_cols if col not in time_candidates]

    if not numeric_cols:
        st.error("Keine numerischen Spalten erkannt. Bitte überprüfe deine Daten.")
    else:
        y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)

        if y_cols:
            if x_col:
                fig = px.line(df, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")
            else:
                fig = px.line(df[y_cols], title="Diagramm ohne Zeitachse")
            st.plotly_chart(fig, use_container_width=True)
