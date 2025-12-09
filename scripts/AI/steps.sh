# 1. First, reset/clear any existing ChromaDB
python3 01_reset_chroma.py

# 2. Create new collection from your JSON file
python3 02_create_collection.py

# 3. Verify the collection was created correctly
python3 03_verify_collection.py

# 4. Test with predefined queries
python3 04_test_queries.py

# 5. (Optional) Use interactive mode for custom queries
python3 05_interactive_query.py