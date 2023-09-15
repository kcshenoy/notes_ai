from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from pypdf import PdfFileReader
import qdrant_client
import os
from dotenv import main
import streamlit as st
import streamlit_authenticator as stauth
from dependencies import sign_up, fetch_users, get_usernames, get_emails

main.load_dotenv()

def get_vector_store():
    '''
    get_vector_store() returns the current vector database being used to store
    all vectorized text
    '''
    client = qdrant_client.QdrantClient(
        QDRANT_HOST, api_key = QDRANT_KEY
        )

    embeddings = OpenAIEmbeddings()
    vector_db = Qdrant(
        client=client,
        collection_name=VECTOR_STORE,
        embeddings=embeddings,
        )

    return vector_db

def get_pdf_text(pdfs):
    '''
    get_pdf_text(pdfs) loops through all pdfs and returns the text extracted from
    each one, concatenated together as a string.

    pdfs->Type returned from st.file_uploader, which is ListofFiles
    '''
    text = ""
    for pdf in pdfs:
        pdf_reader = PdfFileReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

try:
    # collect all current user info
    users = fetch_users()
    emails = []
    usernames = []
    passwords = []

    for user in users:
        emails.append(user['key'])          # add email/primary key to email list
        usernames.append(user['username'])  # add username to username list
        passwords.append(user['password'])  # add password to password list

    creds = {'usernames': {}}
    for index in range(len(emails)):
        creds['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

    # authenticate user login info
    Authenticator = stauth.Authenticate(creds, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=4)

    email, authentication_status, username = Authenticator.login(":green[Login]", "main")

    info, info2 = st.columns(2)

    if not authentication_status:
        sign_up()

    if username:
        if username in usernames:
            if authentication_status:
                
                st.header("Chat with your PDFs")
                st.subheader("Query your files🔎")
                st.text_input("Ask a question about your files")

                # PDF Upload Area
                with st.sidebar:
                    st.subheader(f"{username}'s Documents")
                    pdfs = st.file_uploader(
                        "Upload your PDF files here", accept_multiple_files=True
                    )

                    if st.button(':blue[Process]'):
                        with st.spinner(":green[Processing]"):
                            raw_text = get_pdf_text(pdfs)
                            if raw_text:
                                st.write(raw_text)
                                st.write('Here is the text')

                # loading in .env variables 
                OPENAI_KEY = os.getenv("OPENAI_API_KEY")            # OpenAI API key
                QDRANT_HOST = os.getenv("QDRANT_HOST")              # Qdrant client API key
                QDRANT_KEY = os.getenv("QDRANT_API_KEY")            # Qdrant vector store API key
                DETA_KEY = os.getenv("DETA_API_KEY")                # Deta user store API key
                DETA_PDF_KEY = os.getenv("DETA_PDF_KEY")            # Deta pdf store API key
                VECTOR_STORE = os.getenv("QDRANT_COLLECTION_NAME")  # Qdrant collection name

                # initialize qdrant client
                client = qdrant_client.QdrantClient(
                    QDRANT_HOST, api_key = QDRANT_KEY
                )

                # setup vector config
                vector_config = qdrant_client.http.models.VectorParams(
                    size=1536, 
                    distance=qdrant_client.http.models.Distance.COSINE
                    )

                # create collection for vector store
                # client.recreate_collection(
                #     collection_name=VECTOR_STORE,
                #     vectors_config=vector_config
                # )
                
                vector_db = get_vector_store()

                def create_chunks(text):
                    text_splitter = CharacterTextSplitter(
                        separator='\n',
                        chunk_size=1000,
                        chunk_overlap=150,
                        length_function=len
                    )
                chunks = create_chunks(text)

            elif not authentication_status:
                with info:
                    st.error("Incorrect Username or Password")
            else:
                with info:
                    st.warning("Please provide login info")

        else:
            st.warning("Username does not exist. Please Sign Up")



except:
    st.success("Refresh Page")


# def main():
#     load_dotenv()
#     OPENAI_KEY = os.getenv("OPENAI_API_KEY")
#     QDRANT_HOST = os.getenv("QDRANT_HOST")
#     QDRANT_KEY = os.getenv("QDRANT_API_KEY")
#     DETA_KEY = os.getenv("DETA_API_KEY")

#     client = qdrant_client.QdrantClient(
#         QDRANT_HOST, QDRANT_KEY
#     )

