import os
import time
import torch
import pandas as pd
import streamlit as st

import asyncio
import plotting
import requests
import regex


_ = """A Dashboard to Serenade William

Tab1: Our friendship
    - My love for you
    - A Picture of us
    - Reviews of Steffen as CTO and long time friend
    - ChatGPT conversation with William about Steffen. Responds only with poetry.

Tab2: Subnet ownership
    - Owner earnings trends (select topk netuids, emission vs earnings, time vs block)
    - Owner earnings all time (emission vs earnings, time vs block)

Tab3: Validator ownership
    - Validator earnings distribution (pie chart)
    - Weight distribution (heatmap)

Tab3: Mining ownership
    - TBD

Footer: If I can build this in an evening, imagine what we can build in a year. :train:
"""

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
import bittensor as bt


# Set app config
st.set_page_config(
    page_title='Synapse Labs',
    menu_items={
        'Report a bug': "https://github.com/steffencruz/join-me-william",
        'About': """
        This dashboard is part of my earnest attempt to serenade William into joining me in building Synapse Labs.
        """
    },
    layout = "centered"
    )

st.title('Synapse Labs')
# add vertical space
st.markdown('#')
st.markdown('#')


@st.cache_data()
def load_data():
    df = pd.read_csv('data/subnets/0/df.csv')
    df['timestamp'] = pd.to_datetime(df.timestamp)
    df.sort_values(by=['block','timestamp','netuid'], inplace=True)

    return df


st.cache_data()
def get_metagraph(netuid=0):
    try:
        return bt.metagraph(netuid)
    except:
        class FakeMetagraph:
            def __init__(self):
                self.block = torch.tensor(0)
                self.stake = torch.tensor([1,1,1,1,1])

        return FakeMetagraph()

def get_token_price():
    """Get tao price"""
    resp = requests.get('https://taostats.io')
    match = regex.search('Price.</label> \\$(?P<price>\\d+.\\d+)',resp.text).groupdict()
    price = float(match['price'])
    print(f'Live token price = USD${price:.2f}')
    return price

# Get source data
df = load_data()
blocks = df.block.unique()
last_block = df.block.max()

# tau symbol
tao = u"\u03C4"

metagraph = get_metagraph()
current_block = metagraph.block.item()

token_price = get_token_price()

df['owner_take_usd'] = df.owner_take * token_price


tlmcol1, tlmcol2, tlmcol3 = st.columns(3)
tlmcol1.metric(f'Token price: {tao}', f'${token_price:.2f}')
tlmcol2.metric(f'Current block: ', f'{current_block:,}')
tlmcol3.metric(f'Daily emission: (US$)', f'${7200*token_price:,.0f}')


# add vertical space
st.markdown('#')
st.markdown('#')

tab1, tab2, tab3, tab4 = st.tabs(["Owner", "Validator", "Miner", "Coda"])


