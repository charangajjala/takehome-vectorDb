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
uvicorn app:main:app --reload 
```

Visit the API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Run with Docker Compose

```bash
docker-compose up --build
```

---

## 🔍 Detailed Explanation of Indexing Algorithms

### 📌 BruteForceIndexer

**Overview**  
BruteForceIndexer is a simple and exact K-Nearest Neighbors (KNN) implementation that computes cosine similarity between a query vector and all stored embeddings. It is best suited for small or medium-sized datasets where latency is less of a concern.

**How It Works**  
1. All chunks are stored in a flat list.
2. When a query is received:
   - Cosine similarity is computed between the query embedding and each stored embedding.
   - These similarities are stored as (chunk, similarity) pairs.
   - A max-heap (`heapq.nlargest`) is used to retrieve the top-k most similar chunks efficiently.

**Cosine Similarity Formula**  
\[
\text{cosine}(a, b) = \frac{\sum a_i b_i}{\sqrt{\sum a_i^2} \cdot \sqrt{\sum b_i^2}}
\]

**Time Complexity**  
- **Build**: `O(1)` — simple list assignment.
- **Query**: `O(N·D + N log k)`
  - `O(N·D)` for cosine similarity computation
  - `O(N log k)` for maintaining a heap of size `k`

**Space Complexity**  
- `O(N·D)` to store all embeddings
- `O(N)` for storing metadata like IDs

**Trade-offs**  
✅ Simple and exact  
✅ Supports dynamic inserts/deletes  
❌ Poor scalability due to linear scan of all embeddings during query


---

### 🌲 VPTreeIndexer

**Overview**  
VPTreeIndexer is an exact KNN algorithm based on a Vantage Point Tree (VP-Tree), which is optimized for fast nearest neighbor search using Euclidean distance. It is ideal for static datasets where insertions and deletions are rare.

**How It Works**  

**Build Phase**  
1. Randomly select a data point as the Vantage Point (VP).
2. Compute Euclidean distances from the VP to all other points.
3. Use the median of these distances as a threshold (radius).
4. Partition the dataset into:
   - Left subtree: points within the radius
   - Right subtree: points outside the radius
5. Recursively repeat the process to build the tree.

**Query Phase**  
1. Start at the root node and compute the distance from the query to the VP.
2. Recursively search the subtree (left or right) that the query falls into.
3. Use the triangle inequality to prune unnecessary branches.
4. Maintain a max-heap of the current top-k closest results.

**Euclidean Distance Formula**  
\[
\text{euclidean}(a, b) = \sqrt{\sum (a_i - b_i)^2}
\]

**Time Complexity**  
- **Build**: `O(N log N)` on average (due to recursive median partitioning)
- **Query**:
  - Average: `O(log N · D)` if pruning is effective
  - Worst case: `O(N · D)` if no pruning occurs

**Space Complexity**  
- `O(N·D)` for embeddings
- `O(N)` for storing the tree nodes (each node contains one VP and radius)

**Trade-offs**  
✅ Faster than brute-force for queries  
✅ Exact results using Euclidean distance  
❌ No easy support for dynamic updates  
❌ More complex to implement and maintain
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