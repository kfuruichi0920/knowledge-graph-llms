# Import necessary modules
import streamlit as st
import streamlit.components.v1 as components  # For embedding custom HTML
from generate_knowledge_graph import generate_knowledge_graph
import os

st.set_page_config(
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)

st.title("テキストから知識グラフを生成")

st.sidebar.title("入力ドキュメント")
input_method = st.sidebar.radio(
    "入力方法を選択してください:",
    ["テキストをアップロード", "テキストを入力"]
)

# Dropdown list of saved graphs
saved_files = sorted([f for f in os.listdir("out") if f.endswith(".html")])
selected_saved = st.sidebar.selectbox("保存済みグラフを表示", saved_files) if saved_files else None

generated = False

if input_method == "Upload txt":
    uploaded_file = st.sidebar.file_uploader(label="ファイルをアップロード", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path = generate_knowledge_graph(text)
                st.success("知識グラフの生成が完了しました！")
                with open(output_path, "r", encoding="utf-8") as HtmlFile:
                    components.html(HtmlFile.read(), height=1000)
                generated = True
else:
    text = st.sidebar.text_area("テキストを入力してください", height=300)
    if text:
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path = generate_knowledge_graph(text)
                st.success("知識グラフの生成が完了しました！")
                with open(output_path, "r", encoding="utf-8") as HtmlFile:
                    components.html(HtmlFile.read(), height=1000)
                generated = True

if not generated and selected_saved:
    with open(os.path.join("out", selected_saved), "r", encoding="utf-8") as HtmlFile:
        components.html(HtmlFile.read(), height=1000)