with tab1:

    st.markdown('#')
    st.markdown('#')
    st.header('Subnet Ownership')
    st.success('**Ownership** *earns 18% of all subnet emissions*')

    st.markdown('#')
    st.markdown('#')
    st.markdown('#')

    st.subheader('Subnet Metrics')
    st.markdown('#')

    ncol1, ncol2 = st.columns([0.25, 0.75])
    netuid = ncol1.selectbox('Select a **subnet**', sorted(df.netuid.unique()), index=1)
    df_sn = df.loc[df.netuid==netuid]
    sn_emission = df_sn.Emission.values
    sn_owner_take = df_sn.owner_take.values
    st.markdown('#')

    ncol2.markdown(f'*Showing metrics for subnet* **{netuid}** *between* **{df_sn.timestamp.min().strftime("%d %b")}** *and* **{df_sn.timestamp.max().strftime("%d %b")}**')
    st.markdown('#')

    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric('Emission %', f'{sn_emission[-1]*100:.1f}', delta=f'{(sn_emission[-1]-sn_emission[-2])*100:.1f}')
    mcol2.metric(f'Total earnings ({tao})', f'{tao}{sn_owner_take.sum():,.2f}', delta=f'{tao}{sn_owner_take[-1]:,.2f}')
    mcol3.metric(f'Total earnings (US$)', f'{tao}{sn_owner_take.sum()*token_price:,.2f}', delta=f'{tao}{sn_owner_take[-1]*token_price:,.2f}')
    st.markdown('#')

    with st.expander(f'View **raw** data for subnet {netuid}'):
        st.dataframe(df_sn)

    st.markdown('#')
    st.markdown('#')
    st.markdown('#')

    st.subheader('Subnet Earnings')

    pcol1, pcol2, pcol3 = st.columns(3)

    x = pcol1.selectbox('**Time axis**', ['block','timestamp','day'], index=1)

    y_mapping = {
        'Emissions': 'Emission',
        'Earnings': 'owner_take',
        'Earnings (US$)': 'owner_take_usd',
    }

    y = pcol2.selectbox('**Y axis**', list(y_mapping.keys()), index=1)
    ntop = pcol3.slider('**Top Subnets**', min_value=1, max_value=32, value=5, key='sel_ntop')

    st.plotly_chart(
        plotting.plot_owner_emission_trends(df, x=x, y=y_mapping[y], label=y, color='netuid', ntop=ntop),
        use_container_width=True
    )

    st.plotly_chart(
        plotting.plot_owner_total_earnings(df, y=y_mapping[y], title=y, color='day'),
        use_container_width=True
    )


with tab2:

    st.markdown('#')
    st.markdown('#')
    st.header('Validator Revenue')
    st.success('**Validators** *share 42% of subnet emissions, based on stake. Validators earn 18% tax on all delegated stake.*')

    threshold = st.slider('Stake threshold', min_value=0, max_value=100_000, value=10_000, key='stake_threshold')
    st.plotly_chart(
        plotting.plot_validator_stake(pd.DataFrame({'stake':metagraph.stake}), threshold=threshold),
        use_container_width=True
    )
    
    scol1, scol2 = st.columns(2)
    user_stake = scol1.slider('Validator stake', min_value=0, max_value=100_000, value=10_000, key='user_stake')
    delegated_stake = scol2.slider('Delegated stake', min_value=0, max_value=1_000_000, value=100_000, key='delegated_stake')
    st.plotly_chart(
        plotting.plot_validator_earnings(pd.DataFrame({'delegated':metagraph.stake}), threshold=threshold, user_stake=user_stake, user_delegated=delegated_stake),
        use_container_width=True
    )    


with tab3:

    st.markdown('#')
    st.markdown('#')
    st.subheader('Mining Revenue')
    st.success('**Miners** *share 42% of subnet emissions, based on performance*')

    st.markdown('Coming soon!')


### Coda  ###
with tab4:

    st.markdown('#')
    st.markdown('#')
    st.header('Our **lifelong friendship**')
    # The way to add bold to st.text is to use **bold**.
    st.markdown("""
            We met in the :red[s]kies before we both flew the nest,

            then resumed our great vo:red[y]age in Pacific Northwest.

            We've bee:red[n] through the strangest and nicest of times,

            Including knighting e:red[a]ch other with the finest of wines.

            So much has ha:red[p]pened, so much has been said,

            and now here we are, galaxie:red[s] ahead.

            We got on the train and we're going full st:red[e]am,

            so let's build the future and make it a dream :heart:
            """)

    photo_choices = {
        'good': 'data/photos/good.jpg',
        'sultan': 'data/photos/sultan.jpg',
        'nice': 'data/photos/nice.jpg',
        'chess': 'data/photos/chess.jpg',
        'strange': 'data/photos/strange.jpg'
    }
    photo_choice = st.radio('Choose a time:', list(photo_choices.keys()), horizontal=True, index=0)

    # display image
    st.image(plotting.plot_photo(photo_choices[photo_choice]), use_column_width=True)

    if st.button('Join synapse labs..?', type='primary'):
        st.balloons()
        st.success('Nice time! :heart:')
