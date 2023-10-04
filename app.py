from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import main
from streamlit_tags import st_tags_sidebar, st_tags
from pypdf import PdfReader
import re


from dependencies import sign_up, fetch_users
from vector_fn import *

import qdrant_client
from qdrant_client.http import models
import os
import streamlit as st
import streamlit_authenticator as stauth

main.load_dotenv()

def main(username):
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
    
    #
    # Header and main page for search
    #
    st.title("Chat with your PDFs")

    st.write("")
    keywords_search = st_tags(label='Search your documents by tags', maxtags=3)
    search_tags = list(keywords_search)

    '''Files under specified tags:'''
    if st.button('See files'):
        files = []
        all_files = client.scroll(
                collection_name=VECTOR_STORE,
                scroll_filter=models.Filter(
                    must=[
                        models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="user",
                                    match=models.MatchValue(value=username)
                                ),
                                models.FieldCondition(
                                    key="tags",
                                    match=models.MatchAny(any=search_tags), 
                                ),
                            ],
                        ),
                    ],
                ),
                with_payload=True,
                with_vectors=False,
            )

            # display all tags to user
        if all_files[0]:
            for file in all_files:
                try:
                    val = file[0].payload['filename']
                except AttributeError:
                    continue
                
                if val not in files:
                    files.append(val)
            st.write(str(files))

        elif not all_files[0]:
            st.write('No files under specified tags. See all tags or upload new file in the sidebar.')

    #
    # Question input block

    specify_file = st.text_input("Specify a file you would like to search. Paste a file name from above.")

    # User input
    st.subheader("Query your files🔎")
    user_input = st.text_input("User Input")

    # Initiate Query by clicking button
    if st.button('Query'):
        response = openai.Embedding.create(
            input = user_input,
            model='text-embedding-ada-002'
        )

        embeddings = response['data'][0]['embedding'] # embed user input

        # search based on username and tags
        search_result = client.search(
            collection_name=VECTOR_STORE,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key='user',
                        match=models.MatchValue(
                            value=username,
                        ), 
                    ),
                    models.FieldCondition(
                        key='filename',
                        match=models.MatchValue(
                            value=specify_file,
                        ), 
                    )    
                ],
                should=[
                    models.FieldCondition(
                        key='tags',
                        match=models.MatchAny(any=search_tags,
                        ), 
                    ),
                ]   
            ),
            search_params=models.SearchParams(
                hnsw_ef=128,
                exact=False
            ),
            query_vector=embeddings,
            limit=3
        )
        
        prompt = "Context:\n"
        for result in search_result:
            prompt += result.payload['text'] + "\n---\n"
        prompt += "Question:" + user_input + "\n---\n" + "Answer"

        completion = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "user", "content": prompt}
            ]
        )

        st.write(completion.choices[0].message.content)
 
    #
    # PDF Upload and user pdf info Area
    #

    with st.sidebar:            
        def insert_points(push_points):
            operation_info = client.upsert(
            collection_name=VECTOR_STORE,
            wait=True,
            points=push_points
        )
            
        st.subheader(f"{username}'s Documents")

        # PDF Upload
        pdfs = st.file_uploader(
            "Upload your PDF files here", accept_multiple_files=True
        )

         # Option for user to see all their previous tags to help with search
        if st.button(':blue[See all your tags]'):
            all_tags = []
            all_points = client.scroll(
                collection_name=VECTOR_STORE,
                scroll_filter=models.Filter(
                    must=[
                        models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="user",
                                    match=models.MatchValue(value=username)
                                ),
                            ],
                        ),
                    ],
                ),
                with_payload=True,
                with_vectors=False,
            )

            # display all tags to user
            if all_points[0]:
                for point in all_points:
                    try:
                        vals = point[0].payload['tags']
                    except AttributeError:
                        continue
                    
                    for p in vals:
                        if p not in all_tags:
                            all_tags.append(p)
                
                st.write(str(all_tags))
        
        '''
        '''

        keywords = st_tags(label='Tag your documents', maxtags=3)
        tags = list(keywords)

        if st.button('Process'):
            with st.spinner(":green[Processing]"):
                for p in pdfs:
                    raw_text = get_pdf_text(pdfs)
                    if raw_text:
                        # splitting the text into chunks
                        chunks, filename = create_chunks(raw_text, p.name)
                        for p in pdfs:
                            st.write(p.name)
                        # get the vector database
                        vectors = get_embedding(chunks, username, tags, filename)
                        # push vectors to vector db
                        insert_points(vectors)
                    else:
                        st.write('No machine-readable text in file')
        


# Main function to run app:
if __name__=='__main__':

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
    Authenticator = stauth.Authenticate(creds, cookie_name='Streamlit', key='abcdef')

    email, authentication_status, username = Authenticator.login(":green[Login]", "main")

    info, info2 = st.columns(2)

    if not authentication_status:
        sign_up()
    
    if username:
        if username in usernames:
            if authentication_status:
                main(username)
            elif not authentication_status:
                with info:
                    st.error("Incorrect Username or Password")
            else:
                with info:
                    st.warning("Please provide login info")
        else:
            st.warning("Username does not exist. Please Sign Up")
    else:
        st.warning('Please Enter Username')

