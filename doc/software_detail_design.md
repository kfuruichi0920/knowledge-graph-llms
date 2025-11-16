# ソフトウェア詳細設計書 (Software Detail Design)

## 1. システムアーキテクチャ

### 1.1 全体構成

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Streamlit UI (app.py)                      │   │
│  │  - Model Selection  - Graph History                │   │
│  │  - Input Method     - Data Display                  │   │
│  │  - File Upload      - Graph Visualization           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    Knowledge Graph Generator                        │   │
│  │    (generate_knowledge_graph.py)                    │   │
│  │                                                      │   │
│  │  - extract_graph_data()    - visualize_graph()     │   │
│  │  - summarize_text()        - generate_knowledge_    │   │
│  │                               graph()               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  LangChain   │  │   OpenAI     │  │     PyVis       │  │
│  │  - LLMGraph  │  │  - ChatOpenAI│  │  - Network      │  │
│  │    Transformer│  │  - API       │  │  - Visualization│  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │    .env      │  │   out/       │  │   Session       │  │
│  │  - API Keys  │  │  - HTML      │  │   State         │  │
│  │              │  │  - JSON      │  │                 │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 コンポーネント間の依存関係

```
app.py
  │
  ├─ imports: generate_knowledge_graph
  ├─ imports: streamlit
  ├─ imports: streamlit.components.v1
  ├─ imports: os, re, json, uuid
  │
  └─ calls: generate_knowledge_graph()
              │
              └─ generate_knowledge_graph.py
                   ├─ imports: langchain_experimental
                   ├─ imports: langchain_core
                   ├─ imports: langchain_openai
                   ├─ imports: pyvis
                   └─ imports: dotenv, os, asyncio, json, datetime
```

## 2. モジュール詳細設計

### 2.1 app.py (Presentation Layer)

#### 2.1.1 モジュール概要
- **役割**: ユーザーインターフェースと制御フロー
- **行数**: 206行
- **主要機能**:
  - UI構築
  - ユーザー入力処理
  - グラフ表示制御
  - セッション管理

#### 2.1.2 関数一覧

##### `_to_node_dict(node)` (app.py:11-31)
```python
def _to_node_dict(node):
    """
    ノード情報を辞書型に変換する関数。

    Args:
        node: Node オブジェクトまたは dict

    Returns:
        dict: {"id": str, "type": str}

    処理フロー:
        1. isinstance() で型チェック
        2. dict型の場合: get() で取得
        3. オブジェクト型の場合: getattr() で取得
        4. デフォルト値: 空文字列
    """
```

**設計上の工夫**:
- 型に依存しない柔軟な実装
- デフォルト値による安全性確保
- LangChain の Node 型と dict 型の両対応

##### `_to_rel_dict(rel)` (app.py:34-62)
```python
def _to_rel_dict(rel):
    """
    リレーションシップ情報を辞書型に変換する関数。

    Args:
        rel: Relationship オブジェクトまたは dict

    Returns:
        dict: {"source": str, "target": str, "type": str}

    処理フロー:
        1. isinstance() で型チェック
        2. dict型の場合: get() で取得
        3. オブジェクト型の場合:
           - source.id, target.id にアクセス
           - getattr() で属性取得
        4. デフォルト値: 空文字列
    """
```

**設計上の工夫**:
- ネストされたオブジェクト構造への対応
- source/target の id 属性アクセス
- 型安全性の確保

##### `build_data_html(nodes, relationships)` (app.py:65-111)
```python
def build_data_html(nodes, relationships):
    """
    ノードとリレーションシップをリスト表示し、コピー用ボタンを付与したHTML
    スニペットを返す。

    Args:
        nodes (list): Node オブジェクトまたは dict のリスト
        relationships (list): Relationship オブジェクトまたは dict のリスト

    Returns:
        str: HTML文字列（JavaScript含む）

    処理フロー:
        1. UUID生成（一意性確保）
        2. ノードを辞書型に変換（リスト内包表記）
        3. リレーションを辞書型に変換（リスト内包表記）
        4. HTML リストアイテム生成
        5. HTML + JavaScript 文字列構築
        6. クリップボードコピー機能実装

    技術的特徴:
        - UUID: 複数グラフ表示時のID競合回避
        - 3段階フォールバック:
          1. Clipboard API (モダンブラウザ)
          2. window.clipboardData (IE)
          3. document.execCommand (レガシー)
    """
```

**設計パターン**:
- Template Method パターン（HTML テンプレート生成）
- Fallback パターン（ブラウザ互換性）

