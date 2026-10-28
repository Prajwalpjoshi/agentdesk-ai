
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


KNOWLEDGE_DIR = Path(__file__).parent / "knowledge_base"


class KnowledgeBase:
    """Retrieve relevant passages from local Markdown documents."""

    def __init__(self, directory: Path = KNOWLEDGE_DIR):
        self.documents = []
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self.matrix = None
        self._load_documents(directory)

    def _load_documents(self, directory: Path):
        for path in sorted(directory.glob("*.md")):
            text = path.read_text(encoding="utf-8-sig")
            sections = [
                section.strip()
                for section in text.split("\n## ")
                if section.strip()
            ]

            for section in sections:
                self.documents.append({
                    "source": path.name,
                    "content": section,
                })

        if self.documents:
            self.matrix = self.vectorizer.fit_transform(
                [doc["content"] for doc in self.documents]
            )

    def search(self, query: str, top_k: int = 3):
        """Return relevant passages with source names and scores."""
        if not query.strip() or self.matrix is None:
            return []

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(
            query_vector, self.matrix
        ).flatten()

        ranked_indices = scores.argsort()[::-1]
        results = []

        for index in ranked_indices:
            score = float(scores[index])

            # Avoid presenting irrelevant passages as evidence.
            if score <= 0:
                continue

            document = self.documents[index]
            results.append({
                "source": document["source"],
                "content": document["content"],
                "score": round(score, 3),
            })

            if len(results) >= top_k:
                break

        return results


if __name__ == "__main__":
    kb = KnowledgeBase()

    while True:
        question = input("\nAsk a support question (or 'exit'): ")
        if question.strip().lower() == "exit":
            break

        matches = kb.search(question)

        if not matches:
            print("No relevant documentation found.")
            continue

        for result in matches:
            print(f"\nSource: {result['source']}")
            print(f"Relevance: {result['score']}")
            print(result["content"])
