from requests.sessions import DEFAULT_REDIRECT_LIMIT
import streamlit as st
from pathlib import Path
import requests
import pandas as pd
import numpy as np
import altair as alt
from pandas.io.json import json_normalize
import base64
import SessionState

# sets up function to call Markdown File for "about"
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def download_csv(origdf, filename):
    tmp_download_link = download_link(origdf, filename, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


def filter_by(filterer, select_data, full_data, key):
    options = select_data[filterer].unique().tolist()
    selected_options = st.sidebar.multiselect('', options, key = key)
    list_of_selected = list(selected_options)

    if list_of_selected:
        chosen_columns =  select_data[filterer].isin(selected_options)
        subframe = select_data[chosen_columns]
        fullframe = full_data[chosen_columns]
    else:
        subframe = select_data
        fullframe = full_data

    return [fullframe, subframe]

def draw_chart(col_name, count_name, origdf):
    chart_data = origdf.copy()
    chart_data[count_name] = chart_data.groupby(by=col_name)[col_name].transform('count')
    # st.write(chart_data)
    #TODO: Format chart for easier view
    chart = alt.Chart(chart_data).mark_bar().encode(
        x = count_name,
        y = col_name,
    )
    text = chart.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text = count_name
    )
    st.write(chart+text)

def draw_mt_chart(origdf):
    cf_count = df['musical_type'].str.match('cantus firmus').values.sum()
    sog_count = df['musical_type'].str.match('soggetto').values.sum()
    csog_count = df['musical_type'].str.match('counter soggetto').values.sum()
    cd_count = df['musical_type'].str.match('contrapuntal duo').values.sum()
    fg_count = df['musical_type'].str.match('fuga').values.sum()
    id_count = df['musical_type'].str.match('imitative duo').values.sum()
    nid_count = df['musical_type'].str.match('non-imitative duo').values.sum()
    pe_count = df['musical_type'].str.match('periodic entry').values.sum()
    cad_count = df['musical_type'].str.match('cadence').values.sum()
    hr_count = df['musical_type'].str.match('homorhythm').values.sum()

    mt_dict = {'types':['Cantus firmus', 'Soggetto', 'Counter-soggetto', 'Contrapuntal duo', 'Fuga', 'Imitative Duo', 'Non-imitative duo', 'Periodc entries', 'Cadence', 'Homorhythm'],
                'count': [cf_count, sog_count, csog_count, cd_count, fg_count, id_count, nid_count, pe_count, cad_count, hr_count ]}
    df_mt = pd.DataFrame(data=mt_dict)
    chart_mt = alt.Chart(df_mt).mark_bar().encode(
        x = 'count',
        y = 'types',
    )
    text_mt = chart_mt.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text = 'count'
    )
    st.write(chart_mt+text_mt)

def draw_rt_chart(origdf):
    qt_count = df_r['relationship_type'].str.match('quotation').values.sum()
    tm_count = df_r['relationship_type'].str.match('mechanical transformation').values.sum()
    tnm_count = df_r['relationship_type'].str.match('non-mechanical transformation').values.sum()
    om_count = df_r['relationship_type'].str.match('omission').values.sum()
    nm_count = df_r['relationship_type'].str.match('new material').values.sum()

    rt_dict = {'types':['Quotation', 'Mechanical transformation', 'Non-mechanical transformation', 'Omission', 'New Materia'],
                'count': [qt_count, tm_count, tnm_count, om_count, nm_count]}
    df_rt = pd.DataFrame(data=rt_dict)
    chart_rt = alt.Chart(df_rt).mark_bar().encode(
        x = 'count',
        y = 'types',
    )
    text_rt = chart_rt.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text = 'count'
    )
    st.write(chart_rt+text_rt)


# no longer needed
def get_subtype_count(origdf, mt, stname):
    mt_selected = ""
    subtype = mt_selected
    subtype_count = origdf[subtype].shape[0]
    return int(subtype_count)

# no longer needed
def get_cdtype_count(origdf, stname):
    subtype = (origdf['mt_cad_type'].isin(stname))
    subtype_count = origdf[subtype].shape[0]
    return int(subtype_count)

# no longer needed
def get_mt_count(origdf, mtname):
    musicaltype = (origdf[mtname] == 1)
    musicaltype_count = origdf[musicaltype].shape[0]
    return int(musicaltype_count)