**セキュリティ考慮**:
- XSS対策: ユーザー入力を直接HTMLに埋め込まない（今後の課題）
- UUID使用: DOM ID の一意性保証

#### 2.1.3 メイン処理フロー

```python
# ページ設定 (app.py:113-118)
st.set_page_config(layout="wide", ...)

# タイトル表示 (app.py:120)
st.title("テキストから知識グラフを生成")

# サイドバー: LLMモデル選択 (app.py:122-129)
selected_model = st.sidebar.selectbox(...)

# サイドバー: 入力方法選択 (app.py:131-143)
if "input_method" not in st.session_state:
    st.session_state.input_method = "テキストをアップロード"
input_method = st.sidebar.radio(...)

# 保存済みグラフ取得 (app.py:145-156)
files = [f for f in os.listdir("out") if f.endswith(".html")]
# ファイル名パース: YYYYMMDD_HHMMSS_summary_model.html
info_list = [(timestamp, summary, model, f), ...]
# タイムスタンプ降順ソート

# 入力処理: ファイルアップロード (app.py:160-177)
if input_method == "テキストをアップロード":
    uploaded_file = st.sidebar.file_uploader(...)
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        if st.sidebar.button("知識グラフを生成"):
            with st.spinner("知識グラフを生成しています..."):
                net, output_path, nodes, relationships = \
                    generate_knowledge_graph(text, model_name=selected_model)
            st.success("知識グラフの生成が完了しました！")
            # ノード・リレーション表示
            components.html(build_data_html(nodes, relationships), height=320)
            # グラフ表示
            with open(output_path, "r", encoding="utf-8") as HtmlFile:
                components.html(HtmlFile.read(), height=1000)
            generated = True

# 入力処理: テキスト直接入力 (app.py:178-194)
else:
    text = st.sidebar.text_area(...)
    if text:
        if st.sidebar.button("知識グラフを生成"):
            # 上記と同じ処理

# 履歴表示 (app.py:196-206)
if not generated and selected_display:
    file_path = os.path.join("out", file_map[selected_display])
    json_path = os.path.splitext(file_path)[0] + ".json"
    if os.path.exists(json_path):
        # JSONからノード・リレーション読み込み
        with open(json_path, "r", encoding="utf-8") as jf:
            data = json.load(jf)
        nodes = data.get("nodes", [])
        relationships = data.get("relationships", [])
        components.html(build_data_html(nodes, relationships), height=320)
    # HTMLグラフ表示
    with open(file_path, "r", encoding="utf-8") as HtmlFile:
        components.html(HtmlFile.read(), height=1000)
```

**状態管理設計**:
- `st.session_state.input_method`: 入力方法の永続化
- `generated` フラグ: 新規生成と履歴表示の排他制御

### 2.2 generate_knowledge_graph.py (Business Logic Layer)

#### 2.2.1 モジュール概要
- **役割**: ナレッジグラフ生成のコアロジック
- **行数**: 157行
- **主要機能**:
  - テキストからのグラフデータ抽出
  - テキスト要約
  - グラフ可視化
  - ファイル保存

#### 2.2.2 定数定義

```python
OUTPUT_DIR = "out"  # 出力ディレクトリ (generate_knowledge_graph.py:13)
```

#### 2.2.3 環境変数読み込み

```python
# generate_knowledge_graph.py:16-19
load_dotenv()  # .envファイルを読み込む
api_key = os.getenv("OPENAI_API_KEY")  # 環境変数からAPIキーを取得
```

**セキュリティ設計**:
- API キーをハードコーディングしない
- `.env` ファイルは `.gitignore` で除外
- 環境変数経由でキー管理

#### 2.2.4 関数詳細設計

##### `extract_graph_data(text, llm)` (generate_knowledge_graph.py:23-28)

```python
async def extract_graph_data(text, llm):
    """
    指定したLLMを使って入力テキストから非同期でグラフデータを抽出する.

    Args:
        text (str): 入力テキスト
        llm (ChatOpenAI): LangChain ChatOpenAI インスタンス

    Returns:
        list[GraphDocument]: グラフドキュメントのリスト

    処理フロー:
        1. Document オブジェクト生成（LangChain）
        2. LLMGraphTransformer インスタンス化
        3. aconvert_to_graph_documents() 非同期呼び出し
        4. グラフドキュメント返却

    技術的特徴:
        - async/await 非同期処理
        - LangChain の Graph Transformer 活用
        - LLM を使ったエンティティ・関係抽出
    """
    documents = [Document(page_content=text)]
    graph_transformer = LLMGraphTransformer(llm=llm)
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    return graph_documents
```

