import streamlit as st
from main import collect_urls
from main import scrape
import pandas as pd
import io
from streamlit_autorefresh import st_autorefresh
import gc
st_autorefresh(100*60*1000)


@st.cache(suppress_st_warning=True, show_spinner=False, max_entries=3, ttl=3600)
def st_collect_urls():
    return collect_urls()


@st.cache(suppress_st_warning=True, show_spinner=False, max_entries=3, ttl=3600)
def st_scrape(page_urls):
    return scrape(page_urls)


st.title('支援制度検索')

if st.button('検索開始'):
    st.text('Loading...')
    page_urls = collect_urls()
    st.text('全{}件'.format(len(page_urls)))
    first = int(len(page_urls)//3)
    second = first*2
    df = scrape(page_urls[:first])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        st.download_button('📥 ダウンロード', data=buffer, file_name='first_result.xlsx', mime='application/vnd.ms-excel')
    del df
    gc.collect()
    df = scrape(page_urls[first:second])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        st.download_button('📥 ダウンロード', data=buffer, file_name='second_result.xlsx', mime='application/vnd.ms-excel')
    del df
    gc.collect()
    df = scrape(page_urls[second:])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        st.download_button('📥 ダウンロード', data=buffer, file_name='third_result.xlsx', mime='application/vnd.ms-excel')
    del df
    gc.collect()
