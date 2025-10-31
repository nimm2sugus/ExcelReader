import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Layout auf "wide" setzen
st.set_page_config(layout="wide")

st.title("Zeitreihen-Analyse Tool")

uploaded_file = st.file_uploader("Lade eine CSV- oder Excel-Datei hoch", type=["csv", "xlsx"])
if uploaded_file:
    # Schritt 1: Datei in einen "originalen" DataFrame laden
    if uploaded_file.name.endswith(".csv"):
        df_original = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df_original = pd.read_excel(uploaded_file)

    # Erstelle eine Kopie für alle Bearbeitungen (Filtern, Plotten etc.)
    df_processed = df_original.copy()


    # --- Start der neuen, sicheren Filter-Logik in der Sidebar ---
    st.sidebar.header("Filteroptionen")

    # Der Benutzer wählt die Zeitspalte aus ALLEN Spalten aus.
    # Eine 'None'-Option erlaubt das Deaktivieren des Filters.
    filter_col = st.sidebar.selectbox(
        "Wähle die Zeitspalte für den Filter",
        options=[None] + df_original.columns.tolist()
    )

    if filter_col:
        # Schritt 2: Wandle NUR die ausgewählte Spalte temporär um.
        # Dies geschieht in einer separaten Pandas-Serie und verändert NICHT df_processed.
        temp_time_series = pd.to_datetime(df_processed[filter_col], errors='coerce')

        # Prüfen, ob die Konvertierung mindestens einen gültigen Wert ergeben hat
        if not temp_time_series.notna().any():
            st.sidebar.error(f"Die Spalte '{filter_col}' konnte nicht als Zeitstempel interpretiert werden. Bitte wähle eine andere Spalte.")
        else:
            # Wenn erfolgreich, zeige die Zeitauswahl an
            start_time = st.sidebar.time_input("Startzeit", datetime.time(0, 0))
            end_time = st.sidebar.time_input("Endzeit", datetime.time(23, 59))

            if start_time < end_time:
                # Erstelle eine Maske basierend auf der temporären Zeit-Serie
                mask = temp_time_series.dt.time.between(start_time, end_time)
                # Wende die Maske auf den Bearbeitungs-DataFrame an
                df_processed = df_processed[mask]
                st.sidebar.success(f"Daten gefiltert für den Zeitraum zwischen {start_time.strftime('%H:%M')} und {end_time.strftime('%H:%M')}.")
            else:
                st.sidebar.warning("Die Startzeit muss vor der Endzeit liegen.")

    # --- Ende der Filter-Logik ---


    # Vorschau & Datentypen
    st.subheader("Vorschau der Daten")
    st.caption("Die hier angezeigten Daten sind gefiltert, falls ein Filter in der Seitenleiste aktiv ist.")
    st.dataframe(df_processed.head(), use_container_width=True)

    # Zeige die Datentypen der *ursprünglichen* Datei, um Klarheit zu schaffen
    st.caption("Ursprüngliche Datentypen der hochgeladenen Datei:")
    st.write(df_original.dtypes)


    # --- Plot-Logik ---
    st.subheader("Diagramm erstellen")

    # Numerische Spalten aus dem (potenziell gefilterten) DataFrame erkennen
    numeric_cols = df_processed.select_dtypes(include='number').columns.tolist()

    if not numeric_cols:
        st.error("Keine numerischen Spalten in den (gefilterten) Daten gefunden. Bitte überprüfe deine Daten.")
    else:
        # Auswahl der Y-Achsen
        y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)

        # Auswahl der X-Achse
        x_col = st.selectbox(
            "Wähle die Spalte für die Zeitachse (x-Achse)",
            options=df_processed.columns.tolist()
        )

        if y_cols and x_col:
            st.info(f"Für die Visualisierung wird die Spalte '{x_col}' als Zeitstempel behandelt.")

            # Erstelle eine finale Kopie für den Plot, um die Typen sicher zu konvertieren
            df_plot = df_processed.copy()
            df_plot[x_col] = pd.to_datetime(df_plot[x_col], errors='coerce')

            # Entferne Zeilen, bei denen die X- oder Y-Werte nicht gültig sind
            df_plot.dropna(subset=[x_col] + y_cols, inplace=True)

            if not df_plot.empty:
                fig = px.line(df_plot, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nach der Datenbereinigung sind keine gültigen Daten zum Plotten vorhanden.")