**設計パターン**:
- Strategy パターン（LLM を差し替え可能）
- Async パターン（非同期処理）

**データフロー**:
```
text (str)
  ↓
Document(page_content=text)
  ↓
LLMGraphTransformer.aconvert_to_graph_documents()
  ↓ (OpenAI API 呼び出し)
GraphDocument[
  nodes: [Node(id, type), ...],
  relationships: [Relationship(source, target, type), ...]
]
```

##### `summarize_text(text, llm, max_chars=25)` (generate_knowledge_graph.py:31-38)

```python
def summarize_text(text, llm, max_chars=25):
    """
    指定したLLMを使い、入力テキストを最大文字数以内で要約する.

    Args:
        text (str): 入力テキスト
        llm (ChatOpenAI): LangChain ChatOpenAI インスタンス
        max_chars (int): 最大文字数（デフォルト: 25）

    Returns:
        str: 要約テキスト（max_chars 文字以内）

    処理フロー:
        1. ChatPromptTemplate 生成
           - System: "次のテキストを{max_chars}文字以内で要約してください。"
           - Human: "{text}"
        2. LLM 呼び出し（prompt.format() でテンプレート展開）
        3. 改行除去（strip().replace("\n", "")）
        4. 文字数制限（[:max_chars]）
        5. 要約返却

    用途:
        - ファイル名生成（安全な文字列）
        - グラフ識別用
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"次のテキストを{max_chars}文字以内で要約してください。"),
        ("human", "{text}"),
    ])
    summary = llm.invoke(prompt.format(text=text)).content.strip().replace("\n", "")
    return summary[:max_chars]
```

**設計上の工夫**:
- ファイル名安全性: 改行除去、文字数制限
- LLM 活用: 意味のある要約生成
- Template パターン: プロンプトテンプレート化

##### `visualize_graph(graph_documents, output_file)` (generate_knowledge_graph.py:41-115)

```python
def visualize_graph(graph_documents, output_file):
    """
    抽出したグラフドキュメントをもとにPyVisでナレッジグラフを可視化する。

    Args:
        graph_documents (list[GraphDocument]): グラフドキュメントリスト
        output_file (str): 出力HTMLファイルパス

    Returns:
        tuple: (Network, str)
            - Network: PyVis ネットワークオブジェクト
            - str: 保存したファイルパス

    処理フロー:
        1. PyVis Network インスタンス生成
           - directed=True (有向グラフ)
           - bgcolor="#222222" (ダーク背景)
           - font_color="white"
           - filter_menu=True (フィルター有効)

        2. ノード・リレーション取得
           nodes = graph_documents[0].nodes
           relationships = graph_documents[0].relationships

        3. 有効なノードのルックアップ作成
           node_dict = {node.id: node for node in nodes}

        4. 無効なエッジ除外（両端ノードが存在するもののみ）
           for rel in relationships:
               if rel.source.id in node_dict and rel.target.id in node_dict:
                   valid_edges.append(rel)

        5. ノードをグラフに追加
           for node in valid_nodes:
               try:
                   net.add_node(node.id, label=node.id,
                                title=node.type, group=node.type)
               except:
                   continue  # エラー時スキップ

        6. エッジをグラフに追加
           for rel in valid_edges:
               try:
                   net.add_edge(rel.source.id, rel.target.id,
                                label=rel.type.lower())
               except:
                   continue  # エラー時スキップ

        7. 物理演算設定
           ForceAtlas2Based ソルバー:
             - gravitationalConstant: -100 (斥力)
             - centralGravity: 0.01 (中心引力)
             - springLength: 200 (バネ長)
             - springConstant: 0.08 (バネ定数)
             - minVelocity: 0.75 (最小速度)

        8. 出力ディレクトリ作成（存在しない場合）
           os.makedirs(OUTPUT_DIR, exist_ok=True)

        9. HTMLファイル保存
           net.save_graph(output_file)

        10. エラーハンドリング
            try-except でファイル保存エラー捕捉

    エラー処理戦略:
        - ノード追加失敗: continue でスキップ
        - エッジ追加失敗: continue でスキップ
        - ファイル保存失敗: エラーメッセージ出力、None 返却
    """
```

