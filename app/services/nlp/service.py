import re

from app.services.nlp.chunker import chunk_text
from app.services.nlp.cleaner import clean_text
from app.services.nlp.extractor import extract_text
from app.services.nlp.summarizer import summarize_text


class NLPService:

    @staticmethod
    def process_document(
        file_path: str,
    ) -> dict:

        # 1. Extract
        raw_text = extract_text(file_path)

        # 2. Clean
        text = clean_text(raw_text)

        if not text:
            raise ValueError(
                "Document contains no extractable text"
            )

        # 3. Chunk
        chunks = chunk_text(text)

        # 4. Summary
        summary = summarize_text(text)

        # 5. Statistics
        word_count = len(text.split())

        sentence_count = len(
            re.findall(
                r"[.!?]+",
                text,
            )
        )

        character_count = len(text)

        return {
            "summary": summary,
            "chunk_count": len(chunks),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "character_count": character_count,
        }