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


#main heading of the resource

st.header("CRIM Project Meta Data Viewer")

st.write("These tools assemble metadata for about 5000 observations and 2500 relationships in Citations: The Renaissance Imitation Mass.")
st.write("Visit the [CRIM Project](https://crimproject.org) and its [Members Pages] (https://sites.google.com/haverford.edu/crim-project/home).")
st.write("Use the __checkboxes at the left__ to view detailed and summary data.")
st.write("Use the __headings below__ to perform faceted searches in __Observations__ and __Relationships__.")
st.write("For __Observations__ you can begin with __Piece__ or __Musical Type__.")
st.write("For __Relationships__ you can begin with __Piece__ or __Relationship Type__.")
st.write("Other tools allow you to create __graphs and charts__ of data for each type and subtype in the CRIM Vocabularies")

# st.write("Also see the [Relationship Metadata Viewer] (https://crim-relationship-data-viewer.herokuapp.com/)")

# st.cache speeds things up by holding data in cache

@st.cache(allow_output_mutation=True)

# get the data function 
def get_data(link):
    data = requests.get(link).json()
    #df = pd.DataFrame(data)
    df = pd.json_normalize(data)
    return df 


df = get_data('http://crimproject.org/data/observations/')
df.rename(columns={'piece.piece_id':'piece_id',
                    'observer.name' : 'observer_name',
                    'piece.full_title' : 'title'}, inplace=True)

df_r = get_data('http://crimproject.org/data/relationships/')
df_r.rename(columns={'piece.piece_id':'piece_id',
                    'piece.full_title' : 'title',
                    'observer.name':'observer_name',
                    'model_observation.piece.piece_id':'model',
                    'model_observation.piece.full_title' : 'model_title',
                    'derivative_observation.piece.piece_id':'derivative',
                    'derivative_observation.piece.full_title' : 'derivative_title'}, inplace=True)

select_data = df[["id", "observer_name", "piece_id", "title", "musical_type"]]
select_data_r = df_r[['id', 'observer_name', 'model', 'model_title', 'derivative', 'derivative_title' , 'relationship_type']]


# Sidebar options for _all_ data of a particular type

st.sidebar.write('Use checkboxes below to see all data of a given category.  Advanced filtering can be performed in the main window.')

if st.sidebar.checkbox('Show All Metadata Fields'):
    st.subheader('All CRIM Observations with All Metadata')
    st.write(df)

if st.sidebar.checkbox('Show Selected Metadata:  Observer, Type'):
    st.subheader('Selected Metadata:  Observer, Type')
    st.write(select_data)

if st.sidebar.checkbox('Show Total Observations per Analyst'):
    st.subheader('Total Observations per Analyst')
    st.write(df['observer_name'].value_counts())  


if st.sidebar.checkbox('Show Total Observations per Musical Type'):
    st.subheader('Total Observations per Musical Type')
    st.write(df['musical_type'].value_counts())
  

# st.subheader("All Data and MEI Views")
# sa = st.text_input('Name of file for download (must include ".csv")')
# ## Button to download CSV of results 
# if st.button('Download Complete Dataset as CSV'):
#     #s = st.text_input('Enter text here')
#     tmp_download_link = download_link(df, sa, 'Click here to download your data!')
#     st.markdown(tmp_download_link, unsafe_allow_html=True)



