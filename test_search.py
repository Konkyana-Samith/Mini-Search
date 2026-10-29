from app.search_engine import SearchEngine


engine = SearchEngine()

engine.add_document(
    1,
    "ML Basics",
    "Machine learning is useful",
)

engine.add_document(
    2,
    "Algorithms",
    "Machine learning algorithms are powerful",
)

engine.add_document(
    3,
    "Cooking",
    "Cooking requires fresh ingredients",
)

results = engine.search("machine xyzabc", 2)

for score, document_id in results:
    document = engine.documents[document_id]
    print(f"{document_id}: {document['title']} -> {score:.4f}")