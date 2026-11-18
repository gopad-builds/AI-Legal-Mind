sample_document={"document_id":101, 
                 "case_title":"State of Maharashtra vs ABC",
                 "court":"Supreme Court of India",
                 "year":2024,
                 "judges":["Justice A", "Justice B"],
                 "paragraphs": ["The petitioner challenged the decision of the state government.",
                                "The court examined Article 14 and Article 21 of the Constitution.",
                                "The court observed that Article 21 protects the right to life and personal liberty."],
                 "sections":["Article 14", "Article 21", "Article 19", "Article 21"],
                 "case_date": (2024, 5, 12) }

def inspect_document(document):
    case_title=document["case_title"]
    court_name=document["court"]
    no_of_paragraphs=len(document["paragraphs"])
    no_of_judges=len(document["judges"])
    year_of_judgement=document["case_date"][0]
    return {
        "case_title": case_title,
        "court": court_name,
        "paragraphs": no_of_paragraphs,
        "judges": no_of_judges,
        "year": year_of_judgement
    }

def get_unique_sections(document):
    return  set(document["sections"])

def get_total_word_count(document):
    total_words=0
    for i in range(len(document["paragraphs"])):
        total_words+=len(document["paragraphs"][i].split())
    return total_words


def get_case_date(document):
    return document["case_date"]
