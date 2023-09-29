from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from qdrant_client.http import models
import openai
import uuid

def get_pdf_text(pdfs):
    '''
    get_pdf_text(pdfs) loops through all pdfs and returns the text extracted from
    each one, concatenated together as a string.

    pdfs->Type returned from st.file_uploader, which is ListofFiles
    '''
    text = ""
    for pdf in pdfs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def create_chunks(text):
    '''
    create_chunks(text) applies our texsplitter to the string text that is passed
    and returns the chunks that are formed.

    text-> str
    '''
    text_splitter = CharacterTextSplitter(
        separators=[" ", ",", "\n"],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_text(text)
    return chunks

def get_embedding(chunks, user_id, tags, model_id='text-embedding-ada-002'):
    '''
    get_embedding(chunks, user_id, tags, model_id) embeds our chunks using our desired model,
    default being text-embedding-ada-002. 

    chunks-> List(str)
    user_id-> str
    tags-> List(str)
    model_id-> str
    '''
    points = []
    for idx, chunk in enumerate(chunks):
        response = openai.Embedding.create(
            input = chunk,
            model=model_id
        )

        embeddings = response['data'][0]['embedding']
        point_id = str(uuid.uuid4())

        points.append(models.PointStruct(
            id=point_id, vector=embeddings, 
            payload={'user': str(user_id), 'text': chunk, 'tags': tags}
            ))
        
    return points
