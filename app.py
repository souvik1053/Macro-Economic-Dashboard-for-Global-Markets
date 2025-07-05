import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load & clean data
df = pd.read_csv("world_bank_data_2025.csv")
df.columns = df.columns.str.strip()

# List of indicators
indicators = [
    "Inflation (CPI %)",
    "GDP (Current USD)",
    "GDP per Capita (Current USD)",
    "Unemployment Rate (%)",
    "Interest Rate (Real, %)",
    "Inflation (GDP Deflator, %)",
    "GDP Growth (% Annual)",
    "Current Account Balance (% GDP)",
    "Government Expense (% of GDP)",
    "Government Revenue (% of GDP)",
    "Tax Revenue (% of GDP)",
    "Gross National Income (USD)",
    "Public Debt (% of GDP)"
]

# Sidebar Controls
st.sidebar.title("🌍 Macro Dashboard")
section = st.sidebar.radio("Select Analysis Section", [
    "Compare Countries", "Correlation Heatmap", "Scatter Plot",
])

countries = sorted(df['country_name'].unique())
country1 = st.sidebar.selectbox("Select Country 1", countries, index=0)
country2 = st.sidebar.selectbox("Select Country 2", countries, index=1)

# === Section 1: Country Comparison ===
if section == "Compare Countries":
    st.title("📈 International Macroeconomic Comparison")
    selected_indicators = st.sidebar.multiselect(
        "Select indicators to compare",
        indicators,
        default=["GDP (Current USD)", "Inflation (CPI %)", "Unemployment Rate (%)"]
    )
    for indicator in selected_indicators:
        st.subheader(f"{indicator}")
        fig = px.line(
            df[df["country_name"].isin([country1, country2])],
            x="year", y=indicator, color="country_name",
            title=f"{indicator} – {country1} vs {country2}"
        )
        st.plotly_chart(fig)

        # Auto Insights
        recent_year = df["year"].max()
        latest1 = df[(df["country_name"] == country1) & (df["year"] == recent_year)][indicator].values
        latest2 = df[(df["country_name"] == country2) & (df["year"] == recent_year)][indicator].values

        if latest1.size > 0 and latest2.size > 0:
            diff = round(latest1[0] - latest2[0], 2)
            if diff > 0:
                st.success(f"In {recent_year}, **{country1}** had a higher {indicator} by {diff}")
            elif diff < 0:
                st.error(f"In {recent_year}, **{country2}** had a higher {indicator} by {abs(diff)}")
            else:
                st.info(f"In {recent_year}, both countries had the same {indicator}.")

    with st.expander("📊 Show Raw Data Table"):
        st.dataframe(df[df["country_name"].isin([country1, country2])][["year", "country_name"] + selected_indicators])

# === Section 2: Correlation Heatmap ===
elif section == "Correlation Heatmap":
    st.title(f"📊 Correlation Heatmap – {country1}")
    country_df = df[df["country_name"] == country1].drop(columns=["country_name", "year"])
    corr = country_df.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig)

# === Section 3: Scatter Plot ===
elif section == "Scatter Plot":
    st.title(f"📌 Scatter Plot – {country1}")
    x_indicator = st.selectbox("X-axis Indicator", indicators, index=0)
    y_indicator = st.selectbox("Y-axis Indicator", indicators, index=1)

    scatter_df = df[df["country_name"] == country1].copy()

    # Drop rows with NaNs in required columns
    scatter_df = scatter_df[[x_indicator, y_indicator, "GDP (Current USD)", "year"]].dropna()

    if scatter_df.empty:
        st.warning("⚠️ Not enough data available for this combination.")
    else:
        fig2 = px.scatter(
            scatter_df,
            x=x_indicator,
            y=y_indicator,
            size="GDP (Current USD)",
            color="year",
            hover_name="year",
            title=f"{x_indicator} vs {y_indicator} ({country1})"
        )
        st.plotly_chart(fig2)