# Mini-Search — Information Retrieval Search Engine

A lightweight document search engine that retrieves relevant documents using **TF-IDF weighting** and **cosine similarity**.

## Features

- **Document indexing:** Stores document information and builds an inverted index for efficient retrieval.
- **Text preprocessing:** Processes text before indexing and searching.
- **Relevance ranking:** Uses TF-IDF and cosine similarity to rank search results.
- **REST API:** Provides endpoints for document management and search using FastAPI.
- **Persistent storage:** Uses SQLite to store document data.
- **Web interface:** Provides a frontend built with HTML, CSS, and JavaScript.
- **Automated tests:** Includes tests for verifying application functionality.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite |
| Information Retrieval | Inverted Index, TF-IDF, Cosine Similarity |
| Text Processing | NLTK |
| Frontend | HTML, CSS, JavaScript |
| Testing | Pytest |

## Project Structure

```text
Mini-Search/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── search_engine.py
│   └── ...
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/
├── data/
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13 or a compatible Python version
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Konkyana-Samith/Mini-Search.git
cd Mini-Search
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

Open the local address shown in your terminal. FastAPI's interactive API documentation is normally available at:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check application health |
| POST | `/documents` | Add a document |
| GET | `/search?q=your_query&k=10` | Search and rank documents |
| GET | `/documents/{document_id}` | Retrieve a document |
| DELETE | `/documents/{document_id}` | Delete a document |

## Run Tests

```bash
pytest
```

## How It Works

1. Documents are added to the system and stored in SQLite.
2. Text is preprocessed before indexing.
3. An inverted index helps identify documents containing query terms.
4. TF-IDF represents the importance of terms in documents.
5. Cosine similarity measures query-document similarity.
6. Search results are ranked by relevance.

## Future Improvements

- Add pagination and advanced search filters.
- Improve search evaluation using precision and recall.
- Add support for more document formats.
- Improve the user interface and search experience.

## Author

**Samith Konkyana**

GitHub: [@Konkyana-Samith](https://github.com/Konkyana-Samith)
