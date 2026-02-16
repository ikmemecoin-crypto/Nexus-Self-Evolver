import streamlit as st

title = "Fashion Bunny"

st.title(title)

nav = st.container()
with nav:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Home")
    with col2:
        st.write("Products")
    with col3:
        st.write("About")

header = st.container()
with header:
    st.image("kids_garments.jpg")
    st.button("Shop Now")

section1 = st.container()
with section1:
    st.write("Featured Products")
    col1, col2 = st.columns(2)
    with col1:
        st.image("product1.jpg")
        st.write("$10.99")
        st.button("Add to Cart")
    with col2:
        st.image("product2.jpg")
        st.write("$9.99")
        st.button("Add to Cart")

section2 = st.container()
with section2:
    st.write("Categories")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Tops")
    with col2:
        st.write("Bottoms")
    with col3:
        st.write("Dresses")

footer = st.container()
with footer:
    st.write("Contact Information: 1234567890, fashionbunny@example.com, 123 main st")
    st.write("Social Media Links: Facebook, Instagram")
    email = st.text_input("Newsletter Signup")
    st.button("Signup")