# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
import numpy as np
from streamlit.logger import get_logger
from google.oauth2 import service_account
from google.cloud import bigquery

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )


    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)

    query = """ SELECT * FROM `clouddatamining.categorycount` LIMIT 1000 """
    dfquery = client.query(query)

    df_crimecount=dfquery.to_dataframe()
    # df_crimecount.head()

   # st.bar_chart(df_crimecount)

    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    st.bar_chart(chart_data)


if __name__ == "__main__":
    run()
