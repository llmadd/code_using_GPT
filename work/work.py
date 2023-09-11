import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import concurrent.futures
from langchain.chains.base import Chain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

CHUNK_SIZE = 3000

def load_env(openai_api_key:str,model_name:str,temperature:float)->None:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    chat = ChatOpenAI(model = model_name,temperature = temperature,streaming=True)
    return chat

code_with_comment_chain_systemtemplate = """
你强大的人工智能ChatGPT。

你的任务是为python代码增加中文注释。禁止修改代码！

只允许输出增加注释后的python代码。禁止输出任何其他内容！
"""

doc_code_chain_systemtemplate = """
你强大的人工智能ChatGPT。

你的任务是为代码生成一篇README.md文档。

文档中介绍代码用到的技术栈，代码的功能，代码的使用方法，代码的运行环境等等。

用markdown格式输出README.md文档。
"""

qa_with_code_chain_systemtemplate = """
你强大的人工智能ChatGPT。

你需要根据代码内容和你自身的知识尽可能的回答用户的问题。

要尽可能详细的回答用户问题
"""

def get_file_type(file_name):
    extension = "."+file_name.split('.')[-1]
    if extension in ['.cpp', '.cc', '.cxx', '.hpp', '.h', '.hxx']:
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.CPP,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )
        return splitter
    elif extension == '.go':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.GO,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.java':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.js':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JS,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.php':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PHP,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.proto':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PROTO,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.py':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension in '.rst':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.RST,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.rb':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.RUBY,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.rs':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.RUST,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.scala':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.SCALA,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.swift':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.SWIFT,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension in ['.md', '.markdown']:
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.tex':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.LATEX,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension in ['.html', '.htm']:
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.HTML,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    elif extension == '.sol':
        splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.SOL,chunk_size=CHUNK_SIZE, chunk_overlap=0
    )   
        return splitter
    else:
        return 'Unknown'

def get_code_embd_save(code_split:List[str])->Chroma:
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_texts(texts=code_split,embedding=embeddings)   
    return db


def qa_with_code_chain(db:Chroma,question:str,chat)->str:
    retrievers_re = ""
    retrievers = db.as_retriever(search_kwargs={'k': 4,})
    doc_re = retrievers.get_relevant_documents(question)
    for i in doc_re:
        retrievers_re += i.page_content   
    human_prompt = """
    根据下面代码内容回答问题：
    --------------------
    {retrievers_re}
    --------------------
    问题：{question}
    """
    human_message_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template=human_prompt,
            input_variables=["question"],
            partial_variables={"retrievers_re": retrievers_re}
        )
    )
    chat_prompt_template = ChatPromptTemplate.from_messages([
        ("system", qa_with_code_chain_systemtemplate),
        human_message_prompt
    ])
    chain = LLMChain(llm=chat, prompt=chat_prompt_template)
    answer = chain.run(question)
    return answer

def code_splite(code:str,splitter:RecursiveCharacterTextSplitter)->List[str]:
    splite_code = splitter.split_text(text=code)

    return splite_code

def code_with_comment_chain(code:str,chat)->str:
    chat_prompt_template = ChatPromptTemplate.from_messages([
        ("system", code_with_comment_chain_systemtemplate),
        ("human","{text}")
    ])
    chain = LLMChain(llm=chat, prompt=chat_prompt_template)
    result = chain.run(code)
    return result

def code_doc_chain(code: str,chat) -> str:
    chat_prompt_template = ChatPromptTemplate.from_messages([
        ("system", doc_code_chain_systemtemplate),
        ("human", "{text}")
    ])
    chain = LLMChain(llm=chat, prompt=chat_prompt_template)
    result = chain.run(code)
    return  result

def doc_futures_run(code_list:List[str],chat)->List[str]:

    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:

        futures = [executor.submit(code_doc_chain, _i,chat) for _i in code_list]
        
        # for future in concurrent.futures.as_completed(futures):
        #     result = future.result()
        #     results.append(result)
        # 更新结果不按顺序返回 
        for result in executor.map(lambda future: future.result(), futures):
            results.append(result)
    return results

def comment_future_run(code_list:List[str],chat)->List[str]:
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:

        futures = [executor.submit(code_with_comment_chain, _i,chat) for _i in code_list]
        
        # for future in concurrent.futures.as_completed(futures):
        #     result = future.result()
        #     results.append(result)
        # 更新结果不按顺序返回 
        for result in executor.map(lambda future: future.result(), futures):
            results.append(result)
    return results



# print(st.secrets["openai_api_key"])
    