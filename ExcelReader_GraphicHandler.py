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


    # --- Start der Filter-Logik in der Sidebar ---
    st.sidebar.header("Filteroptionen")

    filter_col = st.sidebar.selectbox(
        "Wähle die Zeitspalte für den Daten-Filter",
        options=[None] + df_original.columns.tolist()
    )

    if filter_col:
        temp_time_series = pd.to_datetime(df_processed[filter_col], errors='coerce')

        if not temp_time_series.notna().any():
            st.sidebar.error(f"Die Spalte '{filter_col}' konnte nicht als Zeitstempel interpretiert werden.")
        else:
            start_time = st.sidebar.time_input("Startzeit für Daten", datetime.time(0, 0))
            end_time = st.sidebar.time_input("Endzeit für Daten", datetime.time(23, 59))

            if start_time < end_time:
                mask = temp_time_series.dt.time.between(start_time, end_time)
                df_processed = df_processed[mask]
                st.sidebar.success(f"Daten gefiltert für den Zeitraum zwischen {start_time.strftime('%H:%M')} und {end_time.strftime('%H:%M')}.")
            else:
                st.sidebar.warning("Die Startzeit muss vor der Endzeit liegen.")

    # --- Ende der Filter-Logik ---


    # Vorschau & Datentypen
    st.subheader("Vorschau der Daten")
    st.caption("Die hier angezeigten Daten sind gefiltert, falls ein Filter in der Seitenleiste aktiv ist.")
    st.dataframe(df_processed.head(), use_container_width=True)
    st.caption("Ursprüngliche Datentypen:")
    st.write(df_original.dtypes)


    # --- Plot-Logik ---
    st.subheader("Diagramm erstellen")

    numeric_cols = df_processed.select_dtypes(include='number').columns.tolist()

    if not numeric_cols:
        st.error("Keine numerischen Spalten in den (gefilterten) Daten gefunden.")
    else:
        y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)
        x_col = st.selectbox(
            "Wähle die Spalte für die Zeitachse (x-Achse)",
            options=df_processed.columns.tolist()
        )

        # --- Start der NEUEN Achsen-Einstellungen ---
        st.subheader("Achsen-Einstellungen")
        st.caption("Lege den initialen sichtbaren Zeitbereich für die x-Achse fest.")
        
        col1, col2 = st.columns(2)
        with col1:
            axis_start_time = st.time_input("Startzeit für Achse", datetime.time(0, 0))
        with col2:
            axis_end_time = st.time_input("Endzeit für Achse", datetime.time(23, 59))
        # --- Ende der NEUEN Achsen-Einstellungen ---


        if y_cols and x_col:
            st.info(f"Für die Visualisierung wird die Spalte '{x_col}' als Zeitstempel behandelt.")

            df_plot = df_processed.copy()
            df_plot[x_col] = pd.to_datetime(df_plot[x_col], errors='coerce')
            df_plot.dropna(subset=[x_col] + y_cols, inplace=True)

            if not df_plot.empty:
                fig = px.line(df_plot, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")

                # --- Start der NEUEN Logik zur Anpassung der Achse ---
                if axis_start_time < axis_end_time:
                    # Nimm das Datum des ersten Datenpunktes als Basis für den Zoom
                    start_date = df_plot[x_col].min().date()
                    
                    # Erstelle die vollen datetime-Objekte für den sichtbaren Bereich
                    zoom_start = datetime.datetime.combine(start_date, axis_start_time)
                    zoom_end = datetime.datetime.combine(start_date, axis_end_time)

                    # Wende den initialen Zoom auf die x-Achse an
                    fig.update_xaxes(range=[zoom_start, zoom_end])
                else:
                    st.warning("Die Startzeit für die Achse muss vor der Endzeit liegen, um den Zoom anzuwenden.")
                # --- Ende der NEUEN Logik ---

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nach der Datenbereinigung sind keine gültigen Daten zum Plotten vorhanden.")