def download_csv(origdf, filename):
    tmp_download_link = download_link(origdf, filename, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


def filter_by(filterer, select_data, full_data, key):
    options = select_data[filterer].unique().tolist()
    selected_options = st.multiselect('', options, key = key)
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
    #st.write(chart_data)
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
    cf_count = get_mt_count(origdf, 'mt_cf')
    sog_count = get_mt_count(origdf, 'mt_sog')
    csog_count = get_mt_count(origdf, 'mt_csog')
    cd_count = get_mt_count(origdf, 'mt_cd')
    fg_count = get_mt_count(origdf, 'mt_fg')
    id_count = get_mt_count(origdf, 'mt_id')
    nid_count = get_mt_count(origdf, 'mt_nid')
    pe_count = get_mt_count(origdf, 'mt_pe')
    cad_count = get_mt_count(origdf, 'mt_cad')
    int_count = get_mt_count(origdf, 'mt_int')
    hr_count = get_mt_count(origdf, 'mt_hr')

    mt_dict = {'types':['Cantus firmus', 'Soggetto', 'Counter-soggetto', 'Contrapuntal duo', 'Fuga', 'ID', 'NID', 'PEN', 'Cadence', 'Interval Patterns', 'Homorhythm'],
                'count': [cf_count, sog_count, csog_count, cd_count, fg_count, id_count, nid_count, pe_count, cad_count, int_count, hr_count ]}
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
    qt_count = get_mt_count(origdf, 'rt_q')
    tm_count = get_mt_count(origdf, 'rt_tm')
    tnm_count = get_mt_count(origdf, 'rt_tnm')
    om_count = get_mt_count(origdf, 'rt_om')
    nm_count = get_mt_count(origdf, 'rt_nm')

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
    

def get_subtype_count(origdf, mt, stname):
    subtype = (origdf['mt_' + mt + '_' + stname] == 1)
    subtype_count = origdf[subtype].shape[0]
    return int(subtype_count)

def get_cdtype_count(origdf, stname):
    subtype = (origdf['mt_cad_type'].isin(stname))
    subtype_count = origdf[subtype].shape[0]
    return int(subtype_count)

def get_mt_count(origdf, mtname):
    musicaltype = (origdf[mtname] == 1)
    musicaltype_count = origdf[musicaltype].shape[0]
    return int(musicaltype_count)

def get_subtype_charts(selected_type, origdf):
    if selected_type.lower() == "cadence":
        cd_chosen = (origdf['mt_cad'] == 1)
        cd_full = origdf[cd_chosen]
        #separate cd type chart (3 types and counts of each)
        cd_dict = {'mt_cad_type':['authentic','phrygian','plagal'],
                    'countcdtypes': [ 
                        get_cdtype_count(cd_full, ['authentic', 'Authentic']),
                        get_cdtype_count(cd_full, ['phrygian', 'Phrygian']),
                        get_cdtype_count(cd_full, ['plagal', 'Plagal']),
                    ]}
        df_cd = pd.DataFrame(data=cd_dict)
        chart_cd = alt.Chart(df_cd).mark_bar().encode(
            x = 'countcdtypes',
            y = 'mt_cad_type',
        )
        text_cd = chart_cd.mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            text = 'countcdtypes'
        )
        st.write(chart_cd+text_cd)

        draw_chart('mt_cad_tone', 'countcdtones', cd_full)
        
        st.write('Distribution plot for cadence type - hover over any point for information')
        cd_full_1 = cd_full.copy()
        cd_full_1['mt_cad_type'].replace({'Authentic':'authentic', 'Phrygian':'phrygian', 'Plagal':'plagal'}, inplace=True) 
        #distribution plot for type and tone
        color_plot = alt.Chart(cd_full_1).mark_circle(size=60).encode(
            x='piece_id',
            y='mt_cad_type',
            color='mt_cad_tone',
            tooltip=['id', 'observer_name', 'mt_cad_type', 'mt_cad_tone']
        )
        st.write(color_plot)



    if selected_type.lower() == "fuga":
        fg_chosen = (origdf['mt_fg'] == 1)
        fg_full = origdf[fg_chosen]
        fg_dict = {'Subtypes':['periodic', 'strict', 'flexed', 'sequential', 'inverted', 'retrograde'],
                    'count': [
                        get_subtype_count(fg_full, 'fg', 'periodic'), 
                        get_subtype_count(fg_full, 'fg', 'strict'), 
                        get_subtype_count(fg_full, 'fg', 'flexed'), 
                        get_subtype_count(fg_full, 'fg', 'sequential'), 
                        get_subtype_count(fg_full, 'fg', 'inverted'), 
                        get_subtype_count(fg_full, 'fg', 'retrograde'),
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
        pe_chosen = (origdf['mt_pe'] == 1)
        pe_full = origdf[pe_chosen]

        pe_dict = {'Subtypes':['strict', 'flexed melodic', 'flexed rhythmic', 'sequential', 'added entry', 'invertible'],
                    'count': [ 
                        get_subtype_count(pe_full, 'pe', 'strict'), 
                        get_subtype_count(pe_full, 'pe', 'flexed'), 
                        get_subtype_count(pe_full, 'pe', 'flt'),
                        get_subtype_count(pe_full, 'pe', 'sequential'), 
                        get_subtype_count(pe_full, 'pe', 'added'), 
                        get_subtype_count(pe_full, 'pe', 'invertible'), 
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
        id_chosen = (origdf['mt_id'] == 1)
        id_full = origdf[id_chosen]
    
        id_dict = {'Subtypes':['strict', 'flexed melodic', 'flexed rhythmic', 'invertible'],
                    'count': [ 
                        get_subtype_count(id_full, 'id', 'strict'), 
                        get_subtype_count(id_full, 'id', 'flexed'), 
                        get_subtype_count(id_full, 'id', 'flt'),
                        get_subtype_count(id_full, 'id', 'invertible'), 
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
        nid_chosen = (origdf['mt_nid'] == 1)
        nid_full = origdf[nid_chosen]

        nid_dict = {'Subtypes':['strict', 'flexed melodic', 'flexed rhythmic', 'invertible'],
                    'count': [ 
                        get_subtype_count(nid_full, 'nid', 'strict'), 
                        get_subtype_count(nid_full, 'nid', 'flexed'), 
                        get_subtype_count(nid_full, 'nid', 'flt'),
                        get_subtype_count(nid_full, 'nid', 'invertible'), 
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
        hr_chosen = (origdf['mt_hr'] == 1)
        hr_full = origdf[hr_chosen]

        hr_dict = {'Subtypes':['simple', 'staggered', 'sequential', 'fauxbourdon'],
                    'count': [ 
                        get_subtype_count(hr_full, 'hr', 'simple'), 
                        get_subtype_count(hr_full, 'hr', 'staggered'), 
                        get_subtype_count(hr_full, 'hr', 'sequential'),
                        get_subtype_count(hr_full, 'hr', 'fauxbourdon'), 
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



st.markdown("---")
st.header("OBSERVATION VIEWER")

order = st.radio("Select order to filter data: ", ('Piece then Musical Type', 'Musical Type then Piece'))
if (order == 'Piece then Musical Type'):
    #filter by piece
    st.subheader("Piece")
    piece_frames = filter_by("piece_id", select_data, df, 'a')
    piece_full = piece_frames[0]
    piece_sub = piece_frames[1]
    #st.write(piece_full)
    #st.write(piece_sub)

    #filter by type with or without piece
    st.subheader("Musical Type")
    mt_frames = filter_by('musical_type', piece_sub, piece_full, 'b')
    mt_full = mt_frames[0]
    mt_sub = mt_frames[1]
    st.markdown('Resulting observations:')
    #st.write(mt_full)
    st.write(mt_sub)

    # view url via link

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


    st.subheader("Graphical representation of result")
    showtype = st.checkbox('By musical type', value=False)
    showpiece = st.checkbox('By piece', value=False)
    if showtype:
        draw_mt_chart(mt_full)
    if showpiece:
        draw_chart("piece_id", "countpiece", mt_sub)
    
    showfiltered = st.checkbox('Show subtype charts for filtered results', value=False)
    if showfiltered:
        selected_types = mt_sub['musical_type'].unique().tolist()
        for mt in selected_types:
            if str(mt).lower() in ['cadence', 'fuga', 'periodic entry', 'imitative duo', 'non-imitative duo', 'homorythm']:
                st.write('Type: ' + str(mt))
                get_subtype_charts(mt, mt_full)

else:
    #filter by musical type
    st.subheader("Musical Type")
    mt_frames = filter_by('musical_type', select_data, df, 'z')
    mt_full = mt_frames[0]
    mt_sub = mt_frames[1]
    #st.write(mt_full)

    #filter by piece with or without musical type
    st.subheader("Piece")
    piece_frames = filter_by('piece', mt_sub, mt_full, 'y')
    piece_full = piece_frames[0]
    piece_sub = piece_frames[1]
    st.markdown('Resulting observations:')
    st.write(piece_sub)

    st.subheader('Download Filtered Results as CSV')
    userinput = st.text_input('Name of file for download (must include ".csv")', key='2')
    if st.button('Download without type details', key='9'):
        download_csv(piece_sub, userinput)
    st.write('or')
    if st.button('Download with type details', key='10'):
        download_csv(piece_full, userinput)

    st.subheader("Graphical representation of result")
    showtype = st.checkbox('By musical type', value=False)
    showpiece = st.checkbox('By piece', value=False)
    if showtype:
        draw_mt_chart(piece_full)
    if showpiece:
        draw_chart("piece", "countpiece", piece_sub)

    showfiltered = st.checkbox('Show subtype charts for filtered results', value=False)
    if showfiltered:
        selected_types = piece_sub['musical_type'].unique().tolist()
        for mt in selected_types:
            if str(mt).lower() in ['cadence', 'fuga', 'periodic entry', 'imitative duo', 'non-imitative duo', 'homorythm']:
                st.write('Type: ' + str(mt))
                get_subtype_charts(mt, piece_full)


st.markdown("---")
st.header("Subtype Charts All Data") 

showall = st.checkbox('Show subtype charts for all data', value=False)
if showall:
    type_options = ['Cadence', 'Fuga', 'Periodic Entry', 'Imitative Duo', 'Non-Imitative Duo', 'Homorythm']
    selected_type = st.radio('', type_options, key = 'g')
    get_subtype_charts(selected_type, df)


st.markdown("---")
st.header("RELATIONSHIP VIEWER")

order = st.radio("Select order to filter data: ", ('Pieces then Relationship Type', 'Relationship Type then Pieces'))
if (order == 'Pieces then Relationship Type'):
    #filter by pieces
    st.subheader("Model Piece")
    mpiece_frames = filter_by("model", select_data_r, df_r, 'c')
    mpiece_full = mpiece_frames[0]
    mpiece_sub = mpiece_frames[1]

    st.subheader("Derivative Piece")
    dpiece_frames = filter_by("derivative", mpiece_sub, mpiece_full, 'd')
    dpiece_full = dpiece_frames[0]
    dpiece_sub = dpiece_frames[1]

    #filter by type with or without pieces
    st.subheader("Relationship Type")
    rt_frames = filter_by('relationship_type', dpiece_sub, dpiece_full, 'e')
    rt_full = rt_frames[0]
    rt_sub = rt_frames[1]
    st.markdown('Resulting relationships:')
    #st.write(rt_full)
    st.write(rt_sub)

    st.subheader("Enter Relationship to View on CRIM Project")

    # view url via link

    prefix = "https://crimproject.org/relationships/" 
    int_val = st.text_input('Relationship Number')
    combined = prefix + int_val

    st.markdown(combined, unsafe_allow_html=True)

    st.subheader('Download Filtered Results as CSV')
    userinput_r = st.text_input('Name of file for download (must include ".csv")', key='3')
    if st.button('Download without type details', key='7'):
        download_csv(rt_sub, userinput_r)
    st.write('or')
    if st.button('Download with type details', key='8'):
        download_csv(rt_full, userinput_r)

    st.subheader("Graphical representation of result")
    showrtype = st.checkbox('By relationship type', value=False)
    showmpiece = st.checkbox('By model observation piece', value=False)
    showdpiece = st.checkbox('By derivative observation piece', value=False)
    if showrtype:
        draw_rt_chart(rt_full)
    
    if showmpiece:
        draw_chart("model", "countmpiece", rt_sub)
    if showdpiece:
        draw_chart("derivative", "countdpiece", rt_sub)

else:
    #filter by musical type
    st.subheader("Relationship Type")
    rt_frames = filter_by('relationship_type', select_data_r, df_r, 'x')
    rt_full = rt_frames[0]
    rt_sub = rt_frames[1]
    #st.write(rt_full)

    #filter by piece with or without musical type
    st.subheader("Model Piece")
    mpiece_frames = filter_by('model', rt_sub, rt_full, 'w')
    mpiece_full = mpiece_frames[0]
    mpiece_sub = mpiece_frames[1]
    #st.write(mpiece_sub)

    st.subheader("Derivative Piece")
    dpiece_frames = filter_by('derivative', mpiece_sub, mpiece_full, 'v')
    dpiece_full = dpiece_frames[0]
    dpiece_sub = dpiece_frames[1]
    st.markdown('Resulting relationships:')
    st.write(dpiece_sub)

    st.subheader('Download Filtered Results as CSV')
    userinput_r = st.text_input('Name of file for download (must include ".csv")', key='4')
    if st.button('Download without type details', key='5'):
        download_csv(dpiece_sub, userinput_r)
    st.write('or')
    if st.button('Download with type details', key='6'):
        download_csv(dpiece_full, userinput_r)

    st.subheader("Graphical representation of result")
    showrtype = st.checkbox('By relationship type', value=False)
    showmpiece = st.checkbox('By model observation piece', value=False)
    showdpiece = st.checkbox('By derivative observation piece', value=False)
    if showrtype:
        draw_rt_chart(dpiece_full)
    if showmpiece:
        draw_chart("model", "countmpiece", dpiece_sub)
    if showdpiece:
        draw_chart("derivative", "countdpiece", dpiece_sub)
    
    

