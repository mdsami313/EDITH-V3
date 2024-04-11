import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from cwe import css, user_template, bot_template
from langchain_google_genai import GoogleGenerativeAI
import google.generativeai as genai
import os
from langchain_community.embeddings import GooglePalmEmbeddings
from io import BytesIO
from gtts import gTTS 
# import librosa

# from st_audiorec import st_audiorec
# import speech_recognition as sr

GENAI_API_KEY = "AIzaSyCbRM1raXsjteH45M92e49YvmBTkcTN1M0"
os.environ["GOOGLE_API_KEY"] = GENAI_API_KEY

genai.configure(api_key=GENAI_API_KEY)
# r = sr.Recognizer()



st.set_page_config(page_title="Chat with multiple PDFs",
                    page_icon=":books:")


if 'doc' not in st.session_state:
    st.session_state['doc'] = False
if 'audio_count' not in st.session_state:
    st.session_state['audio_count'] = 0
if 'audio_history' not in st.session_state:
    st.session_state['audio_history'] = {}

    
##############################################PDF ChatBot###################################################

def text_to_speech(text):
    """
    Converts text to an audio file using gTTS and returns the audio file as binary data
    """
    audio_bytes = BytesIO()
    tts = gTTS(text=text, lang="en")
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes.read()

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = GooglePalmEmbeddings(model="models/embedding-001", google_api_key=GENAI_API_KEY)
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key=GENAI_API_KEY)

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


# audio_history = {}
def handle_userinput(user_question):
    # global audio_count
    # audio_count = 0
    if st.session_state.doc == False:
        st.warning("To Chat, Please Load PDF!")
    elif st.session_state.doc == True:
            response = st.session_state.conversation({'question': user_question})
            # print(response)
            
            st.session_state.chat_history = response['chat_history']
            # print(type(text_to_speech(system_response)))
            with st.spinner("Generating..."):
                # try:
                system_response =  str(st.session_state.chat_history[-1]).split("content='")[1]
                # st.session_state['audio_chat_history'] = text_to_speech(system_response)
                st.session_state['audio_count'] += 1
                audio_hist = st.session_state.audio_chat_history = text_to_speech(system_response)
                # audio_count+=1
                # print("EXECUTED")
                print(st.session_state['audio_count'])
                if st.session_state['audio_count'] % 2 != 0:
                    st.session_state['audio_history'][st.session_state['audio_count']] = text_to_speech(system_response)
                elif st.session_state['audio_count'] % 2 == 0:
                    st.session_state['audio_count']+=1
                    st.session_state['audio_history'][st.session_state['audio_count']] = text_to_speech(system_response)
                #     print("EXE")
                # print(st.session_state['audio_history'].keys())
                # print(st.session_state['audio_history'])
                for i, message in enumerate(st.session_state.chat_history):
                    if i % 2 == 0:
                        st.write(user_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)
                    else:
                        st.write(bot_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)
                        audio_chat = st.audio(st.session_state['audio_history'][i], format="audio/wav")
                        # print(st.session_state.audio_chat_history)
                        # st.session_state.chat_history = audio_chat

        # except:
        #         st.warning("Please Re-Upload File.")
        # except:
        #     st.warning("Give Clear Input To Get The Answer.")
            # st.audio(text_to_speech(system_response), format="audio/wav")
                
def main():
    st.write(css, unsafe_allow_html=True)
    # text = None
    # wav_audio_data = None

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "audio_chat_history" not in st.session_state:
        st.session_state.audio_chat_history = None
    if 'ok_a' not in st.session_state:
        st.session_state.ok_a = False
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = False


    st.title("Chat with multiple PDFs :books:")
    user_question = st.chat_input(placeholder="Ask a question about your documents:")
    
    

    with st.sidebar:
        st.header("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True, type="pdf")
        if len(pdf_docs) != 0:
            print(len(pdf_docs))
            # st.session_state.doc = True
            
            if not st.session_state.uploaded_file:
                st.session_state.uploaded_file = True
                print("The file exists.")
            if st.button("Process"):
                st.session_state.doc = True
                if not st.session_state.ok_a:
                    with st.spinner("Processing"):
                        # get pdf text
                        raw_text = get_pdf_text(pdf_docs)

                        # get the text chunks
                        text_chunks = get_text_chunks(raw_text)

                        # create vector store
                        vectorstore = get_vectorstore(text_chunks)

                        # create conversation chain
                        st.session_state.conversation = get_conversation_chain(
                            vectorstore)
                    st.success("File uploaded successfully!")
                    st.session_state.ok_a = True
        elif len(pdf_docs) == 0:
            st.session_state.conversation = None
            st.session_state.chat_history = None
            st.session_state.audio_chat_history = None
     
    if user_question:   # 
        handle_userinput(user_question)


main()












