import streamlit as st
from main import collect_urls
from main import scrape
import pandas as pd
import io
import pickle
from streamlit_autorefresh import st_autorefresh
st_autorefresh(100*60*1000)


@st.cache(suppress_st_warning=True, show_spinner=False, max_entries=3, ttl=3600)
def st_collect_urls():
    return collect_urls()


@st.cache(suppress_st_warning=True, show_spinner=False, max_entries=3, ttl=3600)
def st_scrape(page_urls):
    return scrape(page_urls)

@st.cache(suppress_st_warning=True, show_spinner=False, max_entries=3, ttl=3600)
def save_urls(page_urls):
    with open('urls.pickle', 'wb') as f:
        pickle.dump(page_urls, f)


st.title('支援制度検索')

if st.button('新規検索開始', key='new'):
    st.text('Loading...')
    page_urls = collect_urls()
    save_urls(page_urls)
    num_pages = len(page_urls)
    with open('num.txt', 'w') as f:
        f.write(num_pages)
    st.text('全{}件'.format(num_pages))
    end_flag = scrape(page_urls)
    if end_flag:
        df = pd.read_csv('output.csv')
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            st.download_button('📥 ダウンロード', data=buffer, file_name='result.xlsx', mime='application/vnd.ms-excel')

if st.button('前回中断したところから開始', key='resume'):
    st.text('Resuming...')
    df = pd.read_csv('output.csv')
    with open('num.txt', 'r') as f:
        num_pages = int(f.read())
    st.text('全{}件'.format(num_pages))
    df = pd.read_csv('output.csv')
    num_finished = len(df)
    st.text('{}件目から再開'.format(num_finished+1))
    end_flag = scrape(page_urls, start_idx=num_finished)
    if end_flag:
        df = pd.read_csv('output.csv')
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            st.download_button('📥 ダウンロード', data=buffer, file_name='result.xlsx', mime='application/vnd.ms-excel')