**データ検証ロジック**:
```python
# 有効なノードのルックアップ (generate_knowledge_graph.py:59-60)
node_dict = {node.id: node for node in nodes}

# 無効なエッジ除外 (generate_knowledge_graph.py:62-68)
valid_edges = []
valid_node_ids = set()
for rel in relationships:
    if rel.source.id in node_dict and rel.target.id in node_dict:
        valid_edges.append(rel)
        valid_node_ids.update([rel.source.id, rel.target.id])
```

**物理演算パラメータ設計** (generate_knowledge_graph.py:92-105):
```json
{
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -100,  // ノード間斥力（離す）
      "centralGravity": 0.01,         // 中心への引力（弱い）
      "springLength": 200,            // エッジの自然長
      "springConstant": 0.08          // エッジのバネ強度
    },
    "minVelocity": 0.75,              // 停止判定速度
    "solver": "forceAtlas2Based"
  }
}
```

**設計意図**:
- ForceAtlas2Based: 大規模グラフに適したアルゴリズム
- 高い斥力: ノードの重なりを防ぐ
- 低い中心引力: グラフの広がりを許容
- 適度なバネ長: 可読性確保

##### `generate_knowledge_graph(text, model_name="gpt-4o-mini")` (generate_knowledge_graph.py:117-157)

```python
def generate_knowledge_graph(text, model_name="gpt-4o-mini"):
    """
    入力テキストからナレッジグラフを生成し可視化する。

    Args:
        text (str): 入力テキスト
        model_name (str): OpenAI モデル名（デフォルト: gpt-4o-mini）

    Returns:
        tuple: (Network, str, list, list)
            - Network: PyVis ネットワークオブジェクト
            - str: 保存したHTMLファイルパス
            - list: ノードリスト
            - list: リレーションシップリスト

    処理フロー:
        1. LLM インスタンス生成
           llm = ChatOpenAI(temperature=0, model_name=model_name)

        2. グラフデータ抽出（非同期実行）
           graph_documents = asyncio.run(extract_graph_data(text, llm))

        3. テキスト要約
           summary = summarize_text(text, llm)
           safe_summary = summary.replace(" ", "").replace("_", "")
                                 .replace("/", "")

        4. ファイル名生成
           timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
           filename = f"{timestamp}_{safe_summary}_{model_name}.html"
           output_file = os.path.join(OUTPUT_DIR, filename)

        5. グラフ可視化
           net, output_file = visualize_graph(graph_documents, output_file)

        6. ノード・リレーション取得
           nodes = graph_documents[0].nodes
           relationships = graph_documents[0].relationships

        7. JSON保存
           json_path = os.path.splitext(output_file)[0] + ".json"
           nodes_data = [{"id": n.id, "type": n.type} for n in nodes]
           rels_data = [{
               "source": r.source.id,
               "target": r.target.id,
               "type": r.type
           } for r in relationships]
           json.dump({"nodes": nodes_data, "relationships": rels_data},
                     f, ensure_ascii=False, indent=2)

        8. エラーハンドリング
           try-except でJSON保存エラー捕捉

        9. 戻り値返却
           return net, output_file, nodes, relationships

    設計上の重要ポイント:
        - temperature=0: 決定的な出力（再現性）
        - asyncio.run(): 非同期処理の同期的実行
        - ensure_ascii=False: 日本語保持
        - indent=2: 読みやすさ
    """
```

**ファイル命名戦略**:
```python
# タイムスタンプ生成 (generate_knowledge_graph.py:135)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 安全な要約文字列 (generate_knowledge_graph.py:134)
safe_summary = summary.replace(" ", "").replace("_", "").replace("/", "")

# ファイル名構築 (generate_knowledge_graph.py:136)
filename = f"{timestamp}_{safe_summary}_{model_name}.html"
```

**一意性保証**:
- タイムスタンプ（秒精度）
- ファイル名から空白・記号除去
- モデル名含む（同時刻の異なるモデル実行を区別）

**JSONデータ構造**:
```json
{
  "nodes": [
    {"id": "Entity1", "type": "Person"},
    {"id": "Entity2", "type": "Organization"}
  ],
  "relationships": [
    {
      "source": "Entity1",
      "target": "Entity2",
      "type": "WORKS_FOR"
    }
  ]
}
```

## 3. データモデル

### 3.1 Node (ノード)

```python
class Node:
    id: str        # ノードの一意識別子
    type: str      # ノードのタイプ（Person, Organization, Location, etc.）
```

**例**:
```json
{"id": "Albert Einstein", "type": "Person"}
{"id": "Princeton University", "type": "Organization"}
```

### 3.2 Relationship (リレーションシップ)

```python
class Relationship:
    source: Node   # 始点ノード
    target: Node   # 終点ノード
    type: str      # 関係の種類
```

