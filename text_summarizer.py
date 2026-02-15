import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def summarize_text(text, summary_length=5):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    freq = {}
    for word in words:
        if word not in stop_words:
            if word not in freq:
                freq[word] = 1
            else:
                freq[word] += 1
    sentences = sent_tokenize(text)
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in freq:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = freq[word]
                else:
                    sentence_scores[sentence] += freq[word]
    summary = ''
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    for sentence, _ in sorted_sentences[:summary_length):
        summary += sentence + ' '
    return summary