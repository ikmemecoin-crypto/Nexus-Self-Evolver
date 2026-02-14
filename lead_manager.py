import streamlit as st
import pandas as pd

st.title("🎯 Lead Tracker")
data = {"Client Name": ["Example Corp", "AI Solutions"], "Status": ["Contacted", "Follow-up"]}
df = pd.DataFrame(data)
st.table(df)
st.success("Lead Tracker is Live!")