**例**:
```json
{
  "source": "Albert Einstein",
  "target": "Princeton University",
  "type": "WORKED_AT"
}
```

### 3.3 GraphDocument

```python
class GraphDocument:
    nodes: list[Node]              # ノードのリスト
    relationships: list[Relationship]  # リレーションシップのリスト
    source: Document               # 元のドキュメント
```

### 3.4 ファイルシステムデータ

#### 3.4.1 HTMLファイル
- **パス**: `out/{timestamp}_{summary}_{model}.html`
- **内容**: PyVis生成のインタラクティブグラフ
- **形式**: 自己完結型HTML（JavaScript、CSS含む）

#### 3.4.2 JSONファイル
- **パス**: `out/{timestamp}_{summary}_{model}.json`
- **内容**: ノード・リレーションシップのメタデータ
- **形式**: UTF-8、インデント2、日本語対応

## 4. シーケンス図

### 4.1 グラフ生成フロー

```
User        app.py           generate_knowledge_graph.py    OpenAI API    FileSystem
 │             │                         │                      │             │
 │─テキスト入力─>│                         │                      │             │
 │             │                         │                      │             │
 │─生成ボタン──>│                         │                      │             │
 │             │                         │                      │             │
 │             │─generate_knowledge_graph()─>│                   │             │
 │             │                         │                      │             │
 │             │                         │─ChatOpenAI()─────────>│             │
 │             │                         │                      │             │
 │             │                         │─extract_graph_data()─>│             │
 │             │                         │  (async)             │             │
 │             │                         │<─GraphDocument───────│             │
 │             │                         │                      │             │
 │             │                         │─summarize_text()─────>│             │
 │             │                         │<─summary─────────────│             │
 │             │                         │                      │             │
 │             │                         │─visualize_graph()────────────────> │
 │             │                         │                      │   save HTML │
 │             │                         │<─────────────────────────────────  │
 │             │                         │                      │             │
 │             │                         │─json.dump()──────────────────────> │
 │             │                         │                      │   save JSON │
 │             │                         │<─────────────────────────────────  │
 │             │                         │                      │             │
 │             │<─(net, path, nodes, rels)─│                    │             │
 │             │                         │                      │             │
 │             │─build_data_html()       │                      │             │
 │             │<─HTML with Copy button  │                      │             │
 │             │                         │                      │             │
 │             │─components.html()       │                      │             │
 │<─ノード一覧──│                         │                      │             │
 │             │                         │                      │             │
 │             │─read HTML file──────────────────────────────────────────────>│
 │             │<─HTML content───────────────────────────────────────────────│
 │             │                         │                      │             │
 │             │─components.html()       │                      │             │
 │<─グラフ表示──│                         │                      │             │
```

### 4.2 履歴表示フロー

```
User        app.py           FileSystem
 │             │                 │
 │─グラフ選択─>│                 │
 │             │                 │
 │             │─read JSON───────>│
 │             │<─nodes, rels────│
 │             │                 │
 │             │─build_data_html()
 │<─ノード一覧──│                 │
 │             │                 │
 │             │─read HTML───────>│
 │             │<─HTML content───│
 │             │                 │
 │<─グラフ表示──│                 │
```

## 5. エラーハンドリング戦略

### 5.1 エラー分類

| エラータイプ | 発生箇所 | 処理方針 |
|-------------|---------|---------|
| ノード追加失敗 | `visualize_graph()` | スキップ（continue） |
| エッジ追加失敗 | `visualize_graph()` | スキップ（continue） |
| ファイル保存失敗 | `visualize_graph()` | エラーログ出力、None返却 |
| JSON保存失敗 | `generate_knowledge_graph()` | エラーログ出力、処理継続 |
| API呼び出し失敗 | `extract_graph_data()`, `summarize_text()` | 例外伝播（未処理） |

### 5.2 部分的失敗の許容

**設計思想**: "Best Effort" アプローチ
- グラフの一部が無効でも、可能な限り表示
- エラーが発生しても処理を継続
- ユーザーに部分的な結果を提供

**実装例** (generate_knowledge_graph.py:79-89):
```python
for node_id in valid_node_ids:
    node = node_dict[node_id]
    try:
        net.add_node(node.id, label=node.id, title=node.type, group=node.type)
    except:
        continue  # エラーが発生した場合はノードをスキップ
```

### 5.3 エラーログ

