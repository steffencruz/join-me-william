import streamlit as st
import plotly.express as px

@st.cache_data()
def plot_owner_total_earnings(df, y='owner_take', color='day'):
    return px.bar(df, x='netuid', y=y, color=color, barmode='group',
            color_continuous_scale='BlueRed',
            title='Total Earnings per Subnet',
            labels={'netuid': 'Subnet', 'owner_take': 'Owner Earning (TAO)', 'day': 'Day'},
            width=800, height=600, template='plotly_white')


@st.cache_data()
def plot_owner_emission_trends(df, x='timestamp', y='owner_take', color='netuid', ntop=32):

    top_netuids = df.groupby('netuid')['owner_take'].sum().sort_values(ascending=False).index[:ntop]

    return px.line(df.loc[df.netuid.isin(top_netuids)], x=x, y=y, color=color,
                   line_group='netuid',
                    title=f'Earnings Trends for Top {ntop} Subnets',
                    labels={'netuid': 'Subnet', 'owner_take': 'Daily Owner Earnings (TAO)'},
                    width=800, height=600, template='plotly_white'
                    ).update_traces(opacity=0.7)
