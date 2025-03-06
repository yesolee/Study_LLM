from langchain_community.document_loaders import WebBaseLoader

# 크롤링 하고 싶은 url
url = 'https://wikidocs.net/231393'

loader = WebBaseLoader(url)

docs = loader.load()
print(len(docs)) # 1
print(len(docs[0].page_content)) # 15735
print(docs[0].page_content)

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits= text_splitter.split_documents(docs)

print(len(splits)) # 19
print(splits[10])
splits[10].page_content
splits[10].metadata

# {'source': 'https://wikidocs.net/231393',
#  'title': '2-1. RAG 개요 - 랭체인(LangChain) 입문부터 응용까지',
#  'description': 'RAG(Retrieval-Augmented Generation) 파이프라인은 기존의 언어 모델에 검색 기능을 추가하여, 주어진 질문이나 문제에 대해 더 정확하고 풍부한 정보를 기…',
#  'language': 'ko'}

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

vectorsotre = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
docs = vectorsotre.similarity_search("인덱싱에 대해 설명해주세요")
print(len(docs))
print(docs[0].page_content)

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

template = '''
    항상 다음의 context에 기반하여 답변하세요.
    : {context}

    Question : {question}    
'''

prompt = ChatPromptTemplate.from_template(template)


model = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Retriever
retriever = vectorsotre.as_retriever()

# combine Documents
def format_docs(docs):
    return '\n\n'.join(doc.page_content for doc in docs)

# RAG Chain 연결
rag_chain = (
    {
        'context': retriever | format_docs, 'question': RunnablePassthrough()
    }
    | prompt
    | model
    | StrOutputParser()
)

# Chain 실행
rag_chain.invoke("인덱싱에 대해 설명해주세요")