import streamlit as st
import plotly.express as px
from PIL import Image



@st.cache_data()
def plot_owner_total_earnings(df, y='owner_take', color='day', title=None):
    return px.bar(df, x='netuid', y=y, color=color, barmode='group',
            color_continuous_scale='BlueRed',
            title=f'Total {title or y} per Subnet',
            labels={'netuid': 'Subnet', 'owner_take': 'Owner Earning (TAO)', 'day': 'Day'},
            width=800, height=600, template='plotly_white')


@st.cache_data()
def plot_owner_emission_trends(df, x='timestamp', y='owner_take', label=None, color='netuid', ntop=32):

    top_netuids = df.groupby('netuid')['owner_take'].sum().sort_values(ascending=False).index[:ntop]

    return px.line(df.loc[df.netuid.isin(top_netuids)], x=x, y=y, color=color,
                   line_group='netuid',
                    title=f'{label or y} Trends for Top {ntop} Subnets',
                    labels={'netuid': 'Subnet', 'owner_take': 'Daily Owner Earnings (TAO)'},
                    width=800, height=600, template='plotly_white'
                    ).update_traces(opacity=0.7)

@st.cache_data()
def plot_validator_stake(stake, threshold=10000):
    return px.pie(stake[stake>threshold], values='stake', hole=0.5,
       title=f'Stake Distribution (Stake > {threshold:,} TAO)',
       width=800, height=600, template='plotly_white')

@st.cache_data()
def plot_photo(path):
    return Image.open(path)