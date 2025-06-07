# リポジトリ概要 (日本語)

このリポジトリは、テキストからエンティティと関係を抽出し、ナレッジグラフを生成して表示する Streamlit アプリケーションです。新規参加者が全体像を素早く理解できるよう、主要なファイル構成と利用手順をまとめます。

## 主なファイル

- **README.md**
  - プロジェクトの概要や依存パッケージが記載されています。*Features*、*Installation*、*Usage* などの項目で基本的な使い方を確認できます。
- **app.py**
  - Streamlit による Web アプリケーションのエントリポイントです。サイドバーからテキストファイルのアップロードまたは直接入力を選び、「Generate Knowledge Graph」ボタンでグラフ生成処理を実行します。
- **generate_knowledge_graph.py**
  - LangChain と OpenAI API を用いてエンティティと関係を抽出し、PyVis でナレッジグラフを描画・保存します。
- **requirements.txt**
  - 必要な Python パッケージの一覧です。LangChain 系や Streamlit、PyVis、python-dotenv などが含まれます。

## 基本的な使い方

1. Python 環境を用意し、`requirements.txt` を使って依存パッケージをインストールします。
2. ルートディレクトリに `.env` ファイルを作成し、`OPENAI_API_KEY` を設定します。
3. `streamlit run app.py` を実行するとアプリが起動します。
4. ブラウザ (通常は `http://localhost:8501`) でアプリを開き、サイドバー上部のドロップダウンで使用する LLM モデルを選択します（デフォルトは `gpt-4o-mini`）。
5. テキストファイルをアップロードするか直接入力してグラフを生成します。
6. 生成したグラフは `out` フォルダに保存され、サイドバーのドロップダウンから再表示できます。

## ディレクトリ構成例

```
knowledge-graph-llms/
├── app.py
├── generate_knowledge_graph.py
├── out/                   # 生成されたグラフの保存先
├── knowledge_graph.ipynb  # Jupyter ノートブック版
├── requirements.txt
└── README.md
```

まずは上記ファイルを読み、実際にアプリを起動して動作を確認すると、コード全体の流れをつかみやすくなります。
