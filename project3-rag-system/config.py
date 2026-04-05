# config.py

# Database
DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "ragdb"
DB_USER = "raguser"
DB_PASSWORD = "ragpassword"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Embedding model
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# LLM
GEMINI_MODEL = "gemini-3-flash-preview"
LLM_TEMPERATURE = 0.1

# Retrieval
TOP_K_CHUNKS = 3