```python
# ファイル保存エラー (generate_knowledge_graph.py:112-113)
except Exception as e:
    print(f"グラフ保存時のエラー: {e}")

# JSON保存エラー (generate_knowledge_graph.py:155-156)
except Exception as e:
    print(f"json保存時のエラー: {e}")
```

**改善案**:
- ロギングライブラリ使用（logging module）
- エラーレベル分類（ERROR, WARNING, INFO）
- ログファイル出力

## 6. パフォーマンス設計

### 6.1 ボトルネック分析

```
処理時間の内訳（推定）:
┌────────────────────────────────────────────┐
│ OpenAI API 呼び出し         │ ██████████████████████████████████████ 80% (約7-8秒)
│ グラフ可視化（PyVis）       │ ████ 10% (約0.5-1秒)
│ ファイル保存               │ ██ 5% (約0.2-0.5秒)
│ その他（UI、データ変換）    │ ██ 5% (約0.2-0.5秒)
└────────────────────────────────────────────┘
```

**主要ボトルネック**: OpenAI API呼び出し
- `extract_graph_data()`: グラフ抽出（最も時間がかかる）
- `summarize_text()`: テキスト要約

### 6.2 非同期処理

```python
# 非同期処理の実装 (generate_knowledge_graph.py:23-28)
async def extract_graph_data(text, llm):
    ...
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    return graph_documents

# 同期コンテキストでの実行 (generate_knowledge_graph.py:131)
graph_documents = asyncio.run(extract_graph_data(text, llm))
```

**設計意図**:
- LangChain の非同期APIを活用
- 将来的なバッチ処理拡張に備える
- 現状は単一テキスト処理のため効果限定的

**改善案**:
```python
# 複数テキストの並列処理（将来）
async def process_multiple_texts(texts, llm):
    tasks = [extract_graph_data(text, llm) for text in texts]
    results = await asyncio.gather(*tasks)
    return results
```

### 6.3 キャッシング戦略

**現状**: キャッシングなし

**改善案**:
1. **LLM応答キャッシュ**:
   - 同じテキストの再処理を回避
   - Redis、ローカルファイルキャッシュ

2. **グラフレンダリングキャッシュ**:
   - 同じグラフデータの再可視化を回避
   - メモリ内キャッシュ

3. **ファイルシステムキャッシュ**:
   - 既存のHTML/JSONファイルを再利用（現在実装済み）

## 7. セキュリティ設計

### 7.1 脅威モデル

| 脅威 | リスクレベル | 対策状況 |
|------|-------------|---------|
| API キー漏洩 | 高 | 実装済み（環境変数） |
| XSS攻撃 | 中 | 未実装 |
| パストラバーサル | 中 | 部分的実装 |
| ファイルアップロード攻撃 | 低 | Streamlit制限に依存 |
| DoS攻撃 | 低 | 未対策 |

### 7.2 実装済みセキュリティ対策

#### 7.2.1 API キー管理
```python
# generate_knowledge_graph.py:16-19
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

**ベストプラクティス**:
- `.env` ファイルを `.gitignore` に追加
- 環境変数経由でキー提供
- ハードコーディング禁止

#### 7.2.2 ファイルパス安全性
```python
# app.py:197
file_path = os.path.join("out", file_map[selected_display])

# generate_knowledge_graph.py:137
output_file = os.path.join(OUTPUT_DIR, filename)
```

**対策**:
- `os.path.join()` 使用（パス結合の安全性）
- 出力ディレクトリを `out/` に限定

### 7.3 未実装のセキュリティ対策

#### 7.3.1 XSS (Cross-Site Scripting)
**脆弱性**:
```python
# app.py:76-82
node_items = "".join([f"<li>{n['id']} ({n['type']})</li>" for n in nodes_dict])
```

**問題点**: ユーザー入力（ノードID、タイプ）をエスケープせずにHTML埋め込み

**改善案**:
```python
import html

node_items = "".join([
    f"<li>{html.escape(n['id'])} ({html.escape(n['type'])})</li>"
    for n in nodes_dict
])
```

#### 7.3.2 パストラバーサル
**脆弱性**:
```python
# app.py:146-156
files = [f for f in os.listdir("out") if f.endswith(".html")]
```

**問題点**: ファイル名の検証不足

**改善案**:
```python
import os.path

def is_safe_filename(filename):
    # ".." を含まない、out/ ディレクトリ内のファイルのみ許可
    return ".." not in filename and os.path.abspath(
        os.path.join("out", filename)
    ).startswith(os.path.abspath("out"))
