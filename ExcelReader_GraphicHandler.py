import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

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

    # --- Start der neuen Filter-Logik in der Sidebar ---
    st.sidebar.header("Filteroptionen")

    # Zeitspalten erkennen
    time_candidates = []
    for col in df.columns:
        # Versuche, die Spalte in ein Datumsformat zu konvertieren
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                time_candidates.append(col)
        except Exception:
            continue

    # Wenn Zeitspalten gefunden wurden, zeige den Zeitfilter an
    if time_candidates:
        x_col_sidebar = st.sidebar.selectbox(
            "Wähle die Zeitspalte für den Filter",
            time_candidates,
            key="sidebar_time_col_selector" # Eindeutiger Schlüssel
        )

        # Zeitauswahl für den Filter
        start_time = st.sidebar.time_input("Startzeit", datetime.time(0, 0))
        end_time = st.sidebar.time_input("Endzeit", datetime.time(23, 59))

        # Filtere den DataFrame basierend auf der ausgewählten Zeit
        if start_time < end_time:
            # Stelle sicher, dass die Zeitspalte ein datetime-Objekt ist
            df[x_col_sidebar] = pd.to_datetime(df[x_col_sidebar])
            # Filtere basierend auf der Uhrzeit
            df = df[df[x_col_sidebar].dt.time.between(start_time, end_time)]
            st.success(f"Daten gefiltert für den Zeitraum zwischen {start_time.strftime('%H:%M')} und {end_time.strftime('%H:%M')}.")
        else:
            st.sidebar.warning("Die Startzeit muss vor der Endzeit liegen.")

    else:
        st.sidebar.info("Keine Zeitspalte für den Filter gefunden.")

    # --- Ende der neuen Filter-Logik ---


    # Vorschau & Datentypen (zeigt gefilterte Daten an, falls Filter aktiv)
    st.subheader("Vorschau der Daten")
    st.dataframe(df.head(), use_container_width=True)
    st.caption("Datentypen:")
    st.write(df.dtypes)


    # Auswahl für x-Achse (Zeit) im Hauptbereich
    # Die Kandidatenliste wird hier neu erstellt, falls Spalten konvertiert wurden
    main_time_candidates = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]

    if main_time_candidates:
        x_col_main = st.selectbox("Wähle die Zeitspalte (x-Achse)", main_time_candidates, key="main_time_col_selector")
    else:
        x_col_main = None
        st.warning("Keine Zeitspalte erkannt. Die Datei wird ohne Zeitachse geplottet.")

    # Numerische Spalten erkennen (robust!)
    numeric_cols = []
    for col in df.columns:
        # Versuch Konvertierung
        numeric_series = pd.to_numeric(df[col], errors="coerce")
        if numeric_series.notna().sum() > 0:
            numeric_cols.append(col)

    # Zeitspalten aus den numerischen Spalten entfernen
    numeric_cols = [col for col in numeric_cols if col not in main_time_candidates]

    if not numeric_cols:
        st.error("Keine numerischen Spalten erkannt. Bitte überprüfe deine Daten.")
    else:
        y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)

        if y_cols:
            st.subheader("Diagramm")
            if x_col_main:
                # Nutze den (potenziell gefilterten) DataFrame für das Diagramm
                fig = px.line(df, x=x_col_main, y=y_cols, title="Zeitreihen-Diagramm")
            else:
                fig = px.line(df[y_cols], title="Diagramm ohne Zeitachse")
            st.plotly_chart(fig, use_container_width=True)
