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

    # Info anzeigen
    st.subheader("Vorschau der Daten")
    st.dataframe(df.head())
    st.caption("Datentypen:")
    st.write(df.dtypes)

    # Erkennung der Zeitspalten, wenn vorhanden
    time_candidates = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            time_candidates.append(col)
        else:
            try:
                # Versuche, die Spalte als Datum zu interpretieren
                parsed = pd.to_datetime(df[col], errors='raise')
                df[col] = parsed
                time_candidates.append(col)
            except:
                continue

    # Wenn keine Zeitspalten gefunden wurden
    if not time_candidates:
        st.warning("Keine Zeitspalte erkannt. Die Datei wird ohne Zeitumwandlung weiterverarbeitet.")
        time_candidates = []  # Keine Zeitspalte zur Auswahl

    # Auswahl der Zeitspalte (nur, wenn Zeitspalten vorhanden sind)
    if time_candidates:
        x_col = st.selectbox("Wähle die Zeitspalte (x-Achse)", time_candidates)
    else:
        x_col = None

    # Nur numerische Spalten für y-Achse
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

    if not numeric_cols:
        st.warning("Keine numerischen Spalten erkannt. Überprüfe die Datentypen oben.")
    else:
        y_cols = st.multiselect("Wähle eine oder mehrere Spalten für die y-Achse", numeric_cols)

        if y_cols:
            # Erstelle das Plot mit der ausgewählten Zeitspalte (x) und den numerischen Spalten (y)
            if x_col:  # Wenn eine Zeitspalte ausgewählt wurde
                fig = px.line(df, x=x_col, y=y_cols, title="Zeitreihen-Diagramm")
            else:  # Wenn keine Zeitspalte vorhanden ist, erstelle einfach ein normales Plot
                fig = px.line(df, y=y_cols, title="Diagramm ohne Zeitachse")

            st.plotly_chart(fig, use_container_width=True)
