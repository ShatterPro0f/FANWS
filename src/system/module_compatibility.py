#!/usr/bin/env python3
"""
Module Compatibility Layer
Handles optional dependencies and provides fallbacks for missing modules.
"""

import logging

# Markdown support
try:
    import markdown2
    MARKDOWN_AVAILABLE = True
    logging.info("✓ Markdown2 module available")
except ImportError:
    try:
        import markdown
        # Create a compatibility wrapper for markdown
        class Markdown2Wrapper:
            def __init__(self):
                self.markdown = markdown

            def markdown(self, text, **kwargs):
                return self.markdown.markdown(text)

        markdown2 = Markdown2Wrapper()
        MARKDOWN_AVAILABLE = True
        logging.info("✓ Markdown module available (using as markdown2)")
    except ImportError:
        MARKDOWN_AVAILABLE = False
        # Create a minimal fallback that just returns the text
        class MarkdownFallback:
            def markdown(self, text, **kwargs):
                return text.replace('\n', '<br>')

        markdown2 = MarkdownFallback()
        logging.warning("⚠ No markdown module available - using basic fallback")

# PDF generation support
try:
    import pdfkit
    PDF_GENERATION_AVAILABLE = True
    logging.info("✓ PDFKit module available")
except ImportError:
    PDF_GENERATION_AVAILABLE = False
    # Create fallback class for pdfkit
    class PDFKitFallback:
        def from_string(self, *args, **kwargs):
            raise NotImplementedError("PDF generation not available - install pdfkit")

        def from_file(self, *args, **kwargs):
            raise NotImplementedError("PDF generation not available - install pdfkit")

    pdfkit = PDFKitFallback()
    logging.warning("⚠ PDFKit not available - PDF generation disabled")

# Plotting support
try:
    import matplotlib
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
    logging.info("✓ Matplotlib module available")
except ImportError:
    PLOTTING_AVAILABLE = False
    # Create fallback class for matplotlib
    class MatplotlibFallback:
        class pyplot:
            @staticmethod
            def figure(*args, **kwargs):
                raise NotImplementedError("Plotting not available - install matplotlib")

            @staticmethod
            def plot(*args, **kwargs):
                raise NotImplementedError("Plotting not available - install matplotlib")

            @staticmethod
            def show():
                raise NotImplementedError("Plotting not available - install matplotlib")

    matplotlib = MatplotlibFallback()
    logging.warning("⚠ Matplotlib not available - plotting disabled")

# Natural Language Toolkit support - Lazy loading
NLTK_AVAILABLE = False
_nltk = None

def get_nltk():
    """Lazy load NLTK when first needed"""
    global _nltk, NLTK_AVAILABLE

    if _nltk is not None:
        return _nltk

    try:
        import nltk
        _nltk = nltk
        NLTK_AVAILABLE = True
        logging.info("✓ NLTK module loaded on demand")
        return _nltk
    except ImportError:
        # Create fallback class for NLTK
        class NLTKFallback:
            class tokenize:
                @staticmethod
                def word_tokenize(text):
                    # Basic word tokenization fallback
                    return text.split()

                @staticmethod
                def sent_tokenize(text):
                    # Basic sentence tokenization fallback
                    import re
                    sentences = re.split(r'[.!?]+', text)
                    return [s.strip() for s in sentences if s.strip()]

            class corpus:
                class stopwords:
                    @staticmethod
                    def words(lang='english'):
                        # Basic stopwords fallback
                        return ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should']

        _nltk = NLTKFallback()
        NLTK_AVAILABLE = False
        logging.warning("⚠ NLTK not available - using basic text processing fallbacks")
        return _nltk

# Provide backwards compatibility
nltk = property(lambda self: get_nltk())

# Additional optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
    logging.info("✓ Requests module available")
except ImportError:
    REQUESTS_AVAILABLE = False
    # Create fallback for requests
    class RequestsFallback:
        @staticmethod
        def get(*args, **kwargs):
            raise NotImplementedError("HTTP requests not available - install requests")

        @staticmethod
        def post(*args, **kwargs):
            raise NotImplementedError("HTTP requests not available - install requests")

    requests = RequestsFallback()
    logging.warning("⚠ Requests not available - HTTP functionality disabled")

# Scikit-learn support - Lazy loading
SKLEARN_AVAILABLE = False
_sklearn = None

def get_sklearn():
    """Lazy load scikit-learn when first needed"""
    global _sklearn, SKLEARN_AVAILABLE

    if _sklearn is not None:
        return _sklearn

    try:
        import sklearn
        _sklearn = sklearn
        SKLEARN_AVAILABLE = True
        logging.info("✓ Scikit-learn module loaded on demand")
        return _sklearn
    except ImportError:
        # Create fallback class for sklearn
        class SklearnFallback:
            class feature_extraction:
                class text:
                    class TfidfVectorizer:
                        def __init__(self, *args, **kwargs):
                            pass
                        def fit_transform(self, documents):
                            return [[1.0] * len(documents)]
                        def get_feature_names_out(self):
                            return ['feature_0']

            class metrics:
                @staticmethod
                def cosine_similarity(X, Y=None):
                    return [[1.0]]

            class cluster:
                class KMeans:
                    def __init__(self, *args, **kwargs):
                        pass
                    def fit(self, X):
                        return self
                    def predict(self, X):
                        return [0] * len(X)

        _sklearn = SklearnFallback()
        SKLEARN_AVAILABLE = False
        logging.warning("⚠ Scikit-learn not available - using basic ML fallbacks")
        return _sklearn

# Provide backwards compatibility
sklearn = property(lambda self: get_sklearn())

# Dotenv compatibility (for environment variable management)
try:
    from dotenv import load_dotenv, set_key
    DOTENV_AVAILABLE = True
    safe_load_dotenv = load_dotenv
    safe_set_key = set_key
except ImportError:
    DOTENV_AVAILABLE = False

    def safe_load_dotenv(dotenv_path=None, stream=None, verbose=False, override=False, interpolate=True, encoding="utf-8"):
        """Fallback for dotenv load_dotenv when python-dotenv is not available"""
        return False

    def safe_set_key(dotenv_path, key_to_set, value_to_set, quote_mode="always", export=False, encoding="utf-8"):
        """Fallback for dotenv set_key when python-dotenv is not available"""
        return False, key_to_set, value_to_set

    logging.warning("⚠ Python-dotenv not available - environment variable management disabled")

# Export compatibility flags and modules
__all__ = [
    'MARKDOWN_AVAILABLE', 'markdown2',
    'PDF_GENERATION_AVAILABLE', 'pdfkit',
    'PLOTTING_AVAILABLE', 'matplotlib',
    'NLTK_AVAILABLE', 'nltk',
    'REQUESTS_AVAILABLE', 'requests',
    'DOTENV_AVAILABLE', 'safe_load_dotenv', 'safe_set_key'
]
