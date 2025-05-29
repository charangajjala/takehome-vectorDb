# VectorDB API - Take-Home Assignment

This project is a lightweight vector database API built with FastAPI. It supports creating libraries, uploading documents, extracting chunks, and performing similarity search using different indexing strategies.

---

## 🚀 Features

- **Document Management**: Create libraries, upload documents, extract chunks.
- **Indexing Algorithms**: Supports both Brute Force and VP-Tree indexers.
- **In-Memory Repository**: Thread-safe in-memory CRUD operations.
- **Search API**: K-Nearest Neighbor (KNN) search on vector embeddings.
- **Environment Configurable**: Easily switch between indexers and settings.
- **Docker Support**: Run locally with or without Docker.

---

## 📂 Folder Structure

```
app/
├── controllers/       # FastAPI route controllers
├── indexers/          # KNN indexer implementations
├── models/            # Pydantic schemas
├── repositories/      # Thread-safe in-memory repository
├── services/          # Business logic
├── config.py          # App settings from .env
main.py                # FastAPI app entry point
```

---

## ⚙️ Setup Instructions

### ✅ Option 1: Using Python `venv`

```bash
python -m venv venv
source venv/bin/activate     # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env         # or manually create .env file (see below)
```

### ✅ Option 2: Using `environment.yml` (Conda)

```bash
conda env create -f environment.yml
conda activate vectordb_api
```

---

## 🌍 .env File

Example `.env`:

```
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

REPO_TYPE=inmemory
INDEXER_TYPE=vptree  # options: bruteforce | vptree

# Optional for integration tests
COHERE_API_KEY=your-cohere-api-key
```

---

## ▶️ Run Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit the API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Run with Docker Compose

```bash
docker-compose up --build
```

---

## 🔍 Indexing Algorithms and Architecture Design

### 📌 BruteForceIndexer

**How it works**  
- Stores all chunk embeddings in a flat list.  
- On search: compute distance between query vector and each stored vector, then return top-k closest.

**Time Complexity**  
- **Build**: O(1) — no preprocessing, just append vectors.  
- **Query**: O(N·D + N log k)  
  - O(N·D): distance computation  
  - O(N log k): maintaining a size-k max-heap  

**Space Complexity**  
- O(N·D) for embeddings  
- O(N) for metadata (IDs, etc.)

**Trade-offs**  
✅ Exact results  
✅ Simple dynamic insert/delete  
❌ Poor scalability (query latency grows with N)

---

### 🌲 VPTreeIndexer

**How it works**

**Build**  
- Choose a random Vantage Point (VP)  
- Compute distances to all others, find median distance as radius  
- Recurse left (within radius) and right (outside radius)  

**Query**  
- At each node, compute distance to VP  
- Recurse into likely subtree using triangle inequality for pruning  

**Time Complexity**  
- **Build**: O(N log N) (on average)  
- **Query**: O(log N · D) average, O(N · D) worst-case  

**Space Complexity**  
- O(N·D) for embeddings  
- O(N) for VP tree nodes  

**Trade-offs**  
✅ Efficient query for static datasets  
❌ Poor dynamic support (insert/delete = rebuild)  
❌ High upfront build cost

---

## 💡 Design & Architecture

### 🧠 In-Memory Repository

**Pattern**  
- Implements `IReadOnlyRepository[T]` and `IWriteRepository[T]` interfaces  
- Thread-safe via `threading.RLock`  

**Thread-Safety**  
- Uses `@synchronized` or `with self._lock:` for atomic operations  
- Allows nested lock calls (re-entrant)

**Pros & Cons**  
✅ Simple and fast for prototyping  
✅ No dependencies  
❌ No data persistence  
❌ Unsuitable for large/distributed datasets

---

### 🔧 Dependency Injection & @lru_cache()

**FastAPI Wiring**  
- `Depends()` wires controllers → services → repositories/indexers  
- `@lru_cache()` makes singleton instances

**Why**  
- One shared instance per server process  
- Efficient without third-party DI libraries

**Trade-offs**  
✅ Minimal setup  
✅ App-wide singleton support  
❌ No scoped lifetimes (e.g., per-request)  
❌ Requires manual cleanup for external resources

**Alternatives**  
- Use `app.state`  
- Use `python-dependency-injector`  
- Initialize singletons in `startup` event

---

## 📈 Indexing Design

### 🔄 Rebuild-on-Search Strategy

```python
chunks = [c for d in lib.documents for c in d.chunks]
self._idx.build(chunks)
results = self._idx.query(query_embedding, k)
```

**Benefits**  
✅ Always reflects latest data  
✅ No need for tracking dirty/invalidation state  
✅ Consistent queries

**Trade-offs**  
❌ Full rebuild cost on every query  
  - Brute-force: O(N)  
  - VP-Tree: O(N log N)

---

### 🚀 Alternative Indexing Designs

#### 1. **Per-Library Cached Index**
- Maintain `Dict[library_id, IKnnIndexer]`
- Rebuild index only on first query after an update
- Lazy evaluation, better performance

#### 2. **Incremental Updates (BruteForce Only)**
- Append/remove vectors directly
- Avoid full rebuild

#### 3. **Advanced Index Structures**
- Use FAISS or HNSW  
- Support native dynamic updates (insert/delete)
- Better performance on large datasets

## 🧪 Testing

- Unit & integration tests in `tests/` folder
- Uses `Cohere API` for realistic embeddings
- Run: `pytest`

---

## 📬 API Overview

Visit [http://localhost:8000/docs](http://localhost:8000/docs)

- `POST /libraries/` — Create a library
- `POST /libraries/{lib_id}/documents/` — Upload a document
- `POST /libraries/{lib_id}/search/` — Search in a library
- `GET /libraries/{lib_id}` — Get library details

---

## 📝 Summary

- ✅ In-memory thread-safe repository with locking
- ✅ Modular services, controllers, indexers
- ✅ Flexible indexing (Brute Force, VP-Tree)
- ✅ Dockerized
- ✅ Embedded testing suite

---

For any issues or questions, feel free to reach out.