# Import necessary modules
import streamlit as st
import streamlit.components.v1 as components  # For embedding custom HTML
from generate_knowledge_graph import generate_knowledge_graph
import os


def build_data_html(nodes, relationships):
    """Return HTML snippet listing nodes and relationships."""
    node_items = "".join(
        [f"<li>{getattr(node, 'id', '')} ({getattr(node, 'type', '')})</li>" for node in nodes]
    )
    rel_items = "".join(
        [
            f"<li>{getattr(rel.source, 'id', '')} -[{getattr(rel, 'type', '')}]-> {getattr(rel.target, 'id', '')}</li>"
            for rel in relationships
        ]
    )
    return (
        "<div style='height:400px; overflow:auto; border:1px solid #ccc; padding:10px;'>"
        "<h4>Nodes</h4><ul>" + node_items + "</ul>"
        "<h4>Relationships</h4><ul>" + rel_items + "</ul></div>"
    )

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
saved_files = sorted([f for f in os.listdir("out") if f.endswith(".html")])
selected_saved = st.sidebar.selectbox("保存済みグラフを表示", saved_files) if saved_files else None

generated = False

if input_method == "Upload txt":
    uploaded_file = st.sidebar.file_uploader(label="ファイルをアップロード", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path, nodes, relationships = generate_knowledge_graph(
                    text, model_name=selected_model
                )
                st.success("知識グラフの生成が完了しました！")
                st.markdown(build_data_html(nodes, relationships), unsafe_allow_html=True)
                with open(output_path, "r", encoding="utf-8") as HtmlFile:
                    components.html(HtmlFile.read(), height=1000)
                generated = True
else:
    text = st.sidebar.text_area("テキストを入力してください", height=300)
    if text:
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path, nodes, relationships = generate_knowledge_graph(
                    text, model_name=selected_model
                )
                st.success("知識グラフの生成が完了しました！")
                st.markdown(build_data_html(nodes, relationships), unsafe_allow_html=True)
                with open(output_path, "r", encoding="utf-8") as HtmlFile:
                    components.html(HtmlFile.read(), height=1000)
                generated = True

if not generated and selected_saved:
    with open(os.path.join("out", selected_saved), "r", encoding="utf-8") as HtmlFile:
        components.html(HtmlFile.read(), height=1000)