def get_subtype_charts(selected_type, origdf):
    if selected_type.lower() == "cadence":
        mt_selected = 'cadence'
        cd_chosen = df['musical_type'].str.match('cadence')
        cd_full = origdf[cd_chosen]
        #separate cd type chart (3 types and counts of each)
        authentic = df['musical_type'].str.match('cadence') & df['type'].str.match('authentic')
        phrygian = df['musical_type'].str.match('cadence') & df['type'].str.match('phrygian')
        plagal = df['musical_type'].str.match('cadence') & df['type'].str.match('plagal')
        irregular = df['musical_type'].str.match('cadence') & df['firreg_cadence']
        cd_dict = {'Cadence Type':['authentic','phrygian','plagal'],
                    'countcdtypes': [
                        authentic.sum(),
                        phrygian.sum(),
                        plagal.sum(),
                        irregular.sum(),
                    ]}
        df_cd = pd.DataFrame(data=cd_dict)
        chart_cd = alt.Chart(df_cd).mark_bar().encode(
            x = 'countcdtypes',
            y = 'Cadence Type',
        )
        text_cd = chart_cd.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text = 'countcdtypes'
        )
        st.write(chart_cd+text_cd)

    if selected_type.lower() == "cadence":
            mt_selected = 'cadence'
            cd_chosen = df['musical_type'].str.match('cadence')
            cd_full = origdf[cd_chosen]
            #separate cd tone chart (many tone and counts of each)
            C = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('C')
            D = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('D')
            E_flat = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('E-flat')
            E = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('E')
            F = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('F')
            G = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('G')
            A = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('A')
            B_flat = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('B-flat')
            B = df['musical_type'].str.match('cadence') & df['cadence_tone'].str.match('B')
            ct_dict = {'Cadence Tone':['C','D','E-flat', 'E', 'F', 'G', 'A', 'B-flat', 'B'],
                        'countcdtones': [
                            C.sum(),
                            D.sum(),
                            E_flat.sum(),
                            E.sum(),
                            F.sum(),
                            G.sum(),
                            A.sum(),
                            B.sum(),
                            B_flat.sum(),
                        ]}
            df_cd = pd.DataFrame(data=ct_dict)
            chart_ct = alt.Chart(df_cd).mark_bar().encode(
                x = 'countcdtones',
                y = 'Cadence Tone',
            )
            text_ct = chart_ct.mark_text(
                align='left',
                baseline='middle',
                dx=3
            ).encode(
                text = 'countcdtones'
            )
            st.write(chart_ct+text_ct)

    if selected_type.lower() == "fuga":
        mt_selected = 'fuga'
        fg_chosen = df['musical_type'].str.match('fuga')
        fg_full = origdf[fg_chosen]
        fg_dict = {'Subtypes':['periodic', 'sequential', 'inverted', 'retrograde'],
                    'count': [
                        df['periodic'].sum(),
                        df['sequential'].sum(),
                        df['inverted'].sum(),
                        df['retrograde'].sum(),
                    ]}
        df_fg = pd.DataFrame(data=fg_dict)
        chart_fg = alt.Chart(df_fg).mark_bar().encode(
            x = 'count',
            y = 'Subtypes',
        )
        text_fg = chart_fg.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text = 'count'
        )
        st.write(chart_fg+text_fg)

    if selected_type.lower() == "periodic entry":
        mt_selected = 'periodic entry'
        pe_chosen = df['musical_type'].str.match('periodic entry')
        pe_full = origdf[pe_chosen]

        pe_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                    'count': [
                        df['sequential'].sum(),
                        df['invertible_counterpoint'].sum(),
                        df['added_entries'].sum(),
                    ]}
        df_pe = pd.DataFrame(data=pe_dict)
        chart_pe = alt.Chart(df_pe).mark_bar().encode(
            x = 'count',
            y = 'Subtypes',
        )
        text_pe = chart_pe.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text = 'count'
        )
        st.write(chart_pe+text_pe)

    if selected_type.lower() == "imitative duo":
        mt_selected = 'imitative duo'
        id_chosen = df['musical_type'].str.match('imitative duo')
        id_full = origdf[id_chosen]

        id_dict = {'Subtypes':['invertible counterpoint', 'added entries'],
                    'count': [
                        df['invertible_counterpoint'].sum(),
                        df['details.added_entries'].sum(),
                    ]}
        df_id = pd.DataFrame(data=id_dict)
        chart_id = alt.Chart(df_id).mark_bar().encode(
            x = 'count',
            y = 'Subtypes',
        )
        text_id = chart_id.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text = 'count'
        )
        st.write(chart_id+text_id)

    if selected_type.lower() == "non-imitative duo":
        mt_selected = 'non-imitative duo'
        nid_chosen = df['musical_type'].str.match('non-imitative duo')
        nid_full = origdf[nid_chosen]

        nid_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                    'count': [
                        df['fields.details.sequential'].sum(),
                        df['fields.details.invertible counterpoint'].sum(),
                        df['fields.details.added entries'].sum(),
                    ]}
        df_nid = pd.DataFrame(data=nid_dict)
        chart_nid = alt.Chart(df_nid).mark_bar().encode(
            x = 'count',
            y = 'Subtypes',
        )
        text_nid = chart_nid.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text = 'count'
        )
        st.write(chart_nid+text_nid)

    if selected_type.lower() == "homorhythm":
        mt_selected = 'homorhythm'
        hr_chosen = df['musical_type'].str.match('homorhythm')
        hr_full = origdf[hr_chosen]
        simple = df['musical_type'].str.match('homorhythm') & df['type'].str.match('simple')
        staggered = df['musical_type'].str.match('homorhythm') & df['type'].str.match('staggered')
        sequential = df['musical_type'].str.match('homorhythm') & df['type'].str.match('sequential')
        fauxbourdon = df['musical_type'].str.match('homorhythm') & df['type'].str.match('fauxbourdon')

        hr_dict = {'Subtypes':['simple', 'staggered', 'sequential', 'fauxbourdon'],
                    'count': [
                        simple.sum(),
                        staggered.sum(),
                        sequential.sum(),
                        fauxbourdon.sum(),
                    ]}
        df_hr = pd.DataFrame(data=hr_dict)
        chart_hr = alt.Chart(df_hr).mark_bar().encode(
            x = 'count',
            y = 'Subtypes',
        )
        text_hr = chart_hr.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text = 'count'
        )
        st.write(chart_hr+text_hr)


#main heading of the resource

st.header("CRIM Project Meta Data Viewer")

st.write("These tools assemble metadata for about 5000 observations and 2500 relationships in Citations: The Renaissance Imitation Mass.")
st.write("Visit the [CRIM Project](https://crimproject.org) and its [Members Pages] (https://sites.google.com/haverford.edu/crim-project/home).")
st.markdown(

'''
- Use the __checkboxes at the left__ to view summaries of Observations by Type, Analyst, and Piece.
- For __Faceted Observation Search__ you can select any number of __pieces__ or __musical types__ (in either order), then view and download CSV files resulting tables.
- For __Faceted Relationship Search__ you can select any number of __pieces__ or __relationship types__ (in either order), then view and download CSV files resulting tables.
- Subtype tools display details as __charts__.
- Want to view a given __observation__ or __relationship__ with notation and metadata?  Enter the given number as noted in the dialogue box.
''')
# st.write("For __Observations__ you can begin with __Piece__ or __Musical Type__.")
# st.write("For __Relationships__ you can begin with __Piece__ or __Relationship Type__.")
# st.write("Subtype tools display __graphs and charts__ of data for each type and subtype in the CRIM Vocabularies")

# st.write("Also see the [Relationship Metadata Viewer] (https://crim-relationship-data-viewer.herokuapp.com/)")

# st.cache speeds things up by holding data in cache

@st.cache(allow_output_mutation=True)

# get the data function
def get_data(link):
    data = requests.get(link).json()
    #df = pd.DataFrame(data)
    df = pd.json_normalize(data)
    return df


# df = get_data('http://crimproject.org/data/observations/')

df = get_data('https://raw.githubusercontent.com/CRIM-Project/CRIM-online/dev/crim/fixtures/migrated-crimdata/cleaned_observations.json')
df.rename(columns={'pk': 'id',
                    'fields.piece':'piece_id',
                    'fields.observer' : 'observer_name',
                    'fields.musical_type': 'musical_type',
                    'fields.details.entry intervals': 'entry_intervals',
                    'fields.details.time intervals': 'time_intervals',
                    'fields.details.periodic': 'periodic',
                    'fields.details.regularity': 'regularity',
                    'fields.details.sequential': 'sequential',
                    'fields.details.inverted': 'inverted',
                    'fields.details.retrograde': 'retrograde',
                    'fields.details.invertible counterpoint': 'invertible_counterpoint',
                    'fields.details.added entries': 'added_entries',
                    'fields.details.ostinato': 'ostinato',
                    'fields.details.type': 'type',
                    'fields.details.dialogue':  'hr_dialogue',
                     'fields.details.tone':  'cadence_tone',
                     'fields.details.irregular cadence': 'irreg_cadence',
                     'fields.details.features': 'features',
}, inplace=True)

drop_list = ['fields.definition',
                     'fields.ema',
                     'fields.remarks',
                     'fields.curated',
                     'fields.created',
                     'fields.updated',
                     'fields.details.voice name',
                     'fields.details.voice names',
                     'fields.details.voice name reg',
                     'fields.details.voice names reg',
                     'fields.details.voice',
                     'fields.details.voices',
                     ]

df_r = get_data('https://raw.githubusercontent.com/CRIM-Project/CRIM-online/dev/crim/fixtures/migrated-crimdata/cleaned_relationships.json')
df_r.rename(columns={'pk': 'id',
                    'fields.observer':'observer_name',
                    'fields.relationship_type': 'relationship_type',
                    'fields.model_observation': 'model_observation',
                    'fields.derivative_observation': 'derivative_observation'}, inplace=True)


select_data = df[["id", "observer_name", "piece_id", "musical_type"]]
select_data_r = df_r[['id', 'observer_name', 'relationship_type', 'model_observation', 'derivative_observation']]


