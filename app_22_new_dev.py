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
from streamlit import caching
# git+https://github.com/HCDigitalScholarship/intervals.git@main

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
def create_bar_chart(variable, count, color, data, condition, *selectors):
    # if type(data.iloc[0, :][variable]) != str:
    #     raise Exception("Label difficult to see!")

    observer_chart = alt.Chart(data).mark_bar().encode(
        y=variable,
        x=count,
        color=color,
        opacity=alt.condition(condition, alt.value(1), alt.value(0.2))
    ).add_selection(
        *selectors
    )
    return observer_chart


def create_heatmap(x, x2, y, color, data, heat_map_width, heat_map_height, selector_condition, *selectors, tooltip):
    # if type(data.iloc[0, :][y]) != str:
    #     raise Exception("Label difficult to see!")

    heatmap = alt.Chart(data).mark_bar().encode(
        x=x,
        x2=x2,
        y=y,
        color=color,
        opacity=alt.condition(selector_condition, alt.value(1), alt.value(0.2)),
        tooltip=tooltip
    ).properties(
        width=heat_map_width,
        height=heat_map_height
    ).add_selection(
        *selectors
    )

    return heatmap


def _process_ngrams_df_helper(ngrams_df, main_col):
    """
    The output from the getNgram is usually a table with
    four voices and ngram of notes properties (duration or
    pitch). This method stack this property onto one column
    and mark which voices they are from.
    :param ngrams_df: direct output from getNgram with 1 columns
    for each voices and ngrams of notes' properties.
    :param main_col: the name of the property
    :return: a dataframe with ['start', main_col, 'voice'] as columns
    """
    # copy to avoid changing original ngrams df
    ngrams_df = ngrams_df.copy()

    # add a start column containing offsets
    ngrams_df.index.name = "start"
    ngrams_df = ngrams_df.reset_index().melt(id_vars=["start"], value_name=main_col, var_name="voice")

    ngrams_df["start"] = ngrams_df["start"].astype(float)
    return ngrams_df


def process_ngrams_df(ngrams_df, ngrams_duration=None, selected_pattern=None, voices=None):
    """
    This method combines ngrams from all voices in different columns
    into one column and calculates the starts and end points of the
    patterns. It could also filter out specific voices or patterns
    for the users to analyze.

    :param ngrams_df: dataframe we got from getNgram in crim-interval
    :param ngrams_duration: if not None, simply output the offsets of the
    ngrams. If we have durations, calculate the end by adding the offsets and
    the durations.
    :param selected_pattern: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :return a new, processed dataframe with only desired patterns from desired voices
    combined into one column with start and end points
    """

    ngrams_df = _process_ngrams_df_helper(ngrams_df, 'pattern')
    if ngrams_duration is not None:
        ngrams_duration = _process_ngrams_df_helper(ngrams_duration, 'duration')
        ngrams_df['end'] = ngrams_df['start'] + ngrams_duration['duration']
    else:
        # make end=start+1 just to display offsets
        ngrams_df['end'] = ngrams_df['start'] + 1

    # filter according to voices and patterns (after computing durations for correct offsets)
    if voices:
        voice_condition = ngrams_df['voice'].isin(voices)
        ngrams_df = ngrams_df[voice_condition].dropna(how='all')

    if selected_pattern:
        pattern_condition = ngrams_df['pattern'].isin(selected_pattern)
        ngrams_df = ngrams_df[pattern_condition].dropna(how='all')

    return ngrams_df


def _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=800, heatmap_height=300):
    """
    Plot a heatmap for crim-intervals getNgram's processed output.
    :param ngrams_df: processed crim-intervals getNgram's output.
    :param selected_pattern: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """

    processed_ngrams_df = processed_ngrams_df.dropna(how='any')

    selector = alt.selection_multi(fields=['pattern'])

    # # turns patterns into string to make it easier to see
    # processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(lambda cell: ", ".join(str(item) for item in cell), na_action='ignore').copy()

    patterns_bar = create_bar_chart('pattern', 'count(pattern)', 'pattern', processed_ngrams_df, selector, selector)
    heatmap = create_heatmap('start', 'end', 'voice', 'pattern', processed_ngrams_df, heatmap_width, heatmap_height,
                             selector, selector, tooltip=['start', 'end', 'pattern'])
    return alt.vconcat(patterns_bar, heatmap)


def plot_ngrams_heatmap(ngrams_df, ngrams_duration=None, selected_patterns=[], voices=[], heatmap_width=800,
                        heatmap_height=300):
    """
    Plot a heatmap for crim-intervals getNgram's output.
    :param ngrams_df: crim-intervals getNgram's output
    :param ngrams_duration: if not None, rely on durations in the
    df to calculate the durations of the ngrams.
    :param selected_patterns: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """
    processed_ngrams_df = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration,
                                            selected_pattern=selected_patterns,
                                            voices=voices)
    return _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=heatmap_width, heatmap_height=heatmap_height)


def _from_ema_to_offsets(df, ema_column):
    """
    This method adds a columns of start and end measure of patterns into
    the relationship dataframe using the column with the ema address.

    :param df: dataframe containing relationships between patterns retrieved
    from CRIM relationship json
    :param ema_column: the name of the column storing ema address.
    :return: the processed dataframe with two new columns start and end
    """
    # retrieve the measures from ema address and create start and end in place
    df['locations'] = df[ema_column].str.split("/", n=1, expand=True)[0]
    df['locations'] = df['locations'].str.split(",")
    df = df.explode('locations')
    df[['start', 'end']] = df['locations'].str.split("-", expand=True).fillna(method='ffill')

    df['start'] = df['start'].astype(float)
    df['end'] = df['end'].astype(float)
    return df


def _process_crim_json_url(url_column):
    # remove 'data' from http://crimproject.org/data/observations/1/ or http://crimproject.org/data/relationships/5/
    url_column = url_column.map(lambda cell: cell.replace('data/', ''))
    return url_column


