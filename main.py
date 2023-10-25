import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Hello",
    page_icon="👋", layout="wide"
)

st.write('''# The Tools''')

main_image=Image.open('logo_main_11.JPG')
st.image(main_image, caption='Version: Beta V1.0', use_column_width='always')

st.sidebar.success("Select a locacase above.")

st.markdown('''---''')

st.markdown(
    """
    * Complete APP deployment, local/cloud. Docker installation runs on Linux.
    * Optimize K&C result analysis.
    * Integrate Static Loads Generation feature.
    * Integrate KnC database.
    * Integrate suspension computer.
"""
)

st.markdown('''---''')

def main():
    cs_body()
    
def cs_body():

    col1, col2 = st.columns(2)

    with col1:
    st.image("logo_main_12.jpg")
    st.write("Description for image1_1")
    st.image("logo_main_13.jpg")
    st.write("Description for image1_2")

# 在第二个列中显示上下两张图片，并在每张图片下面写一行字
    with col2:
    st.image("logo_main_14.jpg")
    st.write("Description for image2_1")
    st.image("logo_main_15.jpg")
    st.write("Description for image2_2")

    return None

# Run main()

if __name__ == '__main__':
    main()
