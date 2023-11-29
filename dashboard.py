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
    page_title='Validator Dashboard',
    menu_items={
        'Report a bug': "https://github.com/opentensor/dashboards/issues",
        'About': """
        This dashboard is part of the OpenTensor project. \n
        """
    },
    layout = "centered"
    )

st.title('Synapse Labs')
# add vertical space
st.markdown('#')
st.markdown('#')



df = pd.read_csv('data/subnets/0/df.csv')
df.sort_values(by=['block','timestamp','netuid'], inplace=True)
blocks = df.block.unique()
last_block = df.block.max()

# tau symbol
tao = u"\u03C4"

st.cache_data()
def get_metagraph(netuid=0):
    try:
        return bt.metagraph(netuid)
    except:
        class FakeMetagraph:
            def __init__(self):
                self.block = torch.tensor(0)

        return FakeMetagraph()

metagraph = get_metagraph()
current_block = metagraph.block.item()

# with st.sidebar:
#     st.title('Options')
#     st.markdown('#')

#     netuid = st.selectbox('Netuid', [1,11], index=0)

#     st.markdown('#')

#     c1, c2 = st.columns([0.7,0.3])
#     staleness =  current_block - last_block
#     msg = c1.warning(f'Out of date ({staleness})') if staleness >= 100 else c1.info('Up to date')
#     if c2.button('Update', type='primary'):
#         msg.info('Downloading')
#         return_code = run_subprocess()
#         if return_code == 0:
#             msg.success('Up to date')
#             time.sleep(1)
#             msg.empty()
#         else:
#             msg.error('Error')

#     st.markdown('#')


#     st.markdown('#')
#     st.markdown('#')
#     # horizontal line
#     st.markdown('<hr>', unsafe_allow_html=True)

#     r1c1, r1c2 = st.columns(2)
#     x = r1c1.selectbox('**Time axis**', ['block','timestamp'], index=0)
#     color = r1c2.selectbox('**Color**', ['coldkey','hotkey','ip'], index=0)
#     r2c1, r2c2 = st.columns(2)
#     ntop = r2c1.slider('**Sample top**', min_value=1, max_value=50, value=10, key='sel_ntop')
#     opacity = r2c2.slider('**Opacity**', min_value=0., max_value=1., value=0.5, key='opacity')
#     r3c1, r3c2 = st.columns(2)
#     smooth = r3c1.slider('Smoothing', min_value=1, max_value=100, value=1, key='sel_churn_smooth')
#     smooth_agg = r3c2.radio('Smooth Aggregation', ['mean','std','max','min','sum'], horizontal=True, index=0)

def get_token_price():
    """Get tao price"""
    resp = requests.get('https://taostats.io')
    match = regex.search('Price.</label> \\$(?P<price>\\d+.\\d+)',resp.text).groupdict()
    price = float(match['price'])
    print(f'Live token price = USD${price:.2f}')
    return price

token_price = get_token_price()

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

    st.subheader('Subnet Metrics')

    ncol1, *_ = st.columns(3)
    netuid = ncol1.selectbox('Select a **subnet**', sorted(df.netuid.unique()), index=1)
    df_sn = df.loc[df.netuid==netuid]
    sn_emission = df_sn.Emission.values
    sn_owner_take = df_sn.owner_take.values

    st.info(f'*Showing metrics for subnet* **{netuid}**')

    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric('Emission %', f'{sn_emission[-1]*100:.1f}', delta=f'{(sn_emission[-1]-sn_emission[-2])*100:.1f}')
    mcol2.metric(f'Total earnings ({tao})', f'{tao}{sn_owner_take.sum():.2f}', delta=f'{tao}{sn_owner_take[-1]-sn_owner_take[-2]:.2f}')
    mcol3.metric(f'Total earnings (US$)', f'{tao}{sn_owner_take.sum()*token_price:,.2f}', delta=f'{tao}{(sn_owner_take[-1]-sn_owner_take[-2])*token_price:,.2f}')

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
        'Earnings': 'owner_take'
    }

    y = pcol2.selectbox('**Y axis**', ['Earnings','Emission'], index=0)
    ntop = pcol3.slider('**Top Subnets**', min_value=1, max_value=32, value=32, key='sel_ntop')

    st.plotly_chart(
        plotting.plot_owner_emission_trends(df, x=x, y=y_mapping[y], color='netuid', ntop=ntop),
        use_container_width=True
    )

    st.plotly_chart(
        plotting.plot_owner_total_earnings(df, y=y_mapping[y], color='day'),
        use_container_width=True
    )