def plot_comparison_heatmap(df, ema_col, main_category='musical_type', other_category='observer.name', option=1,
                            heat_map_width=600, heat_map_height=300):
    """
    This method plots a chart for relationships/observations dataframe retrieved from their
    corresponding json files. This chart has two bar charts displaying the count of variables
    the users selected, and a heatmap displaying the locations of the relationship.
    :param df: relationships or observations dataframe
    :param ema_col: name of the ema column
    :param main_category: name of the main category for the first bar chart.
    The chart would be colored accordingly (default='musical_type').
    :param other_category: name of the other category for the zeroth bar chart.
    (default='observer.name')
    :param heat_map_width: the width of the final heatmap (default=800)
    :param heat_map_height: the height of the final heatmap (default =300)
    :return: a big chart containing two smaller bar chart and a heatmap
    """

    df = df.copy()  # create a deep copy of the selected observations to protect the original dataframe
    df = _from_ema_to_offsets(df, ema_col)

    # sort by id
    df.sort_values(by=main_category, inplace=True)

    df = _from_ema_to_offsets(df, ema_col)
    df['website_url'] = _process_crim_json_url(df['url'])

    df['id'] = df['id'].astype(str)

    # because altair doesn't work when the categories' names have periods,
    # a period is replaced with a hyphen.

    new_other_category = other_category.replace(".", "_")
    new_main_category = main_category.replace(".", "_")

    df.rename(columns={other_category: new_other_category, main_category: new_main_category}, inplace=True)

    other_selector = alt.selection_multi(fields=[new_other_category])
    main_selector = alt.selection_multi(fields=[new_main_category])

    other_category = new_other_category
    main_category = new_main_category

    bar1 = create_bar_chart(main_category, str('count(' + main_category + ')'), main_category, df,
                            other_selector | main_selector, main_selector)
    bar0 = create_bar_chart(other_category, str('count(' + other_category + ')'), main_category, df,
                            other_selector | main_selector, other_selector)

    heatmap = alt.Chart(df).mark_bar().encode(
        x='start',
        x2='end',
        y='id',
        href='website_url',
        color=main_category,
        opacity=alt.condition(other_selector | main_selector, alt.value(1), alt.value(0.2)),
        tooltip=['website_url', main_category, other_category, 'start', 'end', 'id']
    ).properties(
        width=heat_map_width,
        height=heat_map_height
    ).add_selection(
        main_selector
    ).interactive()

    chart = alt.vconcat(
        alt.hconcat(
            bar1,
            bar0
        ),
        heatmap
    )
# inserting url fix here
    # chart['usermeta'] = {
    # "embedOptions": {
    #     'loader': {'target': '_blank'}
    # }

    return chart


def _recognize_integers(num_str):
    if num_str[0] == '-':
        return num_str[1:].isdigit()
    else:
        return num_str.isdigit()


def _close_match_helper(cell):
    # process each cell into an interator of *floats* for easy comparisons
    if type(cell) == str:
        cell = cell.split(",")

    if _recognize_integers(cell[0]):
        cell = tuple(int(item) for item in cell)

    return cell


def _close_match(ngrams_df, key_pattern):
    ngrams_df['pattern'] = ngrams_df['pattern'].map(lambda cell: _close_match_helper(cell), na_action='ignore')
    # making sure that key pattern and other patterns are tuple of string or ints
    if not (type(ngrams_df.iloc[0, :]['pattern']) == type(key_pattern) == tuple
            or type(ngrams_df.iloc[0, :]['pattern'][0]) == type(key_pattern[0])):
        raise Exception("Input patterns and patterns inside dataframe aren't tuple of strings/ints")

    ngrams_df['score'] = ngrams_df['pattern'].map(
        lambda cell: 100 * textdistance.levenshtein.normalized_similarity(key_pattern, cell), na_action='ignore')
    return ngrams_df


def plot_close_match_heatmap(ngrams_df, key_pattern, ngrams_duration=None, selected_patterns=[], voices=[],
                             heatmap_width=800, heatmap_height=300):
    """
    Plot how closely the other vectors match a selected vector.
    Uses the Levenshtein distance.
    :param ngrams_df: crim-intervals getNgram's output
    :param key_pattern: a pattern the users selected to compare other patterns with (tuple of floats)
    :param selected_pattern: the specific other vectors the users selected
    :param ngrams_duration: if None, simply output the offsets. If the users input a
    list of durations, caculate the end by adding durations with offsets and
    display the end on the heatmap accordingly.
    :param selected_patterns: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """

    ngrams = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration, selected_pattern=selected_patterns,
                               voices=voices)
    ngrams.dropna(how='any',
                  inplace=True)  # only the pattern column can be NaN because all columns have starts (==offsets) and voices
    # calculate the score
    key_pattern = _close_match_helper(key_pattern)
    score_ngrams = _close_match(ngrams, key_pattern)

    slider = alt.binding_range(min=0, max=100, step=1, name='cutoff:')
    selector = alt.selection_single(name="SelectorName", fields=['cutoff'],
                                    bind=slider, init={'cutoff': 50})
    return create_heatmap('start', 'end', 'voice', 'score', score_ngrams, heatmap_width, heatmap_height,
                          alt.datum.score > selector.cutoff, selector, tooltip=['start', 'end', 'pattern', 'score'])


def generate_ngrams_and_duration(model, df, n=3, exclude=['Rest'],
                                 interval_settings=('d', True, True), offsets='first'):
    """
    This method accept a model and a dataframe with the melody or notes
    and rests and generate an ngram (in columnwise and unit=0 setting)
    and a corresponding duration ngram
    :param model: an Imported Piece object.
    :param df: dataframe containing consecutive notes.
    :param n: accept any positive integers and would output ngrams of the corresponding sizes
    can't handle the n=-1 option (refer to getNgrams documentation for more)
    :param exclude: (refer to getNgrams documentation)
    :param interval_settings: (refer to getNgrams documentation)
    :param offsets: (refer to getNgrams documentation)
    :return: ngram and corresponding duration dataframe!
    """
    if n == -1:
        raise Exception("Cannot calculate the duration for this type of ngrams")

    # compute dur for the ngrams
    dur = model.getDuration(df)
    dur = dur.reindex_like(df).applymap(str, na_action='ignore')
    # combine them and generate ngrams and duration at the same time
    notes_dur = pd.concat([df, dur])
    ngrams = model.getNgrams(df=df, n=n, exclude=exclude,
                             interval_settings=interval_settings, unit=0, offsets=offsets)
    dur_ngrams = model.getNgrams(df=dur, n=n, exclude=exclude,
                                 interval_settings=interval_settings, unit=0, offsets=offsets)
    dur_ngrams = dur_ngrams.reindex_like(ngrams)

    # sum up durations!
    dur_ngrams = dur_ngrams.applymap(lambda cell: sum([float(element) for element in cell]), na_action='ignore')

    return ngrams, dur_ngrams


# Network visualizations
def process_network_df(df, interval_column_name, ema_column_name):
    """
    Create a small dataframe containing network
    """
    result_df = pd.DataFrame()
    result_df[['piece.piece_id', 'url', interval_column_name]] = \
        df[['piece.piece_id', 'url', interval_column_name]].copy()
    result_df[['segments']] = \
        df[ema_column_name].astype(str).str.split("/", 1, expand=True)[0]
    result_df['segments'] = result_df['segments'].str.split(",")
    return result_df


