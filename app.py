# Import necessary modules
import streamlit as st
import streamlit.components.v1 as components  # For embedding custom HTML
from generate_knowledge_graph import generate_knowledge_graph
import os
import re
import json
import uuid


def _to_node_dict(node):
    if isinstance(node, dict):
        return {"id": node.get("id", ""), "type": node.get("type", "")}
    return {"id": getattr(node, "id", ""), "type": getattr(node, "type", "")}


def _to_rel_dict(rel):
    if isinstance(rel, dict):
        return {
            "source": rel.get("source", ""),
            "target": rel.get("target", ""),
            "type": rel.get("type", ""),
        }
    return {
        "source": getattr(rel.source, "id", ""),
        "target": getattr(rel.target, "id", ""),
        "type": getattr(rel, "type", ""),
    }


def build_data_html(nodes, relationships):
    """Return HTML snippet listing nodes and relationships with copy button."""
    unique = uuid.uuid4().hex
    nodes_dict = [_to_node_dict(n) for n in nodes]
    rels_dict = [_to_rel_dict(r) for r in relationships]
    node_items = "".join(
        [f"<li>{n['id']} ({n['type']})</li>" for n in nodes_dict]
    )
    rel_items = "".join(
        [
            f"<li>{r['source']} -[{r['type']}]-> {r['target']}</li>"
            for r in rels_dict
        ]
    )
    html = f"""
<div id='data-box-{unique}' style='height:300px; overflow:auto; border:1px solid #ccc; padding:10px; position:relative;'>
  <button id='copy-btn-{unique}' style='position:absolute; top:5px; right:5px;'>Copy</button>
  <h4>Nodes</h4><ul>{node_items}</ul>
  <h4>Relationships</h4><ul>{rel_items}</ul>
</div>
<script>
document.getElementById('copy-btn-{unique}').addEventListener('click', function() {{
  const text = document.getElementById('data-box-{unique}').innerText;
  navigator.clipboard.writeText(text);
}});
</script>
"""
    return html

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
# Remember the input method so users can switch back and forth
if "input_method" not in st.session_state:
    st.session_state.input_method = "テキストをアップロード"
input_method = st.sidebar.radio(
    "入力方法を選択してください:",
    ["テキストをアップロード", "テキストを入力"],
    key="input_method",
)
if input_method == "テキストをアップロード":
    st.session_state.pop("text_input", None)
else:
    st.session_state.pop("text_upload", None)

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

if input_method == "テキストをアップロード":
    uploaded_file = st.sidebar.file_uploader(
        label="ファイルをアップロード",
        type=["txt"],
        key="text_upload",
    )
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        if st.sidebar.button("知識グラフを生成", key="generate_button_upload"):
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
    text = st.sidebar.text_area(
        "テキストを入力してください",
        height=300,
        key="text_input",
    )
    if text:
        if st.sidebar.button("知識グラフを生成", key="generate_button_text"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path, nodes, relationships = generate_knowledge_graph(
                    text, model_name=selected_model
                )
                st.success("知識グラフの生成が完了しました！")
                st.markdown(build_data_html(nodes, relationships), unsafe_allow_html=True)
                with open(output_path, "r", encoding="utf-8") as HtmlFile:
                    components.html(HtmlFile.read(), height=1000)
                generated = True

if not generated and selected_display:
    file_path = os.path.join("out", file_map[selected_display])
    json_path = os.path.splitext(file_path)[0] + ".json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as jf:
            data = json.load(jf)
        nodes = data.get("nodes", [])
        relationships = data.get("relationships", [])
        st.markdown(build_data_html(nodes, relationships), unsafe_allow_html=True)
    with open(file_path, "r", encoding="utf-8") as HtmlFile:
        components.html(HtmlFile.read(), height=1000)