# Sidebar options for _all_ data of a particular type

st.sidebar.write('Use buttons and checkboxes below to view or filter all data of a given category.')
st.sidebar.header("Observation Tables and Charts")
if st.sidebar.checkbox('Select Observation Tables and Charts'):
    st.markdown("---")
    st.header("Observations")
    if st.sidebar.checkbox('All Observation Metadata Fields'):
        st.subheader('All CRIM Observations with All Metadata')
        st.write(df)

    if st.sidebar.checkbox('Observer, Piece, Musical Type'):
        st.subheader('Summary: Observer, Piece, Musical Type')
        st.write(select_data)

    if st.sidebar.checkbox('Observations per Analyst'):
        st.subheader('Total Observations per Analyst')
        st.write(df['observer_name'].value_counts())

    if st.sidebar.checkbox('Observations per Piece'):
        st.subheader('Total Observations per Piece')
        st.write(df['piece_id'].value_counts())

    if st.sidebar.checkbox('Observations per Musical Type'):
        st.subheader('Total Observations per Musical Type')
        st.write(df['musical_type'].value_counts())

    if st.sidebar.checkbox('Observation Charts'):
        st.subheader("Graphical representation of result")
        showtype = st.checkbox('By musical type', value=False)
        showpiece = st.checkbox('By piece', value=False)
        if showtype:
           draw_mt_chart(df)
        if showpiece:
           draw_chart("piece_id", "countpiece", df)

# if st.sidebar.checkbox('Select Observation Charts'):
#     # if st.sidebar.checkbox('All Observation Metadata Fields'):
#     #     st.subheader("Graphical representation of result")
#         showtype = st.checkbox('By musical type', value=False)
#         showpiece = st.checkbox('By piece', value=False)
#         if showtype:
#            draw_mt_chart(df)
#         if showpiece:
#            draw_chart("piece_id", "countpiece", piece_sub)



   # showall = st.sidebar.checkbox('Show Subtypes for all Observations', value=False)
   # if showall:
   #     st.header("Subtype Charts for All Pieces")
   #     if df['musical_type'].isin(['fuga']).any():
   #         fg_dict = {'Subtypes':['periodic', 'sequential', 'inverted', 'retrograde'],
   #         'count': [
   #             df['periodic'].sum(),
   #             df['sequential'].sum(),
   #             df['inverted'].sum(),
   #             df['retrograde'].sum(),
   #         ]}
   #         df_fg = pd.DataFrame(data=fg_dict)
   #         chart_fg = alt.Chart(df_fg).mark_bar().encode(
   #             x = 'count',
   #             y = 'Subtypes',
   #         )
   #         text_fg = chart_fg.mark_text(
   #             align='left',
   #             baseline='middle',
   #             dx=3
   #         ).encode(
   #             text = 'count'
   #         )
   #         st.write("Fuga Subtypes from Filtered View Above")
   #         st.write(chart_fg+text_fg)

# showfiltered = st.checkbox('Show subtype charts for filtered results', value=False)
# if showfiltered:
#     selected_types = df['musical_type'].unique().tolist()
#     for mt in selected_types:
#       get_subtype_charts(selected_types, df)
#       if str(mt) in ['cadence', 'fuga', 'periodic entry', 'imitative duo', 'non-imitative duo', 'homorythm']:
#           st.write('Type: ' + str(mt))
#           get_subtype_charts(mt, piece_full)



st.sidebar.header("Relationship Tables and Charts")

if st.sidebar.checkbox('Select Relationship Tables and Charts'):
    st.markdown("---")
    st.header("Relationships")
    if st.sidebar.checkbox('All Relationship Metadata Fields'):
        st.subheader('All Relationship Metadata Fields')
        st.write(df_r)

    if st.sidebar.checkbox('Observer, Relationship Type, Model, Derivative'):
        st.subheader('Selected Metadata:  Observer, Relationship Type, Model Observation ID, Derivative Observation ID')
        st.write(select_data_r)

    if st.sidebar.checkbox('Relationships per Analyst'):
        st.subheader('Total Relationships per Analyst')
        st.write(df_r['observer_name'].value_counts())

    if st.sidebar.checkbox('Relationships per Type'):
        st.subheader('Total Relationships per Type')
        st.write(df_r['relationship_type'].value_counts())

    if st.sidebar.checkbox('Relationship Charts'):
      st.subheader("Relationships by Main Type")
      qt_count = df_r['relationship_type'].str.match('quotation').values.sum()
      tm_count = df_r['relationship_type'].str.match('mechanical transformation').values.sum()
      tnm_count = df_r['relationship_type'].str.match('non-mechanical transformation').values.sum()
      om_count = df_r['relationship_type'].str.match('omission').values.sum()
      nm_count = df_r['relationship_type'].str.match('new material').values.sum()

      rt_dict = {'Relationship Types':['Quotation', 'Mechanical transformation', 'Non-mechanical transformation', 'Omission', 'New Materia'],
                  'count': [qt_count, tm_count, tnm_count, om_count, nm_count]}
      df_rt = pd.DataFrame(data=rt_dict)
      chart_rt = alt.Chart(df_rt).mark_bar().encode(
          x = 'count',
          y = 'Relationship Types',
      )
      text_rt = chart_rt.mark_text(
          align='left',
          baseline='middle',
          dx=3
      ).encode(
          text = 'count'
      )
      st.write(chart_rt+text_rt)

      st.subheader("Relationship Subtypes Charts")
      if st.checkbox('Quotation Types'):
          st.subheader("Quotation Types")
          # Quotation Chart
          exact = df_r['fields.details.type'].str.match('exact')
          monnayage = df_r['fields.details.type'].str.match('monnayage')
          rl_q_dict = {'Quotation Subtype':['exact','monnayage'],
                      'countrltypes': [
                          exact.sum(),
                          monnayage.sum(),
                      ]}
          df_rl_q = pd.DataFrame(data=rl_q_dict)
          chart_rl_q = alt.Chart(df_rl_q).mark_bar().encode(
              x = 'countrltypes',
              y = 'Quotation Subtype',
          )
          text_rl_q = chart_rl_q.mark_text(
              align='left',
              baseline='middle',
              dx=3
          ).encode(
              text = 'countrltypes'
          )
          st.write(chart_rl_q+text_rl_q)

      if st.checkbox('Mechanical Transformation'):
          st.subheader("Mechanical Transformation Subtypes")
      # Mechanical Trans Chart
      #  later add diminution and augmentation once these are in the JSON
      # add kind of transposition (as three types?)
          sound_diff = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.sounding in different voices']
          melodically_inverted = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.melodically inverted']
          retrograde = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.retrograde']
          metrically_shifted = df_r['fields.details.metrically shifted']
          double_cpt = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.double or invertible counterpoint']
          # diminution = df_r['fields.details.systematic diminution']
          # augmentation = df_r['fields.details.systematic augmentation']
          rl_mt_dict = {'Mechanical Transformation Subtype':['sounding in different voices','melodically inverted', 'retrograde','metrically shifted', 'double or invertible counterpoint'],
                      'countrltypes': [
                          sound_diff.sum(),
                          melodically_inverted.sum(),
                          retrograde.sum(),
                          metrically_shifted.sum(),
                          double_cpt.sum(),
                          # diminution.sum(),
                          # augmentation.sum()
                          # transposition,
                      ]}
          df_rl_mt = pd.DataFrame(data=rl_mt_dict)
          chart_rl_mt = alt.Chart(df_rl_mt).mark_bar().encode(
              x = 'countrltypes',
              y = 'Mechanical Transformation Subtype',
          )
          text_rl_mt = chart_rl_mt.mark_text(
              align='left',
              baseline='middle',
              dx=3
          ).encode(
              text = 'countrltypes'
          )
          st.write(chart_rl_mt+text_rl_mt)

      if st.checkbox('Non-Mechanical Transformation'):
          st.subheader("Non-Mechanical Transformation Subtypes")
          # Non Mechanical Trans Chart
          #  later double counterpoint once in the JSON
          sound_diff = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.sounding in different voices']
          melodically_inverted = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.melodically inverted']
          retrograde = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.retrograde']
          metrically_shifted = df_r['fields.details.whole passage metrically shifted']
          transposed = df_r['fields.details.whole passage transposed']
          new_cs = df_r['fields.details.new counter subject']
          old_cs_tr = df_r['fields.details.old counter subject transposed']
          old_cs_ms = df_r['fields.details.old counter subject shifted metrically']
          new_comb = df_r['fields.details.new combination']
          # double_cpt = df_r['fields.relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.double or invertible counterpoint']


          rl_nmt_dict = {'Non-Mechanical Transformation Subtype':['sounding in different voices','melodically inverted', 'retrograde',
          'metrically shifted', 'transposed', 'new counter subject', 'old counter subject transposed', 'old counter subject shifted metrically'
          , 'new combination'],
                      'countrltypes': [
                          sound_diff.sum(),
                          melodically_inverted.sum(),
                          retrograde.sum(),
                          metrically_shifted.sum(),
                          transposed.sum(),
                          new_cs.sum(),
                          old_cs_tr.sum(),
                          old_cs_ms.sum(),
                          new_comb.sum(),
                          # diminution.sum(),
                          # augmentation.sum(),
                      ]}
          df_rl_nmt = pd.DataFrame(data=rl_nmt_dict)
          chart_rl_nmt = alt.Chart(df_rl_nmt).mark_bar().encode(
              x = 'countrltypes',
              y = 'Non-Mechanical Transformation Subtype',
          )
          text_rl_nmt = chart_rl_nmt.mark_text(
              align='left',
              baseline='middle',
              dx=3
          ).encode(
              text = 'countrltypes'
          )
          st.write(chart_rl_nmt+text_rl_nmt)