# add nodes to graph
def create_interval_networks(interval_column, interval_type):
    """
    Helper method to create networks for observations' intervals
    :param interval_column: column containing the intervals users want to
    examine
    :param interval_type: 'melodic' or 'time'
    :return: a dictionary of networks describing the intervals
    """
    # dictionary maps the first time/melodic interval to its corresponding
    # network
    networks_dict = {'all': Network(directed=True, notebook=True)}
    interval_column = interval_column.astype(str)
    networks_dict['all'].add_node('all', color='red', shape='circle', level=0)

    # create nodes from the patterns
    for node in interval_column:
        # create nodes according to the interval types
        if interval_type == 'melodic':
            nodes = re.sub(r'([+-])(?!$)', r'\1,', node).split(",")
            separator = ''
        elif interval_type == 'time':
            nodes = node.split("/")
            separator = '/'
        else:
            raise Exception("Please put either 'time' or 'melodic' for `type_interval`")

        # nodes would be grouped according to the first interval
        group = nodes[0]

        if not group in networks_dict:
            networks_dict[group] = Network(directed=True, notebook=True)

        prev_node = 'all'
        for i in range(1, len(nodes)):
            node_id = separator.join(node for node in nodes[:i])
            # add to its own family network
            networks_dict[group].add_node(node_id, group=group, physics=False, level=i)
            if prev_node != "all":
                networks_dict[group].add_edge(prev_node, node_id)

            # add to the big network
            networks_dict['all'].add_node(node_id, group=group, physics=False, level=i)
            networks_dict['all'].add_edge(prev_node, node_id)
            prev_node = node_id

    return networks_dict


def _manipulate_processed_network_df(df, interval_column, search_pattern_starts_with):
    """
    This method helps to generate interactive widget in create_interactive_compare_df
    :param search_pattern_starts_with:
    :param df: the dataframe the user interact with
    :param interval_column: the column of intervals
    :return: A filtered and colored dataframe based on the option the user selected.
    """
    mask = df[interval_column].astype(str).str.startswith(pat=search_pattern_starts_with)
    filtered_df = df[mask].copy()
    return filtered_df.fillna("-").style.applymap(
        lambda x: "background: #ccebc5" if search_pattern_starts_with in x else "")


def create_interactive_compare_df(df, interval_column):
    """
    This method returns a wdiget allowing users to interact with
    the simple observations dataframe.
    :param df: the dataframe the user interact with
    :param interval_column: the column of intervals
    :return: a widget that filters and colors a dataframe based on the users
    search pattern.
    """
    return interact(_manipulate_processed_network_df, df=fixed(df),
                    interval_column=fixed(interval_column), search_pattern_starts_with='Input search pattern')


def create_comparisons_networks_and_interactive_df(df, interval_column, interval_type, ema_column, patterns=[]):
    """
    Generate a dictionary of networks and a simple dataframe allowing the users
    search through the intervals.
    :param df: the dataframe the user interact with
    :param interval_column: the column of intervals
    :param interval_type: put "time" or "melodic"
    :param ema_column: column containing ema address
    :param patterns: we could only choose to look at specific patterns (optional)
    :return: a dictionary of networks created and a clean interactive df
    """
    # process df
    if patterns:
        df = df[df[interval_column].isin(patterns)].copy()

    networks_dict = create_interval_networks(df[interval_column], interval_type)
    df = process_network_df(df, interval_column, ema_column)
    return networks_dict, create_interactive_compare_df(df, interval_column)

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

st.sidebar.write("Have you recently added Relationships to CRIM?  Refresh to view them")


if st.sidebar.button("Refresh Data from CRIM Project"):
    caching.clear_cache()
# st.cache speeds things up by holding data in cache

@st.cache(allow_output_mutation=True)

# get the data function
def get_data(link):
    data = requests.get(link).json()
    #df = pd.DataFrame(data)
    df = pd.json_normalize(data)
    return df


df = get_data('https://crimproject.org/data/observations')
# df = get_data('https://raw.githubusercontent.com/RichardFreedman/crim_data/main/test_data.json')
# df = requests.get('http://crimproject.org/data/observations/').json()

# df = get_data('https://raw.githubusercontent.com/CRIM-Project/CRIM-online/dev/crim/fixtures/migrated-crimdata/cleaned_observations.json')
df.rename(columns={'piece.piece_id':'piece_id',
                    'piece.full_title':'full_title',
                    'observer.name' : 'observer_name',
                    'details.entry intervals': 'entry_intervals',
                    'details.time intervals': 'time_intervals',
                    'details.voices': 'voices',
                    'details.voice': 'voice',
                    'details.periodic': 'periodic',
                    'details.regularity': 'regularity',
                    'details.sequential': 'sequential',
                    'details.inverted': 'inverted',
                    'details.retrograde': 'retrograde',
                    'details.invertible counterpoint': 'invertible_counterpoint',
                    'details.added entries': 'added_entries',
                    'details.ostinato': 'ostinato',
                    'details.type': 'type',
                    'details.dialogue':  'hr_dialogue',
                     'details.tone':  'cadence_tone',
                     'details.irregular cadence': 'irreg_cadence',
                     'details.features': 'features',
                     'details.dovetail cadence':  'dovetail',
                     'details.dovetail cadence voice':  'dovetail voice',
                     # 'details.dovetail voice name': 'dovetail_voice',
                     'details.dovetail position': 'dovetail_position',
                     'details.irregular roles': 'irregular_roles',

                     # 'details.cantizans': 'cantizans staff',
                     # 'details.tenorizans': 'tenorizans staff',
                    }, inplace=True)

# extract bar numbers from ema

df["measures"] = df['ema'].str.extract('(\d+-\d+)')



drop_list = ['url',
             'ema',
             'remarks',
            'curated',
            'created',
            'updated',
            'observer.url',
            'piece.url',
            'piece.mass',
            'details.voice name',
            'details.voice names',
            'details.voice name reg',
            'details.voice names reg',
            'definition.url',
            'definition.id',
            'definition.observation_definition',
            'details.cantizans name',
            'details.tenorizans name',
            'details.cantizans name reg',
            'details.tenorizans name reg',
            'details.dovetail voice name reg',
            'details.altizans',
            'details.bassizans',
            'details.cantizans',
            'details.tenorizans',
            # 'details.irregular roles'
            # 'details.dovetail cadence voice',
            'details.dovetail voice name',
             'voice',
             'details',
             'full_title',
            ]
df_clean = df.drop(columns=drop_list)

col_order = ['id',
 'piece_id',
 'full_title',
 'musical_type',
 'measures',
 'observer_name',
 'voices',
 'time_intervals',
 'entry_intervals',
 'added_entries',
 'regularity',
 'periodic',
 'inverted',
 'retrograde',
 'sequential',
 'invertible_counterpoint',
 'features',
 'ostinato',
 'type',
 'hr_dialogue',
 'cadence_tone',
 'irregular_roles',
 'dovetail',
 'dovetail_position',
 'irreg_cadence',
 'dovetail voice',
 ]

