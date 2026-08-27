from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer


def summarize_text(
    text: str,
    sentence_count: int = 5,
) -> str:

    if not text.strip():
        return ""

    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english"),
    )

    summarizer = LexRankSummarizer()

    sentences = summarizer(
        parser.document,
        sentence_count,
    )

    return " ".join(
        str(sentence)
        for sentence in sentences
    )