```

#### 7.3.3 入力バリデーション
**現状**: テキスト長、ファイルサイズの明示的検証なし

**改善案**:
```python
MAX_TEXT_LENGTH = 100000  # 100KB

def validate_text(text):
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"テキストが長すぎます（最大{MAX_TEXT_LENGTH}文字）")
    return text
```

## 8. テスト戦略

### 8.1 単体テスト (Unit Tests)

#### 8.1.1 テスト対象関数

| 関数 | テストケース |
|------|-------------|
| `_to_node_dict()` | - dict型入力<br>- オブジェクト型入力<br>- 属性なしの場合 |
| `_to_rel_dict()` | - dict型入力<br>- オブジェクト型入力<br>- ネストされた属性 |
| `build_data_html()` | - 空リスト<br>- 通常データ<br>- UUID一意性 |
| `summarize_text()` | - 文字数制限<br>- 改行除去<br>- 特殊文字処理 |

**テスト例**:
```python
import unittest

class TestNodeConversion(unittest.TestCase):
    def test_to_node_dict_with_dict(self):
        node = {"id": "test", "type": "Person"}
        result = _to_node_dict(node)
        self.assertEqual(result, {"id": "test", "type": "Person"})

    def test_to_node_dict_with_object(self):
        class MockNode:
            id = "test"
            type = "Person"
        result = _to_node_dict(MockNode())
        self.assertEqual(result, {"id": "test", "type": "Person"})

    def test_to_node_dict_missing_attributes(self):
        result = _to_node_dict({})
        self.assertEqual(result, {"id": "", "type": ""})
```

### 8.2 統合テスト (Integration Tests)

#### 8.2.1 テストシナリオ

1. **エンドツーエンドテスト**:
   ```
   テキスト入力 → グラフ生成 → ファイル保存 → 表示
   ```

2. **API統合テスト**:
   ```
   OpenAI API 呼び出し → グラフデータ抽出 → 検証
   ```

3. **ファイルシステムテスト**:
   ```
   HTML保存 → JSON保存 → 読み込み → 検証
   ```

**テスト例**:
```python
class TestKnowledgeGraphGeneration(unittest.TestCase):
    def test_generate_and_save(self):
        text = "Albert Einstein worked at Princeton University."
        net, output_path, nodes, relationships = generate_knowledge_graph(text)

        # ファイル存在確認
        self.assertTrue(os.path.exists(output_path))

        # JSON存在確認
        json_path = os.path.splitext(output_path)[0] + ".json"
        self.assertTrue(os.path.exists(json_path))

        # ノード検証
        self.assertGreater(len(nodes), 0)

        # リレーション検証
        self.assertGreater(len(relationships), 0)

        # クリーンアップ
        os.remove(output_path)
        os.remove(json_path)
```

### 8.3 UI テスト

**ツール**: Streamlit テストフレームワーク（`streamlit.testing.v1`）

**テストケース**:
1. モデル選択UIの動作
2. 入力方法切り替えの動作
3. ファイルアップロードの動作
4. グラフ表示の動作

## 9. デプロイメント設計

### 9.1 ローカル実行

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
echo "OPENAI_API_KEY=your_api_key_here" > .env

# アプリケーション起動
streamlit run app.py
```

### 9.2 Streamlit Cloud デプロイ

**手順**:
1. GitHub リポジトリにプッシュ
2. Streamlit Cloud 接続
3. Secrets に `OPENAI_API_KEY` 設定
4. デプロイ

**制約**:
- `out/` ディレクトリは永続化されない（セッション終了で削除）
- ファイルアップロードサイズ制限（200MB）

### 9.3 Docker デプロイ

**Dockerfile 例**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 出力ディレクトリ作成
RUN mkdir -p out

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**起動**:
```bash
docker build -t knowledge-graph-llms .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key knowledge-graph-llms
```

## 10. 拡張性設計

### 10.1 新しいLLMプロバイダ対応

**現状**: OpenAI専用

**拡張方法**:
```python
# generate_knowledge_graph.py
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

def create_llm(provider, model_name):
    if provider == "openai":
        return ChatOpenAI(temperature=0, model_name=model_name)
    elif provider == "anthropic":
        return ChatAnthropic(temperature=0, model=model_name)
    elif provider == "google":
        return ChatGoogleGenerativeAI(temperature=0, model=model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
```

### 10.2 カスタムグラフレイアウト

**現状**: ForceAtlas2Based のみ