df_clean = df_clean.reindex(columns=col_order)



# st.write(df_clean)
df_r = get_data('https://crimproject.org/data/relationships')

df_view = df_r

# # df_r = get_data('https://raw.githubusercontent.com/CRIM-Project/CRIM-online/dev/crim/fixtures/migrated-crimdata/cleaned_relationships.json')

convert_dict_r = {'id': int,
               }

df = df.astype(convert_dict_r)

df_r.rename(columns={'observer.name':'observer_name',
                    'relationship_type': 'relationship_type',
                    'model_observation.id': 'model_observation',
                    'model_observation.piece.piece_id': 'model',
                    'model_observation.piece.full_title': 'model_title',
                    'derivative_observation.id': 'derivative_observation',
                    'derivative_observation.piece.piece_id': 'derivative',
                    'derivative_observation.piece.full_title':  'derivative_title',
                    'details.type': 'type',
                    'details.self': 'self',
                    'details.activity': 'activity',
                    'details.extent': 'extent',
                    'details.new counter subject': 'new_countersubject',
                    'details.sounding in different voices': "sounding_diff_voices",
                    'details.whole passage transposed': 'whole_passage_transposed',
                    'details.whole passage metrically shifted': 'whole_passage_shifted',
                    'details.melodically inverted': 'melodically_inverted',
                    'details.retrograde': 'retrograde',
                    'details.double or invertible counterpoint': 'invertible_counterpoint',
                    'details.old counter subject shifted metrically': 'old_cs_shifted',
                    'details.old counter subject transposed': 'old_cs_transposed',
                    'details.new combination': 'new_combination',
                    'details.metrically shifted': 'metrically_shifted',
                    'details.transposition': 'transposition',
                    'details.systematic diminution': 'diminution',
                    'details.systematic augmentation': 'augmentation',
                        }, inplace=True)

# df_r.rename(columns={'pk': 'id',
#                     'fields.observer':'observer_name',
#                     'fields.relationship_type': 'relationship_type',
#                     'fields.model_observation': 'model_observation',
#                     'fields.derivative_observation': 'derivative_observation',
#                     'fields.details.type': 'type',
#                     'fields.details.self': 'self',
#                     'fields.details.activity': 'activity',
#                     'fields.details.extent': 'extent',
#                     'fields.details.new counter subject': 'new_countersubject',
#                     'fields.details.sounding in different voices': "sounding_diff_voices",
#                     'fields.details.whole passage transposed': 'whole_passage_transposed',
#                     'fields.details.whole passage metrically shifted': 'whole_passage_shifted',
#                     'fields.details.melodically inverted': 'melodically_inverted',
#                     'fields.details.retrograde': 'retrograde',
#                     'fields.details.double or invertible counterpoint': 'invertible_counterpoint',
#                     'fields.details.old counter subject shifted metrically': 'old_cs_shifted',
#                     'fields.details.old counter subject transposed': 'old_cs_transposed',
#                     'fields.details.new combination': 'new_combination',
#                     'fields.details.metrically shifted': 'metrically_shifted',
#                     'fields.details.transposition': 'transposition',
#                     'fields.details.systematic diminution': 'diminution',
#                     'fields.details.systematic augmentation': 'augmentation',
#                         }, inplace=True)

r_drop_list = ['url',
               'musical_type',
               'curated',
               'created',
               'updated',
               'remarks',
               'observer.url',
               'observer',
               'model_observation.url',
               'model_observation.piece.url',
               # 'model_observation.piece.full_title',
               'model_observation.ema',
               'derivative_observation.url',
               'derivative_observation.piece.url',
               # 'derivative_observation.piece.full_title',
               'derivative_observation.ema',
                'definition.url',
                'definition.id',
                'definition.relationship_definition',
               ]


df_r_clean = df_r.drop(columns=r_drop_list)

select_data = df[["id", "observer_name", "piece_id", "full_title", "musical_type", 'measures']]

#  adds piece_ids and musical_types back into relationship dataframe
# first:  the relevant data from the obs df:
df_short = df[['id', 'full_title', 'piece_id', 'musical_type']]
#
# now a pair of merges based on intersectino of obs ids in the two dfs:
dfs_combined = pd.merge(df_r_clean,
                     df_short,
                     left_on='model_observation',
                     right_on='id',
                     how='outer')
dfs_combined2 = pd.merge(dfs_combined,
                     df_short,
                     left_on='derivative_observation',
                     right_on='id',
                     how='outer')
# drop redundant columns
dfs_combined2.drop(columns=['piece_id_x', 'piece_id_y', 'id_y', 'id'], inplace=True)
# rename the new columns
dfs_combined2.rename(columns={'id_x': 'id',
                           'musical_type_x': 'model_musical_type',
                           'musical_type_y': 'derivative_musical_type'}, inplace=True)
col_order_rels = ['id',
                    'relationship_type',
                    'observer_name',
                    'model_observation',
                    'model',
                    'model_title',
                    'model_musical_type',
                    'derivative_observation',
                    'derivative',
                    'derivative_title',
                    'derivative_musical_type',
                    'activity',
                    'extent',
                    'self',
                    'type',
                    'retrograde',
                    'new_combination',
                    'new_countersubject',
                    'melodically_inverted',
                    'metrically_shifted',
                    'whole_passage_transposed',
                    'whole_passage_shifted',
                    'sounding_diff_voices',
                    'transposition',
                    'old_cs_transposed',
                    'old_cs_shifted',
                    'invertible_counterpoint',
                    'diminution',
                    'augmentation',
                    'details',
                    ]

dfs_combined2 = dfs_combined2.reindex(columns=col_order_rels)


df_r_with_obs = dfs_combined2

# st.write(df_r_with_obs)

select_data_r = df_r_with_obs[['id',
                              'observer_name',
                              'relationship_type',
                              'model_observation',
                              'derivative_observation',
                              'model',
                              'model_title',
                              'derivative',
                              'derivative_title',
                              'model_musical_type',
                              'derivative_musical_type',]]


# Sidebar options for _all_ data of a particular type
st.sidebar.write('View Heatmaps')
if st.sidebar.checkbox('Viewheatmaps'):
    pieceID = "CRIM_Model_0008"
    df_relationships_test = df_view[df_view['model'] == pieceID].copy()

    st.write(plot_comparison_heatmap(df_relationships_test, 'model_observation.ema', main_category='relationship_type', other_category='observer.name', heat_map_width=800, heat_map_height=300))



