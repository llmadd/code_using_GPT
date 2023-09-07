import streamlit as st
from work import work
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


def doc_code(code_str)->str:
    code_split_ = work.code_splite(code_str)
    result = ""
    results = work.doc_futures_run(code_split_)
    for i in results:
        result += i
    return result

def code_with_comment(code_str)->str:
    code_split_ = work.code_splite(code_str)
    result = ""
    results = work.comment_future_run(code_split_)
    for i in results:
        result += i
    return result

def qa_with_code(question:str,code_str)->str:
    code_split_ = work.code_splite(code_str)
    db = work.get_code_embd_save(code_split_)
    result = work.qa_with_code_chain(db = db,question=question)
    return result



st.title(":blue[Analyzing code using GPT 🤖]")


if 'code' not in st.session_state:
    st.session_state.code = ""
if 'doc_result' not in st.session_state:
    st.session_state.doc_result = ""
if 'comment_result' not in st.session_state:
    st.session_state.comment_result = ""


uploaded_file = st.file_uploader(label=":blue[上传代码文件]",type=["py"], help=":blue[仅支持py文件]")

if uploaded_file is not None:
    with st.sidebar:
        st.title(f"{uploaded_file.name}文件源码:")
        code_str = uploaded_file.getvalue().decode("utf-8")
        st.session_state.code = code_str
        st.code(code_str,language="python")
    col1, col2 = st.columns(spec= [0.5,0.5], gap = "large")
    with col1:
        comment_bt = st.button("插入注释")
    if comment_bt:
        with st.spinner("正在插入注释..."):
            result = code_with_comment(st.session_state.code)
        st.session_state.comment_result = result
        st.success("注释插入完成")
    with col2:
        doc_code_bt = st.button("生成文档")
    if doc_code_bt:
        with st.spinner("正在生成文档..."):
            result = doc_code(st.session_state.code)
        st.session_state.doc_result = result
        st.success("文档生成完成")
if st.session_state.comment_result != "":
    with st.expander("注释结果"):
        st.code(st.session_state.comment_result,language="python")
        st.download_button(
            label="下载注释后文件",
            data=st.session_state.comment_result,
            file_name='llmadd.py',)
if st.session_state.doc_result != "":
    with st.expander("文档内容"):
        st.markdown(st.session_state.doc_result)
        st.download_button(
            label="下载文档",
            data=st.session_state.doc_result,
            file_name='doc.md',)

# chat 
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "ai", "avatar":"🤖", "content": "我是强大的人工智能助手,请上传你的代码文件，我将帮助你更好了解代码！"}]
for msg in st.session_state.messages:
    st.chat_message(name=msg["role"],avatar=msg["avatar"]).markdown(msg["content"])

if st.session_state.code == "":
    st.error("请上传代码文件")
    st.stop()
if prompt := st.chat_input(placeholder="咨询与代码文件有关问题",max_chars = 4000,key="prompt"):

    st.session_state.messages.append({"role": "human", "avatar":"🧑", "content": prompt})

    st.chat_message(name="human",avatar="🧑").markdown(prompt)

    with st.chat_message(name="ai",avatar="🤖"):
        with st.spinner("正在生成答案..."):
            response = qa_with_code(prompt,st.session_state.code)

        st.session_state.messages.append({"role": "ai", "avatar":"🤖", "content": response})

        st.markdown(response)