# st.subheader("All Data and MEI Views")
# sa = st.text_input('Name of file for download (must include ".csv")')
# ## Button to download CSV of results
# if st.button('Download Complete Dataset as CSV'):
#     #s = st.text_input('Enter text here')
#     tmp_download_link = download_link(df, sa, 'Click here to download your data!')
#     st.markdown(tmp_download_link, unsafe_allow_html=True)








# st.sidebar.markdown("---")
st.sidebar.header("Filter Observations")
if st.sidebar.checkbox('Filter Observations'):
   st.sidebar.subheader("The order of filtering matters!")
   st.sidebar.write("You can begin by selecting pieces, then filter by type; or the reverse.")
   st.markdown("---")
   st.header("Filtered Observations")

# from linh:

    # from LINH
   order = st.sidebar.radio("Select order to filter data: ", ('Piece then Musical Type', 'Musical Type then Piece'))
   if (order == 'Piece then Musical Type'):
        #filter by piece
        st.sidebar.subheader("Filter by Piece")
        piece_frames = filter_by("piece_id", select_data, df, 'a')
        piece_full = piece_frames[0]
        piece_sub = piece_frames[1]
        #st.write(piece_full)
        #st.write(piece_sub)

        #filter by type with or without piece
        st.sidebar.subheader("Filter by Musical Type")
        mt_frames = filter_by('musical_type', piece_sub, piece_full, 'b')
        mt_full = mt_frames[0]
        mt_sub = mt_frames[1]
        mt_drop_cols = mt_full.drop(columns=drop_list)
        st.subheader("Filtered Observations")
        st.write(mt_full)
        # st.write(mt_drop_cols)

        showfiltered = st.sidebar.checkbox('Show subtype charts for filtered results', value=False)
        if showfiltered:
# Cantus firmus chart_rt
            if mt_sub['musical_type'].isin(['cantus firmus']).any():
               cf_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    mt_full['features'].isin(['both pitches and durations']).sum(),
                    mt_full['features'].isin(['pitches only']).sum(),
                    mt_full['features'].isin(['durations only']).sum(),
               ]}
               df_cf = pd.DataFrame(data=cf_dict)
               chart_cf = alt.Chart(df_cf).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_cf = chart_cf.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Cantus Firmus Subtypes from Filtered View Above")
               st.write(chart_cf+text_cf)
# Soggetto chart_rt
            if mt_sub['musical_type'].isin(['soggetto']).any():
               sg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    mt_full['features'].isin(['both pitches and durations']).sum(),
                    mt_full['features'].isin(['pitches only']).sum(),
                    mt_full['features'].isin(['durations only']).sum(),
               ]}
               df_sg = pd.DataFrame(data=sg_dict)
               chart_sg = alt.Chart(df_sg).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_sg = chart_sg.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Soggetto Subtypes from Filtered View Above")
               st.write(chart_sg+text_sg)
# C Soggetto chart_rt
            if mt_sub['musical_type'].isin(['counter soggetto']).any():
               csg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    mt_full['features'].isin(['both pitches and durations']).sum(),
                    mt_full['features'].isin(['pitches only']).sum(),
                    mt_full['features'].isin(['durations only']).sum(),
               ]}
               df_csg = pd.DataFrame(data=csg_dict)
               chart_csg = alt.Chart(df_csg).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_csg = chart_csg.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Soggetto Subtypes from Filtered View Above")
               st.write(chart_csg+text_csg)
# Contrapuntal Duo chart_rt
            if mt_sub['musical_type'].isin(['contrapuntal duo']).any():
               cd_dict = {'Subtypes':['contrapuntal duos'],
               'count': [
                    mt_full['musical_type'].isin(['contrapuntal duo']).sum(),

               ]}
               df_cd = pd.DataFrame(data=cd_dict)
               chart_cd = alt.Chart(df_cd).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_cd = chart_cd.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Soggetto Subtypes from Filtered View Above")
               st.write(chart_cd+text_cd)
# FUGA Chart
            if mt_sub['musical_type'].isin(['fuga']).any():
                fg_dict = {'Subtypes':['periodic', 'sequential', 'inverted', 'retrograde'],
                'count': [
                    mt_full['periodic'].sum(),
                    mt_full['sequential'].sum(),
                    mt_full['inverted'].sum(),
                    mt_full['retrograde'].sum(),
                ]}
                df_fg = pd.DataFrame(data=fg_dict)
                chart_fg = alt.Chart(df_fg).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_fg = chart_fg.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Fuga Subtypes from Filtered View Above")
                st.write(chart_fg+text_fg)