st.sidebar.write('Use buttons and checkboxes below to view or filter all data of a given category.')
st.sidebar.header("Observation Tables and Charts")
if st.sidebar.checkbox('Select Observation Tables and Charts'):
    st.markdown("---")
    st.header("Observations")
    if st.sidebar.checkbox('All Observation Metadata Fields'):
        st.subheader('All CRIM Observations with All Metadata')
        st.write(df_clean)

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

    st.subheader("Enter Observation to View on CRIM Project")

    prefix = "https://crimproject.org/observations/"
    int_val = st.text_input('Observation Number')
    combined = prefix + int_val

    st.markdown(combined, unsafe_allow_html=True)
    st.sidebar.markdown("---")

#  Filter views There

st.sidebar.header("Filter Observations")
if st.sidebar.checkbox('Select Observations'):
   st.sidebar.subheader("The order of filtering matters!")
   st.sidebar.write("You can begin by selecting pieces, then filter by type; or the reverse.")
   st.markdown("---")


# from linh:

    # from LINH
   order = st.sidebar.radio("Select order to filter data: ", ('Piece > Musical Type', 'Musical Type > Piece'))
   if (order == 'Piece > Musical Type'):
        #filter by piece
        st.sidebar.subheader("Filter by piece")
        # pieceo_frames = filter_by("piece_id", select_data, df, 'a')
        # pieceo_frames = filter_by("piece_id", select_data, df_clean, 'a')
        pieceo_frames = filter_by("full_title", select_data, df_clean, 'a')
        pieceo_full = pieceo_frames[0]
        pieceo_sub = pieceo_frames[1]
        #st.write(piece_full)
        #st.write(piece_sub)

        #filter by type with or without piece
        st.sidebar.subheader("Then filter by musical type")
        mto_frames = filter_by('musical_type', pieceo_sub, pieceo_full, 'b')
        mto_full = mto_frames[0]
        mto_sub = mto_frames[1]
        # mt_drop_cols = mt_full.drop(columns=drop_list)
        # st.subheader("Filtered Observations")
        # st.write(mto_full)

        st.sidebar.subheader("Then filter by person")
        pso_frames = filter_by('observer_name', mto_sub, mto_full, 'c')
        pso_full = pso_frames[0]
        pso_sub = pso_frames[1]
        # ps_drop_cols = ps_full.drop(columns=drop_list)
        st.subheader("Filtered Observations")
        st.write(pso_sub)


        showfiltered = st.sidebar.checkbox('Show subtype charts for filtered results', value=False)
        if showfiltered:
# Cantus firmus chart_rt
            if mto_sub['musical_type'].isin(['cantus firmus']).any():
               cf_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    pso_full['features'].isin(['both pitches and durations']).sum(),
                    pso_full['features'].isin(['pitches only']).sum(),
                    pso_full['features'].isin(['durations only']).sum(),
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
            if mto_sub['musical_type'].isin(['soggetto']).any():
               sg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    pso_full['features'].isin(['both pitches and durations']).sum(),
                    pso_full['features'].isin(['pitches only']).sum(),
                    pso_full['features'].isin(['durations only']).sum(),
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
            if mto_sub['musical_type'].isin(['counter soggetto']).any():
               csg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    pso_full['features'].isin(['both pitches and durations']).sum(),
                    pso_full['features'].isin(['pitches only']).sum(),
                    pso_full['features'].isin(['durations only']).sum(),
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
            if mto_sub['musical_type'].isin(['contrapuntal duo']).any():
               cd_dict = {'Subtypes':['contrapuntal duos'],
               'count': [
                    pso_full['musical_type'].isin(['contrapuntal duo']).sum(),

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
            if mto_sub['musical_type'].isin(['fuga']).any():
                fg_dict = {'Subtypes':['periodic', 'sequential', 'inverted', 'retrograde'],
                'count': [
                    pso_full['periodic'].sum(),
                    pso_full['sequential'].sum(),
                    pso_full['inverted'].sum(),
                    pso_full['retrograde'].sum(),
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
            if mto_sub['musical_type'].isin(['periodic entry']).any():
                pe_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                pso_full['sequential'].sum(),
                                pso_full['invertible_counterpoint'].sum(),
                                pso_full['added_entries'].sum(),
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
            if mto_sub['musical_type'].isin(['imitative duo']).any():

                id_dict = {'Subtypes':['invertible counterpoint', 'added entries'],
                            'count': [
                                pso_full['invertible_counterpoint'].sum(),
                                pso_full['added_entries'].sum(),
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
            if mto_sub['musical_type'].isin(['non-imitative duo']).any():

                nim_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                pso_full['sequential'].sum(),
                                pso_full['invertible_counterpoint'].sum(),
                                pso_full['added_entries'].sum(),
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
            if mto_sub['musical_type'].isin(['homorhythm']).any():
                hr_dict = {'Subtypes':['simple', 'staggered', 'sequential', 'fauxbourdon'],
                            'count': [
                                pso_full['type'].isin(['simple']).sum(),
                                pso_full['type'].isin(['staggered']).sum(),
                                pso_full['type'].isin(['sequential']).sum(),
                                pso_full['type'].isin(['fauxbourdon']).sum(),
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
            if mto_sub['musical_type'].isin(['cadence']).any():
                cd_dict = {'Cadence Type':['authentic','phrygian','plagal'],
                            'countcdtypes': [
                                pso_full['type'].isin(['authentic']).sum(),
                                pso_full['type'].isin(['phrygian']).sum(),
                                pso_full['type'].isin(['plagal']).sum(),
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
            if mto_sub['musical_type'].isin(['cadence']).any():
                ct_dict = {'Cadence Tone':['C','D','E-flat', 'E', 'F', 'G', 'A', 'B-flat', 'B'],
                            'countcdtones': [
                                pso_full['cadence_tone'].isin(['C']).sum(),
                                pso_full['cadence_tone'].isin(['D']).sum(),
                                pso_full['cadence_tone'].isin(['E_flat']).sum(),
                                pso_full['cadence_tone'].isin(['E']).sum(),
                                pso_full['cadence_tone'].isin(['F']).sum(),
                                pso_full['cadence_tone'].isin(['G']).sum(),
                                pso_full['cadence_tone'].isin(['A']).sum(),
                                pso_full['cadence_tone'].isin(['B_flat']).sum(),
                                pso_full['cadence_tone'].isin(['B']).sum(),
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
        int_val = st.text_input('Enter Observation Number')
        combined = prefix + int_val

        st.markdown(combined, unsafe_allow_html=True)

        st.subheader('Download Filtered Observations as CSV')
        userinput = st.text_input('Name of file for download (must include ".csv")', key='z')
        if st.button('Download without type details', key='11'):
            download_csv(pso_sub, userinput)
        st.write('or')
        if st.button('Download with type details', key='12'):
            download_csv(pso_full, userinput)


   else:
    #filter by musical type
    #filter by type with or without piece

        st.sidebar.subheader("Filter by Musical Type")
        mto_frames = filter_by('musical_type', select_data, df_clean, 'd')
        # mto_frames = filter_by('musical_type', select_data, df, 'd')
        mto_full = mto_frames[0]
        mto_sub = mto_frames[1]
        #st.write(mt_full)

        #filter by piece with or without musical type
        st.sidebar.subheader("Then Filter by Piece")
        # pieceo_frames = filter_by('piece_id', mto_sub, mto_full, 'e')
        pieceo_frames = filter_by('full_title', mto_sub, mto_full, 'e')
        pieceo_full = pieceo_frames[0]
        pieceo_sub = pieceo_frames[1]
        # piece_drop_cols = piece_full.drop(columns=drop_list)
        # st.subheader('Filtered Observations')
        # st.write(piece_drop_cols)

        st.sidebar.subheader("Then filter by person")
        pso_frames = filter_by('observer_name', pieceo_sub, pieceo_full, 'f')
        pso_full = pso_frames[0]
        pso_sub = pso_frames[1]

        # ps_drop_cols = ps_full.drop(columns=drop_list)
        st.subheader("Filtered Observations")
        st.write(pso_full)
    # view url via link
        showfiltered = st.sidebar.checkbox('Show subtype charts for filtered results', value=False)
        if showfiltered:
# Cantus firmus chart_rt
            if pieceo_sub['musical_type'].isin(['cantus firmus']).any():
               cf_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    pso_full['features'].isin(['both pitches and durations']).sum(),
                    pso_full['features'].isin(['pitches only']).sum(),
                    pso_full['features'].isin(['durations only']).sum(),
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
            if pieceo_sub['musical_type'].isin(['soggetto']).any():
               sg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    pso_full['features'].isin(['both pitches and durations']).sum(),
                    pso_full['features'].isin(['pitches only']).sum(),
                    pso_full['features'].isin(['durations only']).sum(),
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
            if pieceo_sub['musical_type'].isin(['counter soggetto']).any():
               csg_dict = {'Subtypes':['both pitches and durations', 'pitches only', 'durations only'],
               'count': [
                    pso_full['features'].isin(['both pitches and durations']).sum(),
                    pso_full['features'].isin(['pitches only']).sum(),
                    pso_full['features'].isin(['durations only']).sum(),
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
            if pieceo_sub['musical_type'].isin(['contrapuntal duo']).any():
               cd_dict = {'Subtypes':['contrapuntal duos'],
               'count': [
                    pso_full['musical_type'].isin(['contrapuntal duo']).sum(),

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
            if pieceo_sub['musical_type'].isin(['fuga']).any():
                fg_dict = {'Subtypes':['periodic', 'sequential', 'inverted', 'retrograde'],
                'count': [
                    pso_full['periodic'].sum(),
                    pso_full['sequential'].sum(),
                    pso_full['inverted'].sum(),
                    pso_full['retrograde'].sum(),
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
            if pieceo_sub['musical_type'].isin(['periodic entry']).any():
                pe_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                pso_full['sequential'].sum(),
                                pso_full['invertible_counterpoint'].sum(),
                                pso_full['added_entries'].sum(),
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
            if pieceo_sub['musical_type'].isin(['imitative duo']).any():

                id_dict = {'Subtypes':['invertible counterpoint', 'added entries'],
                            'count': [
                                pso_full['invertible_counterpoint'].sum(),
                                pso_full['added_entries'].sum(),
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
            if pieceo_sub['musical_type'].isin(['non-imitative duo']).any():

                nim_dict = {'Subtypes':['sequential', 'invertible counterpoint', 'added entries'],
                            'count': [
                                pso_full['sequential'].sum(),
                                pso_full['invertible_counterpoint'].sum(),
                                pso_full['added_entries'].sum(),
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
            if pieceo_sub['musical_type'].isin(['homorhythm']).any():
                hr_dict = {'Subtypes':['simple', 'staggered', 'sequential', 'fauxbourdon'],
                            'count': [
                                pso_full['type'].isin(['simple']).sum(),
                                pso_full['type'].isin(['staggered']).sum(),
                                pso_full['type'].isin(['sequential']).sum(),
                                pso_full['type'].isin(['fauxbourdon']).sum(),
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
            if pieceo_sub['musical_type'].isin(['cadence']).any():
                cd_dict = {'Cadence Type':['authentic','phrygian','plagal'],
                            'countcdtypes': [
                                pso_full['type'].isin(['authentic']).sum(),
                                pso_full['type'].isin(['phrygian']).sum(),
                                pso_full['type'].isin(['plagal']).sum(),
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
            if pieceo_sub['musical_type'].isin(['cadence']).any():
                ct_dict = {'Cadence Tone':['C','D','E-flat', 'E', 'F', 'G', 'A', 'B-flat', 'B'],
                            'countcdtones': [
                                pso_full['cadence_tone'].isin(['C']).sum(),
                                pso_full['cadence_tone'].isin(['D']).sum(),
                                pso_full['cadence_tone'].isin(['E_flat']).sum(),
                                pso_full['cadence_tone'].isin(['E']).sum(),
                                pso_full['cadence_tone'].isin(['F']).sum(),
                                pso_full['cadence_tone'].isin(['G']).sum(),
                                pso_full['cadence_tone'].isin(['A']).sum(),
                                pso_full['cadence_tone'].isin(['B_flat']).sum(),
                                pso_full['cadence_tone'].isin(['B']).sum(),
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

# THIS IS OK
        st.subheader("Enter Observation to View on CRIM Project")

        prefix = "https://crimproject.org/observations/"
        int_val = st.text_input(' Observation Number')
        combined = prefix + int_val

        st.markdown(combined, unsafe_allow_html=True)

        st.subheader('Download Filtered Observations as CSV')
        userinput = st.text_input('Name of file for download (must include ".csv")', key='2')
        if st.button('Download without type details', key='9'):
            download_csv(pso_sub, userinput)
        st.write('or')
        if st.button('Download with type details', key='10'):
            download_csv(pso_full, userinput)




st.sidebar.markdown("---")
st.sidebar.header("Relationship Tables and Charts")

if st.sidebar.checkbox('Select Relationship Tables and Charts'):
    st.markdown("---")
    st.header("Relationships")
    if st.sidebar.checkbox('All Relationship Metadata Fields'):
        st.subheader('All Relationship Metadata Fields')
        st.write(df_r_clean)

    if st.sidebar.checkbox('Observer, Relationship Type, Model, Derivative'):
        st.subheader('Selected Metadata:  Observer, Relationship Type, Model Observation ID, Derivative Observation ID')
        st.write(select_data_r)

    if st.sidebar.checkbox('Relationships by Analyst'):
        st.subheader('Total Relationships by Analyst')
        st.write(df_r['observer_name'].value_counts())

    if st.sidebar.checkbox('Relationships by Type'):
        st.subheader('Total Relationships by Type')
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
          exact = df_r['type'].str.match('exact')
          monnayage = df_r['type'].str.match('monnayage')
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

      if st.checkbox('Mechanical Transformation Types'):
          st.subheader("Mechanical Transformation Types")
      # Mechanical Trans Chart
      #  later add diminution and augmentation once these are in the JSON
      # add kind of transposition (as three types?)
          sound_diff = df_r['relationship_type'].str.match('mechanical transformation') & df_r['sounding_diff_voices']
          melodically_inverted = df_r['relationship_type'].str.match('mechanical transformation') & df_r['melodically_inverted']
          retrograde = df_r['relationship_type'].str.match('mechanical transformation') & df_r['retrograde']
          metrically_shifted = df_r['relationship_type'].str.match('mechanical transformation') & df_r['metrically_shifted']
          double_cpt = df_r['relationship_type'].str.match('mechanical transformation') & df_r['invertible_counterpoint']
          diminution = df_r['relationship_type'].str.match('mechanical transformation') & df_r['diminution']
          augmentation = df_r['relationship_type'].str.match('mechanical transformation') & df_r['augmentation']

          # diminution = df_r['fields.details.systematic diminution']
          # augmentation = df_r['fields.details.systematic augmentation']
          rl_mt_dict = {'Mechanical Transformation Subtype':['sounding in different voices','melodically inverted',
          'retrograde','metrically shifted', 'invertible counterpoint', 'diminution', 'augmentation'],
                      'countrltypes': [
                          sound_diff.sum(),
                          melodically_inverted.sum(),
                          retrograde.sum(),
                          metrically_shifted.sum(),
                          double_cpt.sum(),
                          diminution.sum(),
                          augmentation.sum()
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

      if st.checkbox('Non-Mechanical Transformation Types'):
          st.subheader("Non-Mechanical Transformation Types")
          # Non Mechanical Trans Chart
          sound_diff = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['sounding_diff_voices']
          melodically_inverted = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['melodically_inverted']
          retrograde = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['retrograde']
          metrically_shifted = df_r['relationship_type'].str.match('non-mechanical transformation') &  df_r['whole_passage_shifted']
          transposed =  df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['whole_passage_transposed']
          new_cs = df_r['relationship_type'].str.match('non-mechanical transformation') &  df_r['new_countersubject']
          old_cs_tr = df_r['relationship_type'].str.match('non-mechanical transformation') &  df_r['old_cs_transposed']
          old_cs_ms = df_r['relationship_type'].str.match('non-mechanical transformation') &  df_r['old_cs_shifted']
          new_comb = df_r['relationship_type'].str.match('non-mechanical transformation') &  df_r['new_combination']
          double_cpt = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['invertible_counterpoint']
          diminution = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['diminution']
          augmentation = df_r['relationship_type'].str.match('non-mechanical transformation') & df_r['augmentation']


          rl_nmt_dict = {'Non-Mechanical Transformation Subtype':['sounding in different voices','melodically inverted', 'retrograde',
          'metrically shifted', 'transposed', 'new counter subject', 'old counter subject transposed', 'old counter subject shifted metrically'
          , 'new combination', 'diminution', 'augmentation'],
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
                          diminution.sum(),
                          augmentation.sum(),
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



    st.subheader("Enter Relationship to View on CRIM Project")

    prefix = "https://crimproject.org/relationships/"
    int_val = st.text_input('Relationship Number')
    combined = prefix + int_val

    st.markdown(combined, unsafe_allow_html=True)

    st.subheader("Download All Relationship Data")
    sa = st.text_input('Name of file for download (must include ".csv")')
   ## Button to download CSV of results
    if st.button('Download Complete Dataset as CSV'):
       #s = st.text_input('Enter text here')
       tmp_download_link = download_link(df, sa, 'Click here to download your data!')
       st.markdown(tmp_download_link, unsafe_allow_html=True)





st.sidebar.header("Filter Relationships")
if st.sidebar.checkbox('Show Filter Menus'):
   st.sidebar.subheader("The order of filtering matters!")
   st.sidebar.write("You can begin by selecting pieces first, then filter by relationship type; or the reverse.")
   st.markdown("---")

   order = st.sidebar.radio("Select order to filter data: ", ('Piece > Relationship', 'Relationship > Piece'))
   if (order == 'Piece > Relationship'):
       # filter by pieces
       st.sidebar.subheader("Select Model Piece")
       # mpiece_frames = filter_by("model", select_data_r, df_r_with_obs, 'g')
       mpiece_frames = filter_by("model_title", select_data_r, df_r_with_obs, 'g')
       mpiece_full = mpiece_frames[0]
       mpiece_sub = mpiece_frames[1]

       st.sidebar.subheader("Then Select Derivative Piece")
       # dpiece_frames = filter_by("derivative", mpiece_sub, mpiece_full, 'h')
       dpiece_frames = filter_by("derivative_title", mpiece_sub, mpiece_full, 'h')
       dpiece_full = dpiece_frames[0]
       dpiece_sub = dpiece_frames[1]
       # st.write(dpiece_full)

       st.sidebar.subheader("Then Select Relationship Type")
       rt_frames = filter_by('relationship_type', dpiece_sub, dpiece_full, 'i')
       rt_full = rt_frames[0]
       rt_sub = rt_frames[1]
       # st.subheader("Filtered Relationships")
       # st.write(rt_full)

       st.sidebar.subheader("Then filter by person")
       ps_frames = filter_by('observer_name', rt_sub, rt_full, 'k')
       ps_full = ps_frames[0]
       ps_sub = ps_frames[1]
       # ps_drop_cols = ps_full.drop(columns=drop_list)
       st.subheader("Filtered Relationships")
       st.write(ps_full)

       if ps_full['relationship_type'].isin(['quotation']).any():
          st.subheader("Quotation Sub-types in Filtered Relationships")

          exact = ps_full['type'].str.match('exact')
          monnayage = ps_full['type'].str.match('monnayage')
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



       if ps_full['relationship_type'].isin(['mechanical transformation']).any():
            st.subheader("Mechanical Transformation Sub-types in Filtered Relationships")


            sound_diff = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['sounding_diff_voices']
            melodically_inverted = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['melodically_inverted']
            retrograde = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['retrograde']
            metrically_shifted = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['metrically_shifted']
            double_cpt = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['invertible_counterpoint']
            diminution = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['diminution']
            augmentation = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['augmentation']

            # diminution = ps_full['fields.details.systematic diminution']
            # augmentation = ps_full['fields.details.systematic augmentation']
            rl_mt_dict = {'Mechanical Transformation Subtype':['sounding in different voices','melodically inverted',
            'retrograde','metrically shifted', 'invertible counterpoint', 'diminution', 'augmentation'],
                       'countrltypes': [
                           sound_diff.sum(),
                           melodically_inverted.sum(),
                           retrograde.sum(),
                           metrically_shifted.sum(),
                           double_cpt.sum(),
                           diminution.sum(),
                           augmentation.sum()
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

       if ps_full['relationship_type'].isin(['non-mechanical transformation']).any():
            st.subheader("Non-Mechanical Transformation Sub-types in Filtered Relationships")
            # Non Mechanical Trans Chart
            sound_diff = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['sounding_diff_voices']
            melodically_inverted = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['melodically_inverted']
            retrograde = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['retrograde']
            metrically_shifted = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['whole_passage_shifted']
            transposed =  ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['whole_passage_transposed']
            new_cs = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['new_countersubject']
            old_cs_tr = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['old_cs_transposed']
            old_cs_ms = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['old_cs_shifted']
            new_comb = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['new_combination']
            double_cpt = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['invertible_counterpoint']
            diminution = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['diminution']
            augmentation = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['augmentation']


            rl_nmt_dict = {'Non-Mechanical Transformation Subtype':['sounding in different voices','melodically inverted', 'retrograde',
            'metrically shifted', 'transposed', 'new counter subject', 'old counter subject transposed', 'old counter subject shifted metrically'
            , 'new combination', 'diminution', 'augmentation'],
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
                           diminution.sum(),
                           augmentation.sum(),
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

       st.subheader("Enter Relationship to View on CRIM Project")

       prefix = "https://crimproject.org/relationships/"
       int_val = st.text_input('Relationship Number')
       combined = prefix + int_val

       st.markdown(combined, unsafe_allow_html=True)

      # downloaded
       st.subheader('Download Filtered Relationships as CSV')
       userinput = st.text_input('Name of file for download (must include ".csv")', key='y')
       if st.button('Download without type details', key='m'):
           download_csv(ps_sub, userinput)
       st.write('or')
       if st.button('Download with type details', key='n'):
           download_csv(ps_full, userinput)

       #filter by type with or without pieces
   else:
       #filter by musical type
       st.sidebar.subheader("Select Relationship Type")
       rt_frames = filter_by('relationship_type', select_data_r, df_r_with_obs, 'o')
       rt_full = rt_frames[0]
       rt_sub = rt_frames[1]
       # st.write(rt_full)

       #filter by piece with or without musical type
       st.sidebar.subheader("Then Select Model Piece")
       # mpiece_frames = filter_by('model', rt_sub, rt_full, 'p')
       mpiece_frames = filter_by('model_title', rt_sub, rt_full, 'p')
       mpiece_full = mpiece_frames[0]
       mpiece_sub = mpiece_frames[1]
       # st.write(mpiece_sub)

       st.sidebar.subheader("Then Select Derivative Piece")
       # dpiece_frames = filter_by('derivative', mpiece_sub, mpiece_full, 'q')
       dpiece_frames = filter_by('derivative_title', mpiece_sub, mpiece_full, 'q')
       dpiece_full = dpiece_frames[0]
       dpiece_sub = dpiece_frames[1]
       # st.subheader("Filtered Relationships")
       # st.write(dpiece_full)

       st.sidebar.subheader("Then filter by person")
       ps_frames = filter_by('observer_name', dpiece_sub, dpiece_full, 'r')
       ps_full = ps_frames[0]
       ps_sub = ps_frames[1]
       # ps_drop_cols = ps_full.drop(columns=drop_list)
       st.subheader("Filtered Relationships")
       st.write(ps_full)
# adding subtypes

       if ps_full['relationship_type'].isin(['quotation']).any():
          st.subheader("Quotation Sub-types in Filtered Relationships")

          exact = ps_full['type'].str.match('exact')
          monnayage = ps_full['type'].str.match('monnayage')
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



       if ps_full['relationship_type'].isin(['mechanical transformation']).any():
            st.subheader("Mechanical Transformation Sub-types in Filtered Relationships")


            sound_diff = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['sounding_diff_voices']
            melodically_inverted = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['melodically_inverted']
            retrograde = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['retrograde']
            metrically_shifted = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['metrically_shifted']
            double_cpt = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['invertible_counterpoint']
            diminution = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['diminution']
            augmentation = ps_full['relationship_type'].str.match('mechanical transformation') & ps_full['augmentation']

            # diminution = ps_full['fields.details.systematic diminution']
            # augmentation = ps_full['fields.details.systematic augmentation']
            rl_mt_dict = {'Mechanical Transformation Subtype':['sounding in different voices','melodically inverted',
            'retrograde','metrically shifted', 'invertible counterpoint', 'diminution', 'augmentation'],
                       'countrltypes': [
                           sound_diff.sum(),
                           melodically_inverted.sum(),
                           retrograde.sum(),
                           metrically_shifted.sum(),
                           double_cpt.sum(),
                           diminution.sum(),
                           augmentation.sum()
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

       if ps_full['relationship_type'].isin(['non-mechanical transformation']).any():
            st.subheader("Non-Mechanical Transformation Sub-types in Filtered Relationships")
            # Non Mechanical Trans Chart
            sound_diff = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['sounding_diff_voices']
            melodically_inverted = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['melodically_inverted']
            retrograde = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['retrograde']
            metrically_shifted = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['whole_passage_shifted']
            transposed =  ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['whole_passage_transposed']
            new_cs = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['new_countersubject']
            old_cs_tr = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['old_cs_transposed']
            old_cs_ms = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['old_cs_shifted']
            new_comb = ps_full['relationship_type'].str.match('non-mechanical transformation') &  ps_full['new_combination']
            double_cpt = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['invertible_counterpoint']
            diminution = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['diminution']
            augmentation = ps_full['relationship_type'].str.match('non-mechanical transformation') & ps_full['augmentation']


            rl_nmt_dict = {'Non-Mechanical Transformation Subtype':['sounding in different voices','melodically inverted', 'retrograde',
            'metrically shifted', 'transposed', 'new counter subject', 'old counter subject transposed', 'old counter subject shifted metrically'
            , 'new combination', 'diminution', 'augmentation'],
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
                           diminution.sum(),
                           augmentation.sum(),
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

       st.subheader("Enter Relationship to View on CRIM Project")

       prefix = "https://crimproject.org/relationships/"
       int_val = st.text_input('Relationship Number')
       combined = prefix + int_val

       st.markdown(combined, unsafe_allow_html=True)

    # downloaded
       st.subheader('Download Filtered Relationships as CSV')
       userinput = st.text_input('Name of file for download (must include ".csv")', key='y')
       if st.button('Download without type details', key='m'):
           download_csv(ps_sub, userinput)
       st.write('or')
       if st.button('Download with type details', key='n'):
           xdownload_csv(ps_full, userinput)
