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

    # Erstelle eine Kopie. Diese wird nicht mehr gefiltert, sondern bleibt vollständig.
    df_processed = df_original.copy()

    # --- Start der Logik zur Hervorhebung in der Sidebar ---
    st.sidebar.header("Zeitbereich hervorheben")
    st.sidebar.info("Wähle hier eine Zeitspanne aus, die im Diagramm farblich markiert werden soll. Es werden keine Daten entfernt.")

    # Der Benutzer wählt die Zeitspalte aus, die für die Hervorhebung massgebend ist.
    highlight_col = st.sidebar.selectbox(
        "Wähle die Zeitspalte für die Hervorhebung",
        options=[None] + df_original.columns.tolist()
    )

    highlight_start_time = None
    highlight_end_time = None

    if highlight_col:
        # Prüfen, ob die Spalte in ein Datum konvertiert werden kann, ohne die Originaldaten zu ändern.
        temp_time_series = pd.to_datetime(df_processed[highlight_col], errors='coerce')
        if not temp_time_series.notna().any():
            st.sidebar.error(f"Die Spalte '{highlight_col}' konnte nicht als Zeitstempel interpretiert werden.")
            highlight_col = None # Ungültige Spalte zurücksetzen
        else:
            # Zeitauswahl für die Hervorhebung
            highlight_start_time = st.sidebar.time_input("Startzeit der Hervorhebung", datetime.time(8, 0))
            highlight_end_time = st.sidebar.time_input("Endzeit der Hervorhebung", datetime.time(12, 0))

    # --- Ende der Hervorhebungs-Logik ---


    # Vorschau & Datentypen
    st.subheader("Vorschau der Daten")
    st.dataframe(df_processed.head(), use_container_width=True)
    st.caption("Ursprüngliche Datentypen:")
    st.write(df_original.dtypes)


    # --- Plot-Logik ---
    st.subheader("Diagramm")

    numeric_cols = df_processed.select_dtypes(include='number').columns.tolist()

    if not numeric_cols:
        st.error("Keine numerischen Spalten in den Daten gefunden.")
    else:
        y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)
        x_col = st.selectbox(
            "Wähle die Spalte für die Zeitachse (x-Achse)",
            options=df_processed.columns.tolist()
        )

        if y_cols and x_col:
            st.info(f"Für die Visualisierung wird die Spalte '{x_col}' als Zeitstempel behandelt.")

            df_plot = df_processed.copy()
            df_plot[x_col] = pd.to_datetime(df_plot[x_col], errors='coerce')
            df_plot.dropna(subset=[x_col] + y_cols, inplace=True)

            if not df_plot.empty:
                # Schritt 1: Erstelle das Diagramm mit ALLEN Daten
                fig = px.line(df_plot, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")

                # Schritt 2: Füge die Hervorhebung hinzu, falls ausgewählt
                if highlight_col and highlight_start_time and highlight_end_time:
                    if highlight_start_time < highlight_end_time:
                        # Finde alle einzigartigen Tage in den Daten
                        unique_dates = df_plot[x_col].dt.date.unique()

                        # Erstelle für jeden Tag einen markierten Bereich
                        for date in unique_dates:
                            start_dt = datetime.datetime.combine(date, highlight_start_time)
                            end_dt = datetime.datetime.combine(date, highlight_end_time)
                            
                            fig.add_vrect(
                                x0=start_dt,
                                x1=end_dt,
                                fillcolor="LightSalmon",
                                opacity=0.3,
                                layer="below", # Wichtig: Legt den Bereich hinter die Datenlinien
                                line_width=0,
                            )
                    else:
                        st.sidebar.warning("Die Startzeit für die Hervorhebung muss vor der Endzeit liegen.")

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nach der Datenbereinigung sind keine gültigen Daten zum Plotten vorhanden.")
