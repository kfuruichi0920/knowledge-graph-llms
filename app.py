# Import necessary modules
import streamlit as st
import streamlit.components.v1 as components  # For embedding custom HTML
from generate_knowledge_graph import generate_knowledge_graph

# Set up Streamlit page configuration
st.set_page_config(
    page_icon=None, 
    layout="wide",  # Use wide layout for better graph display
    initial_sidebar_state="auto", 
    menu_items=None
)

# Set the title of the app in Japanese
st.title("テキストから知識グラフを生成")

# Sidebar section for user input method
st.sidebar.title("入力ドキュメント")
input_method = st.sidebar.radio(
    "入力方法を選択してください:",
    ["テキストをアップロード", "テキストを入力"],  # Options for uploading a file or manually inputting text
)

# Case 1: User chooses to upload a .txt file
if input_method == "Upload txt":
    # File uploader widget in the sidebar
    uploaded_file = st.sidebar.file_uploader(label="ファイルをアップロード", type=["txt"])
    
    if uploaded_file is not None:
        # Read the uploaded file content and decode it as UTF-8 text
        text = uploaded_file.read().decode("utf-8")
 
        # Button to generate the knowledge graph
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                # Call the function to generate the graph from the text
                net = generate_knowledge_graph(text)
                st.success("知識グラフの生成が完了しました！")
                
                # Save the graph to an HTML file
                output_file = "knowledge_graph.html"
                net.save_graph(output_file) 

                # Open the HTML file and display it within the Streamlit app
                HtmlFile = open(output_file, 'r', encoding='utf-8')
                components.html(HtmlFile.read(), height=1000)

# Case 2: User chooses to directly input text
else:
    # Text area for manual input
    text = st.sidebar.text_area("テキストを入力してください", height=300)

    if text:  # Check if the text area is not empty
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                # Call the function to generate the graph from the input text
                net = generate_knowledge_graph(text)
                st.success("知識グラフの生成が完了しました！")
                
                # Save the graph to an HTML file
                output_file = "knowledge_graph.html"
                net.save_graph(output_file) 

                # Open the HTML file and display it within the Streamlit app
                HtmlFile = open(output_file, 'r', encoding='utf-8')
                components.html(HtmlFile.read(), height=1000)
