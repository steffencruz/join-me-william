import os
import time
import pandas as pd
import streamlit as st

import asyncio
import plotting

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

metagraph = bt.metagraph(0)
current_block = metagraph.block.item()

df = pd.read_csv('data/subnets/0/df.csv')
blocks = df.block.unique()

last_block = df.block.max()

sn1 = df.loc[df.netuid==1]
today = df.loc[df.block == last_block].iloc[0]
sn1_today = today.loc[today.netuid==1]

yesterday = df.loc[df.block == last_block-7200].iloc[0]
sn1_yesterday = yesterday.loc[yesterday.netuid==1]

# tau symbol
tao = u"\u03C4"




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


# add vertical space
st.markdown('#')
st.markdown('#')

tab1, tab2, tab3, tab4 = st.tabs(["Owner", "Validator", "Miner", "Coda"])


with tab1:

    st.markdown('#')
    st.markdown('#')
    st.subheader('Subnet Ownership')
    st.info('**Ownership** *earns 18% of all subnet emissions*')

    st.markdown('#')

    mcol1, mcol2, mcol3 = st.columns(3)
    mcol2.metric('Emission %', f'{sn1_today.emission*100:.1f}', delta=f'{(sn1_today.emission-sn1_yesterday.emission)*100:.1f}')
    mcol3.metric('Earnings', f'{tao}{sn1.earnings.sum():.3f}', delta=f'{tao}{sn1_today.earnings-sn1_yesterday.earnings:.3f}')

    st.markdown('#')
    
    st.plotly_chart(
        plotting.plot_owner_total_earnings(df, y='owner_take', color='day'),
        use_container_width=True
    )

    ntop = st.slider('**Top Subnets**', min_value=1, max_value=32, value=32, key='sel_ntop')
    x = st.selectbox('**Time axis**', ['block','timestamp'], index=0)
    with st.expander(f'Show **emission** trends for top **{ntop}** subnets'):

        st.plotly_chart(
            plotting.plot_owner_emission_trends(df, time_col=x, y='emission', color='netuid', ntop=ntop),
            use_container_width=True
        )

    with st.expander(f'Show **earnings** trends for top **{ntop}** miners'):

        st.plotly_chart(
            plotting.plot_owner_emission_trends(df, time_col=x, y='owner_take', color='netuid', ntop=ntop),
            use_container_width=True
        )


    # selected_block = st.selectbox('**Block**', reversed(df_sel.block.unique()), index=0)

    # st.dataframe(df_sel.loc[df_sel['block']==selected_block])

with tab2:

    st.markdown('#')
    st.markdown('#')
    st.subheader('Validator Revenue')
    st.info('**Activity** *shows the change in stake and emission over time for **validators**, grouped by coldkey*')

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
