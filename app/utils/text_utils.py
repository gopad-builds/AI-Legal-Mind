import re

def clean_text(text):
    """
    Removes leading and trailing spaces and converts the text to lowercase.
    """
    return text.strip().lower()

def count_words(text):
    words_length=len(text.split())
    return words_length

def normalize_whitespace(text: str) -> str:
    # Tabs to space
    text = text.replace("\t", " ")
    # Trailing spaces per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    # Multiple spaces to single
    text = re.sub(r" {2,}", " ", text)
    # 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_page_markers(text: str) -> str:
    # Matches: "Page 1 of 15", "Page 10 of 15"
    return re.sub(r"Page\s+\d+\s+of\s+\d+\s*\n?", "", text).strip()


def remove_digital_signature(text: str) -> str:
    # Matches the Digitally signed block common in Indian court PDFs
    pattern = r"Digitally signed by\s*\n.*?\nDate:.*?\nReason:\s*\nSignature Not Verified\s*\n?"
    return re.sub(pattern, "", text, flags=re.DOTALL).strip()


def fix_hyphenation(text: str) -> str:
    # Only fix line-break hyphens: word- \n word → wordword
    # Preserves well-established, PW-8, non-compliance (no newline after hyphen)
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def fix_spaced_text(text: str) -> str:
    # Fix PyMuPDF spacing artifact: "J U D G M E N T" → "JUDGMENT"
    return re.sub(r"\b([A-Z])(?: ([A-Z])){2,}\b", lambda m: m.group(0).replace(" ", ""), text)


def detect_repeated_headers(pages: list[str], min_occurrences: int = 3) -> list[str]:
    # Split each page into lines, count how many pages each line appears on
    line_page_count: dict[str, int] = {}
    for page_text in pages:
        seen_on_this_page = set()
        for line in page_text.split("\n"):
            stripped = line.strip()
            if len(stripped) > 5 and stripped not in seen_on_this_page:
                line_page_count[stripped] = line_page_count.get(stripped, 0) + 1
                seen_on_this_page.add(stripped)

    return [line for line, count in line_page_count.items() if count >= min_occurrences]


def remove_repeated_headers(text: str, headers: list[str]) -> str:
    for header in headers:
        text = text.replace(header, "")
    return text


def clean_page_text(text: str, headers: list[str]) -> str:
    text = fix_hyphenation(text)
    text = remove_digital_signature(text)
    text = remove_page_markers(text)
    text = remove_repeated_headers(text, headers)
    text = fix_spaced_text(text)
    text = normalize_whitespace(text)
    return text


def clean_document(pages: list[dict]) -> list[dict]:
    page_texts = [p["text"] for p in pages]
    repeated_headers = detect_repeated_headers(page_texts)

    cleaned = []
    for page in pages:
        cleaned.append({
            **page,
            "text": clean_page_text(page["text"], repeated_headers),
            "cleaned": True
        })
    return cleaned
