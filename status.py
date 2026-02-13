# status.py
import streamlit as st
import pandas as pd

# Sample data for the tracker
data = {
    'Task Name': ['Task 1', 'Task 2', 'Task 3'],
    'Priority': ['High', 'Medium', 'Low'],
    'Status': ['In Progress', 'Not Started', 'Completed']
}

# Create a DataFrame from the sample data
df = pd.DataFrame(data)

# Streamlit app
def main():
    st.title('Project Status Tracker')
    st.subheader('Current Project Status')
    st.write(df)

if __name__ == '__main__':
    main()