# Import necessary modules
import streamlit as st
import streamlit.components.v1 as components  # For embedding custom HTML
from generate_knowledge_graph import generate_knowledge_graph
import os
import re

st.set_page_config(
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)

st.title("テキストから知識グラフを生成")

model_options = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
]
selected_model = st.sidebar.selectbox("LLMモデル:", model_options, index=0)

st.sidebar.title("入力ドキュメント")
input_method = st.sidebar.radio(
    "入力方法を選択してください:",
    ["テキストをアップロード", "テキストを入力"]
)

# Dropdown list of saved graphs
files = [f for f in os.listdir("out") if f.endswith(".html")]
info_list = []
for f in files:
    m = re.match(r"(\d{8}_\d{6})_(.*?)_(.*)\.html$", f)
    if m:
        timestamp, summary, model = m.groups()
        info_list.append((timestamp, summary, model, f))
info_list.sort(key=lambda x: x[0], reverse=True)
display_names = [f"{info[1]}_{info[2]}" for info in info_list]
file_map = {f"{info[1]}_{info[2]}": info[3] for info in info_list}
selected_display = st.sidebar.selectbox("保存済みグラフを表示", display_names) if display_names else None

generated = False

if input_method == "Upload txt":
    uploaded_file = st.sidebar.file_uploader(label="ファイルをアップロード", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path = generate_knowledge_graph(text, model_name=selected_model)
                st.success("知識グラフの生成が完了しました！")
                with open(output_path, "r", encoding="utf-8") as HtmlFile:
                    components.html(HtmlFile.read(), height=1000)
                generated = True
else:
    text = st.sidebar.text_area("テキストを入力してください", height=300)
    if text:
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path = generate_knowledge_graph(text, model_name=selected_model)
                st.success("知識グラフの生成が完了しました！")
                with open(output_path, "r", encoding="utf-8") as HtmlFile:
                    components.html(HtmlFile.read(), height=1000)
                generated = True

if not generated and selected_display:
    with open(os.path.join("out", file_map[selected_display]), "r", encoding="utf-8") as HtmlFile:
        components.html(HtmlFile.read(), height=1000)