# PEN chart
            if mt_sub['musical_type'].isin(['periodic entry']).any():
                pe_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                mt_full['sequential'].sum(),
                                mt_full['invertible_counterpoint'].sum(),
                                mt_full['added_entries'].sum(),
                            ]}
                df_pe = pd.DataFrame(data=pe_dict)
                chart_pe = alt.Chart(df_pe).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_pe = chart_pe.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Periodic Entry Subtypes from Filtered View Above")
                st.write(chart_pe+text_pe)
# ID Subtypes
            if mt_sub['musical_type'].isin(['imitative duo']).any():

                id_dict = {'Subtypes':['invertible counterpoint', 'added entries'],
                            'count': [
                                mt_full['invertible_counterpoint'].sum(),
                                mt_full['added_entries'].sum(),
                            ]}
                df_id = pd.DataFrame(data=id_dict)
                chart_id = alt.Chart(df_id).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_id = chart_id.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Imitative Duo Subtypes from Filtered View Above")

                st.write(chart_id+text_id)
# NIM here
            if mt_sub['musical_type'].isin(['non-imitative duo']).any():

                nim_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                mt_full['sequential'].sum(),
                                mt_full['invertible_counterpoint'].sum(),
                                mt_full['added_entries'].sum(),
                            ]}
                df_nim = pd.DataFrame(data=nim_dict)
                chart_nim = alt.Chart(df_nim).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_nim = chart_nim.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Non-Imitative Duo Subtypes from Filtered View Above")
                st.write(chart_nim+text_nim)
# HR Here
            if mt_sub['musical_type'].isin(['homorhythm']).any():
                hr_dict = {'Subtypes':['simple', 'staggered', 'sequential', 'fauxbourdon'],
                            'count': [
                                mt_full['type'].isin(['simple']).sum(),
                                mt_full['type'].isin(['staggered']).sum(),
                                mt_full['type'].isin(['sequential']).sum(),
                                mt_full['type'].isin(['fauxbourdon']).sum(),
                            ]}
                df_hr = pd.DataFrame(data=hr_dict)
                chart_hr = alt.Chart(df_hr).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_hr = chart_hr.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Homorhythm Subtypes from Filtered View Above")
                st.write(chart_hr+text_hr)
# CAD here
            if mt_sub['musical_type'].isin(['cadence']).any():
                cd_dict = {'Cadence Type':['authentic','phrygian','plagal'],
                            'countcdtypes': [
                                mt_full['type'].isin(['authentic']).sum(),
                                mt_full['type'].isin(['phrygian']).sum(),
                                mt_full['type'].isin(['plagal']).sum(),
                            ]}
                df_cd = pd.DataFrame(data=cd_dict)
                chart_cd = alt.Chart(df_cd).mark_bar().encode(
                    x = 'countcdtypes',
                    y = 'Cadence Type',
                )
                text_cd = chart_cd.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'countcdtypes'
                )
                st.write("Cadence Types from Filtered View Above")
                st.write(chart_cd+text_cd)
# cad Tone
            if mt_sub['musical_type'].isin(['cadence']).any():
                ct_dict = {'Cadence Tone':['C','D','E-flat', 'E', 'F', 'G', 'A', 'B-flat', 'B'],
                            'countcdtones': [
                                mt_full['cadence_tone'].isin(['C']).sum(),
                                mt_full['cadence_tone'].isin(['D']).sum(),
                                mt_full['cadence_tone'].isin(['E_flat']).sum(),
                                mt_full['cadence_tone'].isin(['E']).sum(),
                                mt_full['cadence_tone'].isin(['F']).sum(),
                                mt_full['cadence_tone'].isin(['G']).sum(),
                                mt_full['cadence_tone'].isin(['A']).sum(),
                                mt_full['cadence_tone'].isin(['B_flat']).sum(),
                                mt_full['cadence_tone'].isin(['B']).sum(),
                            ]}
                df_cd = pd.DataFrame(data=ct_dict)
                chart_ct = alt.Chart(df_cd).mark_bar().encode(
                    x = 'countcdtones',
                    y = 'Cadence Tone',
                )
                text_ct = chart_ct.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'countcdtones'
                )
                st.write("Cadence Tones from Filtered View Above")
                st.write(chart_ct+text_ct)

        st.subheader("Enter Observation to View on CRIM Project")

        prefix = "https://crimproject.org/observations/"
        int_val = st.text_input('Observation Number')
        combined = prefix + int_val

        st.markdown(combined, unsafe_allow_html=True)

        st.subheader('Download Filtered Results as CSV')
        userinput = st.text_input('Name of file for download (must include ".csv")', key='1')
        if st.button('Download without type details', key='11'):
            download_csv(mt_sub, userinput)
        st.write('or')
        if st.button('Download with type details', key='12'):
            download_csv(mt_full, userinput)

#  THESE TWO WORK CORRECTLY
    # show_types = st.checkbox('Show Distribution of Musical Types in Filtered Results', value=False)
    # if show_types:
    #     st.subheader("Distribution of Musical Types in Filtered Results Above")
    #     musical_types = mt_sub['musical_type'].value_counts()
    #     st.write(musical_types)
    #
    # show_pieces = st.checkbox('Show Distribution of Pieces in Filtered Results', value=False)
    # if show_pieces:
    #     st.subheader("Distribution of Pieces in Filtered Results Above")
    #     piece_ids = mt_sub['piece_id'].value_counts()
    #     st.write(piece_ids)
    #
   else:
    #filter by musical type
    #filter by type with or without piece

        st.sidebar.subheader("Musical Type")
        mt_frames = filter_by('musical_type', select_data, df, 'z')
        mt_full = mt_frames[0]
        mt_sub = mt_frames[1]
        #st.write(mt_full)

        #filter by piece with or without musical type
        st.sidebar.subheader("Piece")
        piece_frames = filter_by('piece_id', mt_sub, mt_full, 'y')
        piece_full = piece_frames[0]
        piece_sub = piece_frames[1]
        st.subheader('Filtered Observations')
        st.write(piece_sub)
    # view url via link
        showfiltered = st.sidebar.checkbox('Show subtype charts for filtered results', value=False)
        if showfiltered:
# Cantus firmus chart_rt
            if piece_sub['musical_type'].isin(['cantus firmus']).any():
               cf_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    piece_full['features'].isin(['both pitches and durations']).sum(),
                    piece_full['features'].isin(['pitches only']).sum(),
                    piece_full['features'].isin(['durations only']).sum(),
               ]}
               df_cf = pd.DataFrame(data=cf_dict)
               chart_cf = alt.Chart(df_cf).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_cf = chart_cf.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Cantus Firmus Subtypes from Filtered View Above")
               st.write(chart_cf+text_cf)
# Soggetto chart_rt
            if piece_sub['musical_type'].isin(['soggetto']).any():
               sg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    piece_full['features'].isin(['both pitches and durations']).sum(),
                    piece_full['features'].isin(['pitches only']).sum(),
                    piece_full['features'].isin(['durations only']).sum(),
               ]}
               df_sg = pd.DataFrame(data=sg_dict)
               chart_sg = alt.Chart(df_sg).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_sg = chart_sg.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Soggetto Subtypes from Filtered View Above")
               st.write(chart_sg+text_sg)
