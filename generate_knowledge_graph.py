from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pyvis.network import Network

from dotenv import load_dotenv
import os
import asyncio
import json
from datetime import datetime

OUTPUT_DIR = "out"


# Load the .env file
load_dotenv()
# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")


# Extract graph data from input text
async def extract_graph_data(text, llm):
    """Asynchronously extract graph data from input text using a given LLM."""
    documents = [Document(page_content=text)]
    graph_transformer = LLMGraphTransformer(llm=llm)
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    return graph_documents


def summarize_text(text, llm, max_chars=25):
    """Summarize the input text within a character limit using the provided LLM."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"次のテキストを{max_chars}文字以内で要約してください。"),
        ("human", "{text}"),
    ])
    summary = llm.invoke(prompt.format(text=text)).content.strip().replace("\n", "")
    return summary[:max_chars]


def visualize_graph(graph_documents, output_file):
    """
    Visualizes a knowledge graph using PyVis based on the extracted graph documents.

    Args:
        graph_documents (list): A list of GraphDocument objects with nodes and relationships.

    Returns:
        tuple: The visualized network graph object, the path to the saved HTML file,
        and the extracted nodes and relationships.
    """
    # Create network
    net = Network(height="1200px", width="100%", directed=True,
                      notebook=False, bgcolor="#222222", font_color="white", filter_menu=True, cdn_resources='remote') 

    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships

    # Build lookup for valid nodes
    node_dict = {node.id: node for node in nodes}
    
    # Filter out invalid edges and collect valid node IDs
    valid_edges = []
    valid_node_ids = set()
    for rel in relationships:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            valid_edges.append(rel)
            valid_node_ids.update([rel.source.id, rel.target.id])

    # Track which nodes are part of any relationship
    connected_node_ids = set()
    for rel in relationships:
        connected_node_ids.add(rel.source.id)
        connected_node_ids.add(rel.target.id)

    # Add valid nodes to the graph
    for node_id in valid_node_ids:
        node = node_dict[node_id]
        try:
            net.add_node(node.id, label=node.id, title=node.type, group=node.type)
        except:
            continue  # Skip node if error occurs

    # Add valid edges to the graph
    for rel in valid_edges:
        try:
            net.add_edge(rel.source.id, rel.target.id, label=rel.type.lower())
        except:
            continue  # Skip edge if error occurs

    # Configure graph layout and physics
    net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            }
        }
    """)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        net.save_graph(output_file)
        print(f"Graph saved to {os.path.abspath(output_file)}")
        return net, output_file
    except Exception as e:
        print(f"Error saving graph: {e}")
        return None


def generate_knowledge_graph(text, model_name="gpt-4o-mini"):
    """
    Generates and visualizes a knowledge graph from input text.

    This function runs the graph extraction asynchronously and then visualizes
    the resulting graph using PyVis.

    Args:
        text (str): Input text to convert into a knowledge graph.
        model_name (str): OpenAI model name used for entity extraction.

    Returns:
        tuple: The visualized network graph object and the saved file path.
    """
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    graph_documents = asyncio.run(extract_graph_data(text, llm))

    summary = summarize_text(text, llm)
    safe_summary = summary.replace(" ", "").replace("_", "").replace("/", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{safe_summary}_{model_name}.html"
    output_file = os.path.join(OUTPUT_DIR, filename)
    net, output_file = visualize_graph(graph_documents, output_file)
    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships
    # Save nodes and relationships to JSON for later display
    json_path = os.path.splitext(output_file)[0] + ".json"
    try:
        nodes_data = [{"id": getattr(n, "id", ""), "type": getattr(n, "type", "")} for n in nodes]
        rels_data = [
            {
                "source": getattr(r.source, "id", ""),
                "target": getattr(r.target, "id", ""),
                "type": getattr(r, "type", ""),
            }
            for r in relationships
        ]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"nodes": nodes_data, "relationships": rels_data}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving json: {e}")
    return net, output_file, nodes, relationships
