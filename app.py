import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('sales_data.csv')

st.title('Sales Data Dashboard')

st.write(df.head())

fig, ax = plt.subplots()
ax.plot(df['Date'], df['Sales'])
ax.set_xlabel('Date')
ax.set_ylabel('Sales')
st.pyplot(fig)

st.bar_chart(df['Sales'])