# C Soggetto chart_rt
            if piece_sub['musical_type'].isin(['counter soggetto']).any():
               csg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    piece_full['features'].isin(['both pitches and durations']).sum(),
                    piece_full['features'].isin(['pitches only']).sum(),
                    piece_full['features'].isin(['durations only']).sum(),
               ]}
               df_csg = pd.DataFrame(data=csg_dict)
               chart_csg = alt.Chart(df_csg).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_csg = chart_csg.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Soggetto Subtypes from Filtered View Above")
               st.write(chart_csg+text_csg)
# Contrapuntal Duo chart_rt
            if piece_sub['musical_type'].isin(['contrapuntal duo']).any():
               cd_dict = {'Subtypes':['contrapuntal duos'],
               'count': [
                    piece_full['musical_type'].isin(['contrapuntal duo']).sum(),

               ]}
               df_cd = pd.DataFrame(data=cd_dict)
               chart_cd = alt.Chart(df_cd).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
               )
               text_cd = chart_cd.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
               ).encode(
                    text = 'count'
               )
               st.write("Soggetto Subtypes from Filtered View Above")
               st.write(chart_cd+text_cd)
# FUGA Chart
            if piece_sub['musical_type'].isin(['fuga']).any():
                fg_dict = {'Subtypes':['periodic', 'sequential', 'inverted', 'retrograde'],
                'count': [
                    piece_full['periodic'].sum(),
                    piece_full['sequential'].sum(),
                    piece_full['inverted'].sum(),
                    piece_full['retrograde'].sum(),
                ]}
                df_fg = pd.DataFrame(data=fg_dict)
                chart_fg = alt.Chart(df_fg).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_fg = chart_fg.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Fuga Subtypes from Filtered View Above")
                st.write(chart_fg+text_fg)
# PEN chart
            if piece_sub['musical_type'].isin(['periodic entry']).any():
                pe_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                piece_full['sequential'].sum(),
                                piece_full['invertible_counterpoint'].sum(),
                                piece_full['added_entries'].sum(),
                            ]}
                df_pe = pd.DataFrame(data=pe_dict)
                chart_pe = alt.Chart(df_pe).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_pe = chart_pe.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Periodic Entry Subtypes from Filtered View Above")
                st.write(chart_pe+text_pe)
# ID Subtypes
            if piece_sub['musical_type'].isin(['imitative duo']).any():

                id_dict = {'Subtypes':['invertible counterpoint', 'added entries'],
                            'count': [
                                piece_full['invertible_counterpoint'].sum(),
                                piece_full['added_entries'].sum(),
                            ]}
                df_id = pd.DataFrame(data=id_dict)
                chart_id = alt.Chart(df_id).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_id = chart_id.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Imitative Duo Subtypes from Filtered View Above")

                st.write(chart_id+text_id)
# NIM here
            if piece_sub['musical_type'].isin(['non-imitative duo']).any():

                nim_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                piece_full['sequential'].sum(),
                                piece_full['invertible_counterpoint'].sum(),
                                piece_full['added_entries'].sum(),
                            ]}
                df_nim = pd.DataFrame(data=nim_dict)
                chart_nim = alt.Chart(df_nim).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_nim = chart_nim.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Non-Imitative Duo Subtypes from Filtered View Above")
                st.write(chart_nim+text_nim)
# HR Here
            if piece_sub['musical_type'].isin(['homorhythm']).any():
                hr_dict = {'Subtypes':['simple', 'staggered', 'sequential', 'fauxbourdon'],
                            'count': [
                                piece_full['type'].isin(['simple']).sum(),
                                piece_full['type'].isin(['staggered']).sum(),
                                piece_full['type'].isin(['sequential']).sum(),
                                piece_full['type'].isin(['fauxbourdon']).sum(),
                            ]}
                df_hr = pd.DataFrame(data=hr_dict)
                chart_hr = alt.Chart(df_hr).mark_bar().encode(
                    x = 'count',
                    y = 'Subtypes',
                )
                text_hr = chart_hr.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'count'
                )
                st.write("Homorhythm Subtypes from Filtered View Above")
                st.write(chart_hr+text_hr)
# CAD here
            if piece_sub['musical_type'].isin(['cadence']).any():
                cd_dict = {'Cadence Type':['authentic','phrygian','plagal'],
                            'countcdtypes': [
                                piece_full['type'].isin(['authentic']).sum(),
                                piece_full['type'].isin(['phrygian']).sum(),
                                piece_full['type'].isin(['plagal']).sum(),
                            ]}
                df_cd = pd.DataFrame(data=cd_dict)
                chart_cd = alt.Chart(df_cd).mark_bar().encode(
                    x = 'countcdtypes',
                    y = 'Cadence Type',
                )
                text_cd = chart_cd.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'countcdtypes'
                )
                st.write("Cadence Types from Filtered View Above")
                st.write(chart_cd+text_cd)
# cad Tone
            if piece_sub['musical_type'].isin(['cadence']).any():
                ct_dict = {'Cadence Tone':['C','D','E-flat', 'E', 'F', 'G', 'A', 'B-flat', 'B'],
                            'countcdtones': [
                                piece_full['cadence_tone'].isin(['C']).sum(),
                                piece_full['cadence_tone'].isin(['D']).sum(),
                                piece_full['cadence_tone'].isin(['E_flat']).sum(),
                                piece_full['cadence_tone'].isin(['E']).sum(),
                                piece_full['cadence_tone'].isin(['F']).sum(),
                                piece_full['cadence_tone'].isin(['G']).sum(),
                                piece_full['cadence_tone'].isin(['A']).sum(),
                                piece_full['cadence_tone'].isin(['B_flat']).sum(),
                                piece_full['cadence_tone'].isin(['B']).sum(),
                            ]}
                df_cd = pd.DataFrame(data=ct_dict)
                chart_ct = alt.Chart(df_cd).mark_bar().encode(
                    x = 'countcdtones',
                    y = 'Cadence Tone',
                )
                text_ct = chart_ct.mark_text(
                    align='left',
                    baseline='middle',
                    dx=3
                ).encode(
                    text = 'countcdtones'
                )
                st.write("Cadence Tones from Filtered View Above")
                st.write(chart_ct+text_ct)
# 2/6 THIS IS PULLING FULL DATA, noT FILTERED

            # st.subheader("Graphical representation of result")
            # showtype = st.checkbox('By musical type', value=False)
            # showpiece = st.checkbox('By piece', value=False)
            # if showtype:
            #    draw_mt_chart(piece_sub)
            # if showpiece:
            #    draw_chart("piece_id", "countpiece", piece_sub)
# THIS IS OK
        st.subheader("Enter Observation to View on CRIM Project")

        prefix = "https://crimproject.org/observations/"
        int_val = st.text_input('Observation Number')
        combined = prefix + int_val

        st.markdown(combined, unsafe_allow_html=True)

        st.subheader('Download Filtered Results as CSV')
        userinput = st.text_input('Name of file for download (must include ".csv")', key='2')
        if st.button('Download without type details', key='9'):
            download_csv(piece_sub, userinput)
        st.write('or')
        if st.button('Download with type details', key='10'):
            download_csv(piece_full, userinput)
