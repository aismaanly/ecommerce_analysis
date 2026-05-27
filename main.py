import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import plotly.express as px
import streamlit as st
import urllib
from function import DataAnalyzer, BrazilMapPlotter

# Custom orange color scale — avoids near-white so colors stay visible on cream background
ORANGE_SCALE = ["#FFCC80", "#FB8C00", "#E65100", "#7B2D00"]

st.set_page_config(
    page_title="E-Commerce Public Data Analysis",
    page_icon="https://raw.githubusercontent.com/aismaanly/ecommerce_analysis/main/assets/icon.png",
    layout="wide"
)

sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("https://raw.githubusercontent.com/aismaanly/ecommerce_analysis/main/dashboard/df.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('https://raw.githubusercontent.com/aismaanly/ecommerce_analysis/main/dashboard/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Adding a logo
    st.image("https://raw.githubusercontent.com/aismaanly/ecommerce_analysis/main/assets/logo.png", width=280)

    # Data range
    st.divider()
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("E-Commerce Public Data Analysis 🛒")
st.write("**This is a dashboard for analyzing E-Commerce public data.**")

# ── Top-level Metrics ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.metric("Total Order", value=f'{total_order:,}')

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    st.metric("Total Revenue", value=f'{total_revenue:,.2f}')

with col3:
    avg_spend = sum_spend_df["total_spend"].mean()
    st.metric("Average Spend", value=f'{avg_spend:,.2f}')

st.divider()

# ── Daily Orders Delivered ───────────────────────────────────────────────────
st.subheader("Daily Orders Delivered")
st.divider()

fig = px.line(
    daily_orders_df,
    x="order_approved_at",
    y="order_count",
    markers=True,
    title="Count of Daily Orders",
    labels={"order_approved_at": "Date", "order_count": "Order Count"},
    color_discrete_sequence=["#FB8C00"]
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── Customer Spend Money ─────────────────────────────────────────────────────
st.subheader("Customer Spend Money")
st.divider()

fig = px.line(
    sum_spend_df,
    x="order_approved_at",
    y="total_spend",
    markers=True,
    title="Customer Spend Over Time",
    labels={"order_approved_at": "Date", "total_spend": "Total Spend"},
    color_discrete_sequence=["#FB8C00"]
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── Order Items ──────────────────────────────────────────────────────────────
st.subheader("Order Items")
st.divider()

col1, col2 = st.columns(2)
with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.metric("Total Items", value=f'{total_items:,}')
with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.metric("Average Items", value=f'{avg_items:,.2f}')

col1, col2 = st.columns(2)

with col1:
    top5 = sum_order_items_df.head(5)
    fig = px.bar(
        top5,
        x="product_count",
        y="product_category_name_english",
        orientation="h",
        title="Most Sold Products",
        labels={"product_count": "Number of Sales", "product_category_name_english": ""},
        color="product_count",
        color_continuous_scale=ORANGE_SCALE
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    bot5 = sum_order_items_df.sort_values(by="product_count", ascending=True).head(5)
    fig = px.bar(
        bot5,
        x="product_count",
        y="product_category_name_english",
        orientation="h",
        title="Fewest Products Sold",
        labels={"product_count": "Number of Sales", "product_category_name_english": ""},
        color="product_count",
        color_continuous_scale=ORANGE_SCALE
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Review Score ─────────────────────────────────────────────────────────────
st.subheader("Review Score")
st.divider()

col1, col2 = st.columns(2)
with col1:
    avg_review_score = review_score.mean()
    st.metric("Average Review Score", value=f'{avg_review_score:.2f}')
with col2:
    most_common_review_score = review_score.value_counts().idxmax()
    st.metric("Most Common Review Score", value=f'{most_common_review_score}')

review_df = review_score.reset_index()
review_df.columns = ["review_score", "count"]

fig = px.bar(
    review_df,
    x="review_score",
    y="count",
    title="Customer Review Scores for Service",
    labels={"review_score": "Rating", "count": "Count"},
    color="count",
    color_continuous_scale=ORANGE_SCALE,
    text="count"
)
fig.update_traces(textposition="outside")
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
    xaxis=dict(type="category")
)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── Customer Demographic ─────────────────────────────────────────────────────
st.subheader("Customer Demographic")
st.divider()

tab1, tab2 = st.tabs(["State", "Geolocation"])

with tab1:
    most_common_state_val = state.customer_state.value_counts().index[0]
    st.metric("Most Common State", value=most_common_state_val)

    state_counts = state.customer_state.value_counts().reset_index()
    state_counts.columns = ["customer_state", "customer_count"]

    fig = px.bar(
        state_counts,
        x="customer_state",
        y="customer_count",
        title="Number of Customers from State",
        labels={"customer_state": "State", "customer_count": "Number of Customers"},
        color="customer_count",
        color_continuous_scale=ORANGE_SCALE
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    map_plot.plot()

    with st.expander("See Explanation"):
        st.write('According to the graph that has been created, there are more customers in the southeast and south. Other information, there are more customers in cities that are capitals (São Paulo, Rio de Janeiro, Porto Alegre, and others).')

st.divider()
st.caption('Copyright (C) Aisma Nurlaili 2024')