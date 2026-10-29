import re

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


class TextProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.stemmer = PorterStemmer()

    def process(self, text: str) -> list[str]:
        text = text.lower()

        tokens = re.findall(r"[a-z]+", text)

        tokens = [
            token
            for token in tokens
            if token not in self.stop_words
        ]

        tokens = [
            self.stemmer.stem(token)
            for token in tokens
        ]

        return tokens