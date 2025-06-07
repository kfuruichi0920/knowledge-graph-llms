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


# .envファイルを読み込む
load_dotenv()
# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")


# 入力テキストからグラフデータを抽出
async def extract_graph_data(text, llm):
    """指定したLLMを使って入力テキストから非同期でグラフデータを抽出する."""
    documents = [Document(page_content=text)]
    graph_transformer = LLMGraphTransformer(llm=llm)
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    return graph_documents


def summarize_text(text, llm, max_chars=25):
    """指定したLLMを使い、入力テキストを最大文字数以内で要約する."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"次のテキストを{max_chars}文字以内で要約してください。"),
        ("human", "{text}"),
    ])
    summary = llm.invoke(prompt.format(text=text)).content.strip().replace("\n", "")
    return summary[:max_chars]


def visualize_graph(graph_documents, output_file):
    """
    抽出したグラフドキュメントをもとにPyVisでナレッジグラフを可視化する。

    引数:
        graph_documents (list): ノードとリレーションシップを持つGraphDocumentオブジェクトのリスト。

    戻り値:
        tuple: 可視化したネットワークグラフオブジェクト、保存したHTMLファイルのパス、
        抽出したノードとリレーションシップ。
    """
    # ネットワークを作成
    net = Network(height="800px", width="100%", directed=True,
                      notebook=False, bgcolor="#222222", font_color="white", filter_menu=True, cdn_resources='remote') 

    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships

    # 有効なノードのルックアップを作成
    node_dict = {node.id: node for node in nodes}
    
    # 無効なエッジを除外し、有効なノードIDを収集
    valid_edges = []
    valid_node_ids = set()
    for rel in relationships:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            valid_edges.append(rel)
            valid_node_ids.update([rel.source.id, rel.target.id])

    # いずれかのリレーションシップに含まれるノードIDを追跡
    connected_node_ids = set()
    for rel in relationships:
        connected_node_ids.add(rel.source.id)
        connected_node_ids.add(rel.target.id)

    # 有効なノードをグラフに追加
    for node_id in valid_node_ids:
        node = node_dict[node_id]
        try:
            net.add_node(node.id, label=node.id, title=node.type, group=node.type)
        except:
            continue  # エラーが発生した場合はノードをスキップ

    # 有効なエッジをグラフに追加
    for rel in valid_edges:
        try:
            net.add_edge(rel.source.id, rel.target.id, label=rel.type.lower())
        except:
            continue  # エラーが発生した場合はエッジをスキップ

    # グラフのレイアウトと物理演算を設定
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
        print(f"グラフを保存しました: {os.path.abspath(output_file)}")
        return net, output_file
    except Exception as e:
        print(f"グラフ保存時のエラー: {e}")
        return None


def generate_knowledge_graph(text, model_name="gpt-4o-mini"):
    """
    入力テキストからナレッジグラフを生成し可視化する。

    この関数はグラフ抽出を非同期で実行し、PyVisでグラフを可視化する。

    引数:
        text (str): ナレッジグラフに変換する入力テキスト。
        model_name (str): エンティティ抽出に使用するOpenAIモデル名。

    戻り値:
        tuple: 可視化したネットワークグラフオブジェクトと保存ファイルパス。
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
    # ノードとリレーションシップをJSONで保存（後で表示用）
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
        print(f"json保存時のエラー: {e}")
    return net, output_file, nodes, relationships
