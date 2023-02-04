import streamlit as st
from main import collect_urls
from main import scrape
import pandas as pd
import io


@st.cache(suppress_st_warning=True, show_spinner=False)
def st_collect_urls():
    return collect_urls()


@st.cache(suppress_st_warning=True, show_spinner=False)
def st_scrape(page_urls):
    return scrape(page_urls)


st.title('支援制度検索')

if st.button('検索開始'):
    page_urls = collect_urls()
    st.text('全{}件'.format(len(page_urls)))
    df = scrape(page_urls)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        st.download_button('📥 ダウンロード', data=buffer, file_name='result.xlsx', mime='application/vnd.ms-excel')
