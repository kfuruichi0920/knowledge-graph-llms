# Knowledge Graph Generator

A Streamlit application that extract graph data (entities and relationships) from text input using LangChain and OpenAI's GPT models, and generates interactive graphs.
![CleanShot 2025-05-28 at 13 11 46](https://github.com/user-attachments/assets/4fef9158-8dd8-432d-bb8a-b53953a82c6c)

👉 This repo is part of my project tutorial on Youtube:
[![](https://img.youtube.com/vi/O-T_6KOXML4/0.jpg)](https://www.youtube.com/watch?v=O-T_6KOXML4)
日本語での概要は [docs/NEW_PARTICIPANT_GUIDE_JA.md](docs/NEW_PARTICIPANT_GUIDE_JA.md) を参照してください。

## Features

- Two input methods: text upload (.txt files) or direct text input
- Interactive knowledge graph visualization
- Customizable graph display with physics-based layout
- Selectable LLM model from the sidebar
- Entity relationship extraction using a selectable OpenAI GPT model

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Dependencies

The application requires the following Python packages:

- langchain (>= 0.1.0): Core LLM framework
- langchain-experimental (>= 0.0.45): Experimental LangChain features
- langchain-openai (>= 0.1.0): OpenAI integration for LangChain
- python-dotenv (>= 1.0.0): Environment variable support
- pyvis (>= 0.3.2): Graph visualization
- streamlit (>= 1.32.0): Web UI framework

Install all required dependencies using the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

### Setup

1. Clone this repository:
   ```bash
   git clone [repository-url]
   cd knowledge_graph_app_2
   ```

   Note: Replace `[repository-url]` with the actual URL of this repository.

2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

To run the Streamlit app:

```bash
streamlit run app.py
```

This will start the application and open it in your default web browser (typically at http://localhost:8501).

## Usage

1. Select an LLM model from the dropdown at the top of the sidebar
2. Choose your input method from the sidebar (Upload txt or Input text)
3. If uploading a file, select a .txt file from your computer
4. If using direct input, type or paste your text into the text area
5. Click the "Generate Knowledge Graph" button
6. Wait for the graph to be generated (this may take a few moments depending on the length of the text)
7. Explore the interactive knowledge graph:
   - Drag nodes to rearrange the graph
   - Hover over nodes and edges to see additional information
   - Zoom in/out using the mouse wheel
   - Filter the graph for specific nodes and edges.
8. The resulting HTML graph is saved in the `out` directory with a timestamped filename.
9. Previously generated graphs can be selected from a dropdown list and viewed again.

## How It Works

The application uses LangChain's experimental graph transformers with a selectable OpenAI GPT model to:
1. Extract entities from the input text
2. Identify relationships between these entities
3. Generate a graph structure representing this information
4. Visualize the graph using PyVis, a Python interface for the vis.js visualization library

## License

This project is licensed under the MIT License - a permissive open source license that allows for free use, modification, and distribution of the software.

For more details, see the [MIT License](https://opensource.org/licenses/MIT) documentation.
