import re
import unicodedata

# Load dictionary globally
with open('arabic_words.txt', 'r', encoding='utf-8') as f:
    ARABIC_DICTIONARY = set(w.strip() for w in f if len(w.strip()) > 1)

def strip_diacritics(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

def tokenize_arabic(text):
    return re.findall(r'[\u0600-\u06FF]+', text)

def spell_check(tokens):
    misspelled = [word for word in tokens if word not in ARABIC_DICTIONARY]
    return misspelled

def grade_arabic_text_offline(text):
    stripped_text = strip_diacritics(text)
    tokens = tokenize_arabic(stripped_text)

    word_count = len(tokens)
    unique_words = len(set(tokens))
    avg_word_len = sum(len(w) for w in tokens) / word_count if word_count else 0

    # Spell checking
    misspelled = spell_check(tokens)
    spelling_penalty = len(misspelled) * 0.3
    spelling_score = max(3 - int(spelling_penalty), 1)

    # Grammar scoring
    grammar_score = 2
    if '؟' in text or '،' in text:
        grammar_score += 1
    if re.match(r'^[\u0600-\u06FF\s،؟]+$', text.strip()):
        grammar_score += 1

    # Vocabulary scoring
    vocab_score = 1
    if unique_words > 10:
        vocab_score += 1
    if avg_word_len > 4:
        vocab_score += 1

    # Clarity scoring
    clarity_score = 2 if word_count > 8 else 1
    if any(w in text for w in ['أيضًا', 'لذلك', 'ولكن', 'ثم', 'بينما']):
        clarity_score += 1

    total_score = grammar_score + vocab_score + clarity_score + spelling_score

    return {
        "grammar_score": grammar_score,
        "vocabulary_score": vocab_score,
        "clarity_score": clarity_score,
        "spelling_score": spelling_score,
        "total_score": total_score,
        "misspelled_words": misspelled,
        "feedback": f"{word_count} words, {len(misspelled)} possibly misspelled. Avg. word length: {avg_word_len:.2f}"
    }