# FIX HERE



    # showfiltered = st.checkbox('Show subtype charts for filtered results here', value=False)
    # if showfiltered:
    #     selected_types = piece_sub['musical_type'].unique().tolist()
    #     for mt in selected_types:
    #         if str(mt).lower() in ['cadence', 'fuga', 'periodic entry', 'imitative duo', 'non-imitative duo', 'homorythm']:
    #             st.write('Type: ' + str(mt))
    #             get_subtype_charts(mt, piece_full)


    # show_types = st.checkbox('Show Distribution of Musical Types in Results', value=False)
    # if show_types:
    #     st.subheader("Distribution of Musical Types in Results ")
    #     musical_types = mt_sub['musical_type'].value_counts()
    #     st.write(musical_types)

    # show_pieces = st.checkbox('Show Distribution of Pieces in Results', value=False)
    # if show_pieces:
    #     piece_ids = mt_sub['piece_id'].value_counts()
    #     # st.write(piece_ids)
    #     st.write(mt_sub)
    # if show_pieces_2:
    #     st.subheader("Distribution of Pieces in Results ")
    #     piece_ids_2 = mt_sub_2['piece_id'].value_counts()
    #     st.write(piece_ids_2)
    # st.subheader("Graphical representation of result")
    # showtype = st.checkbox('By musical type', value=False)
    # showpiece = st.checkbox('By piece', value=False)
    # if showtype:
    #     draw_mt_chart(piece_full)
    # if showpiece:
    #     draw_chart("piece", "countpiece", piece_sub)

    # showfiltered = st.checkbox('Show subtype charts for filtered results', value=False)
    # if showfiltered:
    #     selected_types = piece_sub['musical_type'].unique().tolist()
    #     for mt in selected_types:
    #         if str(mt).lower() in ['cadence', 'fuga', 'periodic entry', 'imitative duo', 'non-imitative duo', 'homorythm']:
    #             st.write('Type: ' + str(mt))
    #             get_subtype_charts(mt, piece_full)

    # st.subheader("Charts by Type")
    # showtype = st.checkbox('By musical type', value=False)
    # showpiece = st.checkbox('By piece', value=False)
    # if showtype:
    #     draw_mt_chart(piece_full)
    # if showpiece:
    #     draw_chart("piece", "countpiece", piece_sub)

    # showfiltered = st.checkbox('Show subtype charts for filtered results', value=False)
    # if showfiltered:
    #     selected_types = piece_sub['musical_type'].unique().tolist()
    #     for mt in selected_types:
    #         if str(mt).lower() in ['cadence', 'fuga', 'periodic entry', 'imitative duo', 'non-imitative duo', 'homorythm']:
    #             st.write('Type: ' + str(mt))
    #             # get_subtype_charts(mt, piece_full)
    #             get_subtype_charts(mt, piece_sub)


st.markdown("---")

# st.markdown("---")
# st.header("RELATIONSHIP VIEWER")

# THE FOLLOWING WILL NOT WORK UNTIL WE CAN RECOVER MODEL ID FROM OBSERVATIONS DF FOR A GIVEN OBS ID
# WHICH IS LISTED IN THE RELATIONSHIP DF AS ID ONLY.
# SAME FOR DERIVATIVE
# order = st.radio("Select order to filter data: ", ('Pieces then Relationship Type', 'Relationship Type then Pieces'))
# if (order == 'Pieces then Relationship Type'):
#     # filter by pieces
#     st.subheader("Model Piece")
#     mpiece_frames = filter_by("model", select_data_r, df_r, 'c')
#     mpiece_full = mpiece_frames[0]
#     mpiece_sub = mpiece_frames[1]

#     st.subheader("Derivative Piece")
#     dpiece_frames = filter_by("derivative", mpiece_sub, mpiece_full, 'd')
#     dpiece_full = dpiece_frames[0]
#     dpiece_sub = dpiece_frames[1]

#     #filter by type with or without pieces

# st.sidebar.subheader("Relationships by Type")
# qt_count = df_r['relationship_type'].str.match('quotation').values.sum()
# tm_count = df_r['relationship_type'].str.match('mechanical transformation').values.sum()
# tnm_count = df_r['relationship_type'].str.match('non-mechanical transformation').values.sum()
# om_count = df_r['relationship_type'].str.match('omission').values.sum()
# nm_count = df_r['relationship_type'].str.match('new material').values.sum()
#
# rt_dict = {'Relationship Types':['Quotation', 'Mechanical transformation', 'Non-mechanical transformation', 'Omission', 'New Materia'],
#             'count': [qt_count, tm_count, tnm_count, om_count, nm_count]}
# df_rt = pd.DataFrame(data=rt_dict)
# chart_rt = alt.Chart(df_rt).mark_bar().encode(
#     x = 'count',
#     y = 'Relationship Types',
# )
# text_rt = chart_rt.mark_text(
#     align='left',
#     baseline='middle',
#     dx=3
# ).encode(
#     text = 'count'
# )
# st.write(chart_rt+text_rt)

# st.subheader("Relationship Subtypes Charts")
# if st.checkbox('Quotation Types'):
#     st.subheader("Quotation Subtypes")
#     # Quotation Chart
#     exact = df_r['fields.quotation type'].str.match('exact')
#     monnayage = df_r['fields.quotation type'].str.match('monnayage')
#     rl_q_dict = {'Quotation Subtype':['exact','monnayage'],
#                 'countrltypes': [
#                     exact.sum(),
#                     monnayage.sum(),
#                 ]}
#     df_rl_q = pd.DataFrame(data=rl_q_dict)
#     chart_rl_q = alt.Chart(df_rl_q).mark_bar().encode(
#         x = 'countrltypes',
#         y = 'Quotation Subtype',
#     )
#     text_rl_q = chart_rl_q.mark_text(
#         align='left',
#         baseline='middle',
#         dx=3
#     ).encode(
#         text = 'countrltypes'
#     )
#     st.write(chart_rl_q+text_rl_q)
#
# if st.checkbox('Mechanical Transformation'):
#     st.subheader("Mechanical Transformation Subtypes")
# # Mechanical Trans Chart
# #  later add diminution and augmentation once these are in the JSON
# # add kind of transposition (as three types?)
#     sound_diff = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.sounding in different voices']
#     melodically_inverted = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.melodically inverted']
#     retrograde = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.retrograde']
#     metrically_shifted = df_r['fields.details.metrically shifted']
#     double_cpt = df_r['relationship_type'].str.match('mechanical transformation') & df_r['fields.details.double or invertible counterpoint']
#     # diminution = df_r['fields.details.systematic diminution']
#     # augmentation = df_r['fields.details.systematic augmentation']
#     rl_mt_dict = {'Mechanical Transformation Subtype':['sounding in different voices','melodically inverted', 'retrograde','metrically shifted', 'double or invertible counterpoint'],
#                 'countrltypes': [
#                     sound_diff.sum(),
#                     melodically_inverted.sum(),
#                     retrograde.sum(),
#                     metrically_shifted.sum(),
#                     double_cpt.sum(),
#                     # diminution.sum(),
#                     # augmentation.sum()
#                     # transposition,
#                 ]}
#     df_rl_mt = pd.DataFrame(data=rl_mt_dict)
#     chart_rl_mt = alt.Chart(df_rl_mt).mark_bar().encode(
#         x = 'countrltypes',
#         y = 'Mechanical Transformation Subtype',
#     )
#     text_rl_mt = chart_rl_mt.mark_text(
#         align='left',
#         baseline='middle',
#         dx=3
#     ).encode(
#         text = 'countrltypes'
#     )
#     st.write(chart_rl_mt+text_rl_mt)
#
# if st.checkbox('Non-Mechanical Transformation'):
#     st.subheader("Non-Mechanical Transformation Subtypes")
#     # Non Mechanical Trans Chart
#     #  later double counterpoint once in the JSON
#     sound_diff = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.sounding in different voices']
#     melodically_inverted = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.melodically inverted']
#     retrograde = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.retrograde']
#     metrically_shifted = df_r['fields.details.whole passage metrically shifted']
#     transposed = df_r['fields.details.whole passage transposed']
#     new_cs = df_r['fields.details.new counter subject']
#     old_cs_tr = df_r['fields.details.old counter subject transposed']
#     old_cs_ms = df_r['fields.details.old counter subject shifted metrically']
#     new_comb = df_r['fields.details.new combination']
#     # double_cpt = df_r['fields.relationship_type'].str.match('non-mechanical transformation') & df_r['fields.details.double or invertible counterpoint']
#
#
#     rl_nmt_dict = {'Non-Mechanical Transformation Subtype':['sounding in different voices','melodically inverted', 'retrograde',
#     'metrically shifted', 'transposed', 'new counter subject', 'old counter subject transposed', 'old counter subject shifted metrically'
#     , 'new combination'],
#                 'countrltypes': [
#                     sound_diff.sum(),
#                     melodically_inverted.sum(),
#                     retrograde.sum(),
#                     metrically_shifted.sum(),
#                     transposed.sum(),
#                     new_cs.sum(),
#                     old_cs_tr.sum(),
#                     old_cs_ms.sum(),
#                     new_comb.sum(),
#                     # diminution.sum(),
#                     # augmentation.sum(),
#                 ]}
#     df_rl_nmt = pd.DataFrame(data=rl_nmt_dict)
#     chart_rl_nmt = alt.Chart(df_rl_nmt).mark_bar().encode(
#         x = 'countrltypes',
#         y = 'Non-Mechanical Transformation Subtype',
#     )
#     text_rl_nmt = chart_rl_nmt.mark_text(
#         align='left',
#         baseline='middle',
#         dx=3
#     ).encode(
#         text = 'countrltypes'
#     )
#     st.write(chart_rl_nmt+text_rl_nmt)