with tab2:

    st.markdown('#')
    st.markdown('#')
    st.header('Validator Revenue')
    st.success('**Validators** *earn 18% of nominator dividends*')
    
    # mcol1, mcol2, mcol3 = st.columns(3)
    # mcol2.metric('Emission %', f'{sn1_today.emission*100:.1f}', delta=f'{(sn1_today.emission-sn1_yesterday.emission)*100:.1f}')
    # mcol3.metric('Earnings', f'{tao}{sn1.earnings.sum():.3f}', delta=f'{tao}{sn1_today.earnings-sn1_yesterday.earnings:.3f}')

    # st.plotly_chart(
    #     plotting.plot_animation(validators, x=vac_x, y=vac_y, color=vac_color, size=vac_size, opacity=opacity),
    #     use_container_width=True
    # )
    # validator_choice = st.radio('Select:', validator_choices, horizontal=True, index=0)
    # with st.expander(f'Show **{validator_choice}** trends for top **{ntop}** validators'):

    #     st.plotly_chart(
    #         plotting.plot_trace(validators, time_col=x,col=validator_choice, ntop=ntop, smooth=smooth, smooth_agg=smooth_agg, opacity=opacity),
    #         use_container_width=True
    #     )

    # count_col = st.radio('Count', cabal_choices, index=0, horizontal=True, key='sel_validator_count')
    # with st.expander(f'Show **{count_col}** trends for top **{ntop}** validators'):

    #     st.plotly_chart(
    #         plotting.plot_cabals(validators, time_col=x, count_col=count_col, sel_col=color, ntop=ntop, smooth=smooth, smooth_agg=smooth_agg, opacity=opacity),
    #         use_container_width=True
    #     )

with tab3:

    st.markdown('#')
    st.markdown('#')
    st.subheader('Mining Revenue')
    st.info('**Block introspection** *shows the complete metagraph of a block*')

    # selected_block = st.selectbox('**Block**', reversed(df_sel.block.unique()), index=0)

    # st.dataframe(df_sel.loc[df_sel['block']==selected_block])



### Coda  ###
with tab4:

    st.markdown('#')
    st.markdown('#')
    st.subheader('Introduction')
    st.info('Our **lifelong friendship**')
    st.text("""
            We met the **s**kies before we both flew the nest,
            then resumed our great journe**y** in Pacific Northwest.
            We've bee**n** through the strangest and nicest of times,
            Including knighting e**a**ch other with the finest of wines.
            So much has ha**p**pened, so much has been said,
            and now here we are, galaxies ahead.
            We got on the train and we're going full **s**team,
            so let's build the future and make it a dr**e**am :heart:
            """)

    photo_choices = {
        'good': 'data/photos/good.jpg',
        'sultan': 'data/photos/sultan.jpg',
        'nice': 'data/photos/nice.jpg',
        'chess': 'data/photos/chess.jpg',
        'strange': 'data/photos/strange.jpeg'
    }
    photo_choice = st.radio('Times', ['good','bad','nice','chess','strange'], horizontal=True, index=0)

    # display image
    st.image(photo_choice[photo_choice], use_column_width=True)

    if st.button('Join..?', type='primary'):
        st.balloons()
        st.success('Nice time! :heart:')
