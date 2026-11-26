import re

KNOWN_HEADINGS = {
    "JUDGMENT", "ORDER", "FACTS", "FACTS OF THE CASE", "ISSUES",
    "ISSUES FOR CONSIDERATION", "ANALYSIS", "CONCLUSION", "BACKGROUND",
    "FACTUAL BACKGROUND", "FINDINGS", "FINDINGS RECORDED BY THE COURTS BELOW",
    "INTRODUCTION", "ARGUMENTS", "SUBMISSIONS", "DECISION", "REASONING",
    "RELIEF", "OPERATIVE PART", "DIRECTIONS", "OBSERVATIONS"
}

COURT_PATTERNS = [
    r"IN THE SUPREME COURT OF INDIA",
    r"IN THE HIGH COURT OF \w+",
    r"IN THE DISTRICT COURT OF \w+",
    r"HIGH COURT OF \w+",
    r"SUPREME COURT OF INDIA",
]

CASE_NUMBER_PATTERNS = [
    r"CRIMINAL APPEAL NO\..*",
    r"CIVIL APPEAL NO\..*",
    r"W\.P\.\s*\(.*?\)\s*NO\..*",
    r"SLP\s*\(.*?\)\s*NO\..*",
    r"WRIT PETITION.*NO\..*",
    r"TRANSFER PETITION.*NO\..*",
    r"SPECIAL LEAVE PETITION.*",
]


def normalize_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r" {2,}", " ", line)
    return line


def is_likely_heading(line: str) -> bool:
    line = normalize_line(line)
    if not line:
        return False

    # Exact known heading match first
    if line.upper() in KNOWN_HEADINGS:
        return True

    # Must not be a court name or case number
    for pattern in COURT_PATTERNS + CASE_NUMBER_PATTERNS:
        if re.match(pattern, line, re.IGNORECASE):
            return False

    # Heuristic: all uppercase, no trailing period, reasonable length
    if (
        line == line.upper()
        and not line.endswith(".")
        and len(line) <= 60
        and len(line.split()) >= 1
        and not re.search(r"\d", line)  # headings rarely contain digits
        and not line.startswith("(")    # excludes (i), (ii) sub-items
    ):
        return True

    return False


def is_numbered_paragraph(line: str) -> tuple[bool, int | None]:
    line = normalize_line(line)
    # Matches: "1.", "2.", "10." at start
    m = re.match(r"^(\d+)\.\s+\S", line)
    if m:
        return True, int(m.group(1))
    # Matches: "(1)", "(2)" at start
    m = re.match(r"^\((\d+)\)\s+\S", line)
    if m:
        return True, int(m.group(1))
    # Matches: "1)" at start
    m = re.match(r"^(\d+)\)\s+\S", line)
    if m:
        return True, int(m.group(1))
    return False, None


def extract_legal_references(text: str) -> list[str]:
    patterns = [
        r"Section\s+\d+[A-Z]?\s+(?:of\s+the\s+)?(?:IPC|CrPC|CPC|IEA|ITPA|[A-Z]{2,})",
        r"Section\s+\d+[A-Z]?\s+of\s+the\s+[A-Z][a-zA-Z\s]+Act(?:,\s*\d{4})?",
        r"Article\s+\d+[A-Z]?(?:\s+of\s+the\s+Constitution)?",
        r"u/s\.\s+[\d,\s&A-Z]+",
        r"s\.\s*\d+(?:[,\s&\d]+)?(?:of\s+the\s+[A-Z][a-zA-Z\s]+)?",
        r"Order\s+[IVXLC]+\s+Rule\s+\d+",
    ]
    references = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        references.extend([m.strip() for m in matches])
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for r in references:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique


def extract_court_details(pages: list[dict]) -> dict:
    first_page_text = pages[0].get("text", "") if pages else ""
    court = ""
    case_number = ""
    judge = ""

    for line in first_page_text.split("\n"):
        line = normalize_line(line)
        if not court:
            for pattern in COURT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    court = line
                    break
        if not case_number:
            for pattern in CASE_NUMBER_PATTERNS:
                if re.match(pattern, line, re.IGNORECASE):
                    case_number = line
                    break
        if not judge:
            if re.search(r",\s*J\.$", line) or re.search(r",\s*C\.J\.$", line):
                judge = line

    return {"court": court, "case_number": case_number, "judge": judge}
