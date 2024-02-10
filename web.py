import streamlit as st
from chains import *


# Streamlit app
def main():
    if "setup_done" not in st.session_state:
        print("Performing setup")
        st.session_state.rag = prepare_setup()
        st.session_state.setup_done = True
    # Load the image file
    logo = open('FinGuruLogo.png', 'rb').read()
    # Display the image in the upper left corner
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(logo)

    st.markdown('## Recomendador de fondos de inversión')

    # Text input for the question
    question = st.text_input("¿Qué tipo de fondo te interesa?")

    # Button to submit the question
    if st.button("Enviar"):
        if question:
            with st.spinner("Analizando ..."):
                answer = st.session_state.rag.invoke(question)
                st.write(answer)

if __name__ == "__main__":
    main()
