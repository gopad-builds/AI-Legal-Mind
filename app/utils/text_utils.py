def clean_text(text):
    """
    Removes leading and trailing spaces and converts the text to lowercase.
    """
    return text.strip().lower()

def count_words(text):
    words_length=len(text.split())
    return words_length
