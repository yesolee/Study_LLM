import streamlit as st
import os
os.environ["OPENAI_API_KEY"] = "sk-로 시작하는 키 입력"

st.set_page_config(page_title="이메일 작성 서비스에요", page_icon=":robot:")
st.header('이메일 작성기')

def getEmail():
    input_test = st.text_area(label="메일 입력", label_visibility='collapsed', placeholder="당신의 메일은...", key="input_text")
    return input_test

input_text = getEmail()

query_template = """

    이메일을 작성해주세요.
    아래는 이메일입니다.:
    이메일: {email}
"""

from langchain import PromptTemplate
prompt = PromptTemplate(
    input_variables=["email"],
    template = query_template
)

from langchain_community.chat_models import ChatOpenAI

def loadLanguageModel():
    llm = ChatOpenAI(temperature=0.0, model="gpt-4")
    return llm

st.button("*예제를 보여주세요*", type="secondary", help="봇이 작성한 메일을 확인해보세요")
st.markdown("### 봇이 작성한 메일은")

if input_text:
    llm = loadLanguageModel()
    prompt_with_email = prompt.format(email=input_text)
    formatted_email = llm.predict(prompt_with_email)

    st.write(formatted_email)