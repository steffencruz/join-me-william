import streamlit as st
import plotly.express as px
from PIL import Image
import pandas as pd


labels={'netuid': 'Subnet', 'Emission':'Emission (%)', 'owner_take': 'Daily Owner Earnings (TAO)','owner_take_usd': 'Daily Owner Earnings ($USD)'}

@st.cache_data()
def plot_owner_total_earnings(df, y='owner_take', color='day', title=None):
    return px.bar(df, x='netuid', y=y, 
                  color=color, barmode='group',opacity=0.7,
                  hover_data=['timestamp','block','owner_take','owner_take_usd','Emission'],
                    color_continuous_scale='BlueRed',
                    title=f'Total {title or y} per Subnet',
                    labels=labels,
                    width=800, height=600, template='plotly_white')


@st.cache_data()
def plot_owner_emission_trends(df, x='timestamp', y='owner_take', label=None, color='netuid', ntop=32):

    top_netuids = df.groupby('netuid')[y].sum().sort_values(ascending=False).index[:ntop]

    return px.line(df.loc[df.netuid.isin(top_netuids)], x=x, y=y, color=color,
                   line_group='netuid', hover_data=['timestamp','block','owner_take','owner_take_usd','Emission'],
                    title=f'{label or y} Trends for Top {ntop} Subnets',
                    labels=labels,
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


@st.cache_data()
def plot_validator_earnings(df, threshold=10000, user_stake=10_000, user_delegated=100_000):
    # TODO: Calculate based on netuids that validator is part of
    # TODO: Estimate operational costs

    df['stake'] = 0.01*df['delegated']
    df['delegated'] = 0.99*df['delegated']
    df['total_stake'] = df['stake'] + df['delegated']
    df['Id'] = 'Metagraph'
    
    df_user = pd.DataFrame({'stake':[user_stake],'delegated':[user_delegated], 'total_stake':[user_stake+user_delegated], 'Id':['User']})
    df = pd.concat([df, df_user], ignore_index=True)
    df['daily dividends'] = (df['stake']+df['delegated']*0.18)/1000
    
    print(df)

    fig = px.scatter(df.loc[df.total_stake>threshold], x='total_stake', y='daily dividends',
                     color='Id', size='stake', hover_name='Id', hover_data={'stake':':.2f', 'delegated':':.2f', 'total_stake':':.2f', 'daily dividends':':.2f'},
                labels={'total_stake':'Total stake', 'stake':'Validator stake', 'delegated':'Delegated stake','daily dividends':'Daily dividends (TAO)'},
                title=f'Validator Expected Earnings (Stake > {threshold:,} TAO)',
                width=800, height=600, template='plotly_white'
            ).update_traces(opacity=0.6)

    for x in [1,2,5,10,20]:
        fig.add_hline(y=0.18*7200*0.01*x, annotation_text=f'SN Owner @ {x}%', line_dash='dot', line_width=1)

    return fig