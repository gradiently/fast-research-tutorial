import streamlit as st
from important.snowflake import read_sql
from glow.secrets import GLOW_SECRETS
import os
import matplotlib.pyplot as plt

os.environ["SNOWFLAKE_PASSWORD"] = GLOW_SECRETS["SNOWFLAKE_PASSWORD"]

st.title("How to use this app")


def make_sql(
    locale: str = "All",
    country: str = "All",
    limit: int = 10,
):
    """
    Core magic function
    """
    conditions = []
    if locale != "All":
        conditions.append(f"locale = '{locale}'")
    if country != "All":
        conditions.append(f"country = '{country}'")
    if len(conditions) > 0:
        where = "where " + " and ".join(conditions)
    else:
        where = ""
    return f"select event, count(1) as ct from business_events {where} group by event order by ct desc limit {limit};"


country_selector = st.selectbox(
    "Select a country",
    [
        "All",
        "US",
        "JP",
        "DE",
        "GB",
        "SG",
    ],
)
locale_selector = st.selectbox(
    "Select a locale",
    [
        "All",
        "en",
        "ja-JP",
        "zh-CN",
        "es-419",
        "de-DE",
        "ru-RU",
    ],
)
limit_number = st.slider("Limit", min_value=3, max_value=20, value=10)


if st.button("Show events"):
    events = read_sql(make_sql(locale=locale_selector, country=country_selector, limit=limit_number))
    st.table(events)

    fig, ax = plt.subplots()
    top_5_events = events.nlargest(5, "CT")
    other_events = events.drop(top_5_events.index)

    labels = top_5_events["EVENT"].tolist() + ["Others"]
    sizes = top_5_events["CT"].tolist() + [other_events["CT"].sum()]

    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")

    st.pyplot(fig)


# streamlit run streamlit_example.py  --server.headless true