# def get_rel_subtype_charts(selected_type, origdf):
#     if selected_type.lower() == "Quotation":
#         rt_selected = 'Quotation'
#         rt_chosen = df_r['relationship_type'].str.match('Quotation')
#         rt_full = origdf[rt_chosen]
#         #separate rl type chart (2 types and counts of each)
#         exact = df_r['relationship_type'].str.match('Quotation') & df_r['fields.quotation type'].str.match('exact')
#         monnayage = df_r['relationship_type'].str.match('Quotation') & df_r['fields.quotation type'].str.match('monnayage')
#         rl_q_dict = {'Quotation Type':['exact','monnayage'],
#                     'countrltypes': [
#                         exact.sum(),
#                         monnayage.sum(),
#                     ]}
#         df_rl = pd.DataFrame(data=rl_q_dict)
#         chart_rl = alt.Chart(df_rl).mark_bar().encode(
#             x = 'countrltypes',
#             y = 'Quotation Type',
#         )
#         text_rl = chart_rl.mark_text(
#             align='left',
#             baseline='middle',
#             dx=3
#         ).encode(
#             text = 'countrltypes'
#         )
#         st.write(chart_rl+text_rl)

# showall = st.checkbox('Show subtype charts for relationship data', value=False)
# if showall:
#     r_type_options = ['Quotation', 'Mechanical Transformation']
#     r_selected_type = st.radio('', r_type_options, key = 'm')
#     get_rel_subtype_charts(r_selected_type, df_r)

# rt_frames = filter_by('relationship_type', 'df_r', 'select_data_r', 'e')
# # rt_frames = filter_by('relationship_type', dpiece_sub, dpiece_full, 'e')
# rt_full = rt_frames[0]
# rt_sub = rt_frames[1]
# st.markdown('Resulting relationships:')
# #st.write(rt_full)
# st.write(rt_sub)

# st.subheader("Enter Relationship to View on CRIM Project")

#     # view url via link

# prefix = "https://crimproject.org/relationships/"
# int_val = st.text_input('Relationship Number')
# combined = prefix + int_val

# st.markdown(combined, unsafe_allow_html=True)

# st.subheader('Download Filtered Results as CSV')
# userinput_r = st.text_input('Name of file for download (must include ".csv")', key='3')
# if st.button('Download without type details', key='7'):
#     download_csv(rt_sub, userinput_r)
# st.write('or')
# if st.button('Download with type details', key='8'):
#     download_csv(rt_full, userinput_r)

# st.subheader("Graphical representation of result")
# showrtype = st.checkbox('By relationship type', value=False)
# # showmpiece = st.checkbox('By model observation piece', value=False)
# # showdpiece = st.checkbox('By derivative observation piece', value=False)
# if showrtype:
#     draw_rt_chart(rt_full)

# if showmpiece:
#     draw_chart("model", "countmpiece", rt_sub)
# if showdpiece:
#     draw_chart("derivative", "countdpiece", rt_sub)

# else:
#     #filter by musical type
#     st.subheader("Relationship Type")
#     rt_frames = filter_by('relationship_type', select_data_r, df_r, 'x')
#     rt_full = rt_frames[0]
#     rt_sub = rt_frames[1]
#     #st.write(rt_full)

#     #filter by piece with or without musical type
#     st.subheader("Model Piece")
#     mpiece_frames = filter_by('model', rt_sub, rt_full, 'w')
#     mpiece_full = mpiece_frames[0]
#     mpiece_sub = mpiece_frames[1]
#     #st.write(mpiece_sub)

#     st.subheader("Derivative Piece")
#     dpiece_frames = filter_by('derivative', mpiece_sub, mpiece_full, 'v')
#     dpiece_full = dpiece_frames[0]
#     dpiece_sub = dpiece_frames[1]
#     st.markdown('Resulting relationships:')
#     st.write(dpiece_sub)

    # view url via link

# st.subheader("Enter Relationship to View on CRIM Project")

# prefix = "https://crimproject.org/relationships/"
# int_val = st.text_input('Relationship Number')
# combined = prefix + int_val

# st.markdown(combined, unsafe_allow_html=True)

# st.subheader('Download Filtered Results as CSV')
# userinput_r = st.text_input('Name of file for download (must include ".csv")', key='4')
# if st.button('Download without type details', key='5'):
#     download_csv(dpiece_sub, userinput_r)
# st.write('or')
# if st.button('Download with type details', key='6'):
#     download_csv(dpiece_full, userinput_r)

# st.subheader("Graphical representation of result")
# showrtype = st.checkbox('By relationship type', value=False)
# showmpiece = st.checkbox('By model observation piece', value=False)
# showdpiece = st.checkbox('By derivative observation piece', value=False)
# if showrtype:
#     draw_rt_chart(dpiece_full)
# if showmpiece:
#     draw_chart("model", "countmpiece", dpiece_sub)
# if showdpiece:
#     draw_chart("derivative", "countdpiece", dpiece_sub)
