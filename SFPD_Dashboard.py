from urllib.error import URLError

import altair as alt
import pydeck as pdk
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

def data_frame_demo():
    @st.cache_data
    def get_table_data():
        query = """ SELECT * FROM ( SELECT pddistrict, year, crime_count FROM `clouddatamining.crimecount`) PIVOT (MAX(crime_count) FOR year IN 
        (2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017)) """
        dfquery = client.query(query)
        df = dfquery.to_dataframe()
        return df.set_index("pddistrict")

    def get_chart_data():
        query = """ SELECT * FROM `clouddatamining.crimecount` WHERE year > 2006"""
        dfquery = client.query(query)
        df = dfquery.to_dataframe()
        return df

    try:
        df = get_table_data()
        chart_data = get_chart_data()
        districts = st.multiselect(
            "Choose districts", list(df.index), ["PARK", "BAYVIEW"]
        )
        if not districts:
            st.error("Please select at least one country.")
        else:

            data = df.loc[districts]
            st.write("### Crimes reported by districts", data.sort_index())

            chart_data = chart_data[chart_data['pddistrict'].isin(districts)]
            chart_data['year'] = chart_data['year'].astype(str)
            chart = (
                alt.Chart(chart_data)
                .mark_area(opacity=0.3)
                .encode(
                    x=alt.X("year:T"),
                    y=alt.Y("crime_count:Q", stack=None),
                    color="pddistrict:N",
                )
            )
            st.altair_chart(chart, use_container_width=True)
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )


def line_plot():
    def get_table_data():
        query = """ SELECT * FROM ( SELECT category, month, crime_count FROM `clouddatamining.category_count_by_month`) PIVOT (MAX(crime_count) FOR month IN 
        ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'))"""
        dfquery = client.query(query)
        df = dfquery.to_dataframe()
        return df.set_index('category')

    def get_chart_data():
        query = """ SELECT * FROM `clouddatamining.category_count_by_month`"""
        dfquery = client.query(query)
        df = dfquery.to_dataframe()
        return df

    df = get_chart_data()
    df_table = get_table_data()

    df.sort_values(by='month', ignore_index=True)
    crime = st.selectbox(
        "Choose category", list(df_table.index), index=list(df_table.index).index('ASSAULT')
    )

    st.write("### Crimes per month - Category-Wise", df_table[df_table.index == crime])
    df = df[df['category'] == crime]
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X('month:N', sort=['January', 'February', 'March', 'April', 'May',
                                     'June', 'July', 'August', 'September', 'October', 'November', 'December']),
            y=alt.Y('crime_count:Q', scale=alt.Scale(domain=[df['crime_count'].min(), df['crime_count'].max()]))
        )
    )
    st.altair_chart(chart, use_container_width=True)


def map_plot():
    def get_table_data():
        query = """ SELECT * FROM `clouddatamining.locationdata`"""
        dfquery = client.query(query)
        df = dfquery.to_dataframe()
        return df

    df_table = get_table_data()

    list1 = list(df_table['category'].unique())
    list1.remove('SEX OFFENSES, FORCIBLE')
    crime = st.selectbox(
        "Choose category", list1, index=list1.index('ROBBERY')
    )

    st.write("### Crimes Location by Category")
    df_table = df_table[df_table.category == crime]
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state={
                "latitude": 37.76,
                "longitude": -122.4,
                "zoom": 11,
                "pitch": 50,
            },
            layers=[pdk.Layer(
                "HexagonLayer",
                data=df_table,
                get_position=["long", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            )],
        )
    )

st.set_page_config(page_title="SFPD Dashboard", page_icon="📊")
st.markdown("# SFPD Dashboard")
st.sidebar.header("SFPD Dashboard")

data_frame_demo()
line_plot()
map_plot()