**拡張方法**:
```python
def visualize_graph(graph_documents, output_file, layout="force_atlas"):
    net = Network(...)

    if layout == "force_atlas":
        net.set_options("""{"physics": {"solver": "forceAtlas2Based"}}""")
    elif layout == "hierarchical":
        net.set_options("""{"layout": {"hierarchical": true}}""")
    elif layout == "circular":
        net.set_options("""{"layout": {"improvedLayout": false}}""")

    ...
```

### 10.3 グラフエクスポート機能

**要望**: PNG, SVG, PDF 出力

**実装案**:
```python
# Selenium を使ったスクリーンショット
from selenium import webdriver

def export_graph_as_image(html_path, output_path, format="png"):
    driver = webdriver.Chrome()
    driver.get(f"file://{os.path.abspath(html_path)}")
    driver.save_screenshot(output_path)
    driver.quit()
```

### 10.4 バッチ処理

**要望**: 複数ファイル一括処理

**実装案**:
```python
async def batch_generate_graphs(texts, llm):
    tasks = [extract_graph_data(text, llm) for text in texts]
    all_graph_documents = await asyncio.gather(*tasks)

    results = []
    for i, graph_docs in enumerate(all_graph_documents):
        # 各グラフを個別に可視化・保存
        net, path = visualize_graph(graph_docs, f"out/batch_{i}.html")
        results.append((net, path))

    return results
```

## 11. 依存関係

### 11.1 主要ライブラリ

| ライブラリ | バージョン | 用途 |
|-----------|-----------|------|
| streamlit | - | Web UI フレームワーク |
| langchain-experimental | - | LLMGraphTransformer |
| langchain-core | - | Document, Prompts |
| langchain-openai | - | ChatOpenAI |
| pyvis | - | グラフ可視化 |
| python-dotenv | - | 環境変数管理 |

### 11.2 依存関係グラフ

```
app.py
  ├── streamlit
  ├── generate_knowledge_graph (ローカルモジュール)
  └── os, re, json, uuid (標準ライブラリ)

generate_knowledge_graph.py
  ├── langchain-experimental
  │     └── langchain-core
  ├── langchain-openai
  │     └── langchain-core
  ├── pyvis
  ├── python-dotenv
  └── os, asyncio, json, datetime (標準ライブラリ)
```

## 12. 設定管理

### 12.1 環境変数

| 変数名 | 必須 | 説明 | デフォルト |
|--------|-----|------|-----------|
| OPENAI_API_KEY | Yes | OpenAI API キー | - |

### 12.2 定数

```python
# generate_knowledge_graph.py
OUTPUT_DIR = "out"  # 出力ディレクトリ

# app.py
model_options = [
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4.1",
    "gpt-4o-mini",
    "gpt-4o",
]
```

**改善案**: 設定ファイル化
```yaml
# config.yaml
output:
  directory: "out"

models:
  - name: "gpt-4.1-mini"
    provider: "openai"
  - name: "gpt-4.1-nano"
    provider: "openai"

visualization:
  physics:
    solver: "forceAtlas2Based"
    gravitationalConstant: -100
```

## 13. ロギング設計

### 13.1 現状

```python
# generate_knowledge_graph.py:110, 156
print(f"グラフを保存しました: {os.path.abspath(output_file)}")
print(f"グラフ保存時のエラー: {e}")
print(f"json保存時のエラー: {e}")
```

### 13.2 改善案

```python
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("knowledge_graph.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用例
logger.info(f"グラフを保存しました: {os.path.abspath(output_file)}")
logger.error(f"グラフ保存時のエラー: {e}", exc_info=True)
```

## 14. バージョン管理

### 14.1 Git履歴

```
b5424d7 - コメント追加
2a60bbb - コードコメントの日本語化
7121d53 - Merge pull request #11 (コピー機能修正)
53d65f2 - Enable clipboard copy
cd5df39 - Merge pull request #10 (テキスト選択後のアップロード)
```

### 14.2 セマンティックバージョニング

**推奨バージョン管理**:
- メジャー: 破壊的変更
- マイナー: 新機能追加
- パッチ: バグフィックス

**現状**: バージョン番号なし

**改善案**:
```python
# app.py
__version__ = "1.0.0"

st.sidebar.text(f"Version: {__version__}")
```

---

**文書管理情報**
- **文書ID**: SDD-KG-LLM-001
- **バージョン**: 1.0
- **最終更新**: 2025-11-16
- **ベースコミット**: b5424d7
- **総コード行数**: 363行 (app.py: 206, generate_knowledge_graph.py: 157)
- **関連文書**:
  - UI設計書: `doc/user_interface_design.md`
  - 要件定義書: `doc/software_requirement.md`
