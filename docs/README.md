# Qdrant - AI Rooms Workflow Addon

## Overview

Qdrant vector database addon for Rooms AI. This addon provides functionality to interact with Qdrant, a high-performance vector similarity search engine, enabling storage and retrieval of vector embeddings in AI workflows.

**Addon Type:** `storage` 

## Features

- **Collection Management**: Create and delete vector collections
- **Vector Storage**: Upsert points (vectors) with metadata to collections
- **Similarity Search**: Search for similar vectors using various distance metrics (Cosine, Euclidean, Dot Product)
- **Flexible Connectivity**: Support for local mode, remote server, gRPC, and Qdrant Cloud
- **Metadata Support**: Store and retrieve custom payloads with vectors

## Add to Rooms AI using poetry

Using the script

```bash
poetry add git+https://github.com/synvex-ai/qdrant-rooms-pkg.git
```

In the web interface, follow online guide for adding an addon. You can still use JSON in web interface.


## Configuration

### Addon Configuration
Add this addon to your AI Rooms workflow configuration:

```json
{
  "addons": [
    {
      "id": "qdrant-1",
      "type": "storage",
      "name": "Qdrant Vector Database",
      "enabled": true,
      "url": "http://localhost:6333",
      "prefer_grpc": false,
      "timeout": 60,
      "secrets": {
        "qdrant_api_key": "QDRANT_API_KEY"
      }
    }
  ]
}
```

### Configuration Fields

#### BaseAddonConfig Fields
All addons inherit these base configuration fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | - | Unique identifier for the addon instance |
| `type` | string | Yes | - | Type of the addon ("template") |
| `name` | string | Yes | - | Display name of the addon |
| `description` | string | Yes | - | Description of the addon |
| `enabled` | boolean | No | true | Whether the addon is enabled |

#### CustomAddonConfig Fields (Qdrant-specific)
This Qdrant addon adds these specific configuration fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | string | No | None | Qdrant server URL (e.g., http://localhost:6333) |
| `host` | string | No | None | Qdrant server host (alternative to url) |
| `port` | integer | No | 6333 | Qdrant server port |
| `grpc_port` | integer | No | 6334 | Qdrant gRPC port |
| `prefer_grpc` | boolean | No | false | Prefer gRPC for communication |
| `timeout` | integer | No | 60 | Request timeout in seconds |

### Required Secrets

| Secret Key | Environment Variable | Description |
|------------|---------------------|-------------|
| `qdrant_api_key` | `QDRANT_API_KEY` | Qdrant API key (optional for local mode, required for Qdrant Cloud) |

### Environment Variables
Create a `.env` file in your workflow directory:

```bash
# .env file
# Only required for Qdrant Cloud
QDRANT_API_KEY=your_qdrant_api_key_here
```

## Available Actions

### `create_collection`
Creates a new collection in Qdrant for storing vectors.

**Parameters:**
- `collection_name` (string, required): Name of the collection to create
- `vector_size` (integer, required): Dimensionality of vectors to store
- `distance` (string, optional): Distance metric - "Cosine", "Euclid", or "Dot" (default: "Cosine")

**Output Structure:**
- `collection_name` (string): Name of the created collection
- `success` (boolean): Whether the collection was created successfully
- `message` (string): Status message

**Workflow Usage:**
```json
{
  "id": "create-embeddings-collection",
  "action": "qdrant-1::create_collection",
  "parameters": {
    "collection_name": "documents",
    "vector_size": 384,
    "distance": "Cosine"
  }
}
```

### `upsert_points`
Insert or update points (vectors with metadata) in a collection.

**Parameters:**
- `collection_name` (string, required): Name of the collection
- `points` (list, required): List of points to upsert, each containing:
  - `id` (integer/string): Unique identifier for the point
  - `vector` (list of floats): Vector embeddings
  - `payload` (object, optional): Metadata to store with the vector

**Output Structure:**
- `collection_name` (string): Name of the collection
- `points_count` (integer): Number of points upserted
- `success` (boolean): Whether the upsert was successful
- `message` (string): Status message

**Workflow Usage:**
```json
{
  "id": "store-vectors",
  "action": "qdrant-1::upsert_points",
  "parameters": {
    "collection_name": "documents",
    "points": [
      {
        "id": 1,
        "vector": [0.1, 0.2, 0.3],
        "payload": {"text": "example document", "category": "test"}
      }
    ]
  }
}
```

### `search_points`
Search for similar vectors in a collection.

**Parameters:**
- `collection_name` (string, required): Name of the collection to search
- `query_vector` (list of floats, required): Query vector to find similar points
- `limit` (integer, optional): Maximum number of results (default: 5)
- `score_threshold` (float, optional): Minimum similarity score threshold

**Output Structure:**
- `collection_name` (string): Name of the collection searched
- `results` (list): List of search results, each containing:
  - `id`: Point identifier
  - `score`: Similarity score
  - `payload`: Metadata associated with the point
- `results_count` (integer): Number of results returned
- `success` (boolean): Whether the search was successful
- `message` (string): Status message

**Workflow Usage:**
```json
{
  "id": "search-similar-docs",
  "action": "qdrant-1::search_points",
  "parameters": {
    "collection_name": "documents",
    "query_vector": "{{embedding-step.output.vector}}",
    "limit": 10,
    "score_threshold": 0.7
  }
}
```

### `delete_collection`
Delete a collection from Qdrant.

**Parameters:**
- `collection_name` (string, required): Name of the collection to delete

**Output Structure:**
- `collection_name` (string): Name of the deleted collection
- `success` (boolean): Whether the collection was deleted successfully
- `message` (string): Status message

**Workflow Usage:**
```json
{
  "id": "cleanup-collection",
  "action": "qdrant-1::delete_collection",
  "parameters": {
    "collection_name": "old_documents"
  }
}
```

## Connection Examples

### Local Qdrant Server
```json
{
  "id": "qdrant-local",
  "type": "storage",
  "name": "Local Qdrant",
  "enabled": true,
  "url": "http://localhost:6333",
  "secrets": {}
}
```

### Qdrant Cloud
```json
{
  "id": "qdrant-cloud",
  "type": "storage",
  "name": "Qdrant Cloud",
  "enabled": true,
  "url": "https://xxxxx.cloud.qdrant.io:6333",
  "secrets": {
    "qdrant_api_key": "QDRANT_API_KEY"
  }
}
```

### Using gRPC
```json
{
  "id": "qdrant-grpc",
  "type": "storage",
  "name": "Qdrant with gRPC",
  "enabled": true,
  "host": "localhost",
  "port": 6333,
  "grpc_port": 6334,
  "prefer_grpc": true,
  "secrets": {}
}
``` 


## Testing & Lint

Like all Rooms AI deployments, addons should be roughly tested.

A basic PyTest is setup with a cicd to require 90% coverage in tests. Else it will not deploy the new release.

We also have ruff set up in cicd.

### Running the Tests

```bash
poetry run pytest tests/ --cov=src/template_rooms_pkg --cov-report=term-missing
```

Note: Update test coverage path once tests are implemented.

### Running the linter

```bash
poetry run ruff check . --fix
```

### Pull Requests & versioning

Like for all deployments, we use semantic versioning in cicd to automatize the versions.

For this, use the apprioriate commit message syntax for semantic release in github.


## Developers / Mainteners

- Adrien EPPLING :  [adrienesofts@gmail.com](mailto:adrienesofts@gmail.com)
