import streamlit as st
from streamlit_chat import message
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
import tempfile
from langchain.document_loaders import PyPDFLoader
import os

os.environ["OPENAI_API_KEY"]= "sk-로 시작하는 키 입력"

# streamlit 파일 업로드 기능 생성
uploaded_file = st.sidebar.file_uploader("upload", type="pdf")

# 업로드된 pdf를 FAISS에 저장
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    loader = PyPDFLoader(tmp_file_path)
    data = loader.load()
    embeddings = OpenAIEmbeddings()
    vectors = FAISS.from_documents(data, embeddings)

    # ConversationRetrevalChain으로 대화형 챗봇 구성
    chain = ConversationalRetrievalChain.from_llm(llm = ChatOpenAI(temperature=0.0, model='gpt-4'), retriever=vectors.as_retriever())

    # 문맥 유지를 위해 과거 대화 이력을 추가
    def conversation_chat(query):
        result = chain({"question":query, "chat_history":st.session_state['history']})
        st.session_state['history'].append((query,result['answer']))
        return result['answer']
    
    # 초기 질문과 답변에 대한 처리
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["안녕하세요! "+ uploaded_file.name + "에 관해 질문 주세요."]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["안녕하세요!"]

    # 챗봇 이력에 대한 컨테이너
    response_container = st.container()

    # 사용자가 입력한 문장에 대한 컨테이너
    container = st.container()

    with container:
        with st.form(key="Conv_Question", clear_on_submit=True):
            user_input = st.text_input("Query:", placeholder="PDF 파일에 대해 얘기해볼까요? :)", key="input")
            submit_button = st.form_submit_button(label="Send")

            # 사용자가 질문을 입력하고 [Send] 버튼을 눌렀을때 처리
            if submit_button and user_input:
                output = conversation_chat(user_input)
                # 사용자의 질문이나 llm에 대한 결과를 계속 추가
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

            # llm이 답변을 해야하는 경우에 대한 처리
            if st.session_state['generated']:
                with response_container:
                    for i in range(len(st.session_state['generated'])):
                        message(st.session_state['past'][i], is_user=True, key=str(i) + "_user", avatar_style="fun-emoji", seed = "Nala")
                        message(st.session_state['generated'][i], key=str(i), avatar_style="bottts", seed="Fluffy")    