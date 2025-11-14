"""
Text processing module for FANWS application.
Handles text analysis, synonym management, and content processing.
"""

import re
import os
import json
import logging
import threading
from typing import Dict, List, Optional, Set, Any, Tuple
from collections import Counter, defaultdict
from ..core.error_handling_system import ErrorHandler
from ..database.database_manager import DatabaseManager
from ..core.error_handling_system import ErrorHandler, FileOperationError

class TextAnalyzer:
    """Comprehensive text analysis for writing assistance."""

    def __init__(self):
        """Initialize text analyzer."""
        self.word_frequency = Counter()
        self.phrase_frequency = Counter()
        self.readability_cache = {}  # Simple dict cache
        self._lock = threading.RLock()

        # Initialize basic patterns
        self.sentence_pattern = re.compile(r'[.!?]+')
        self.word_pattern = re.compile(r'\b[a-zA-Z]+\b')
        self.paragraph_pattern = re.compile(r'\n\s*\n')

        logging.info("TextAnalyzer initialized")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive text analysis."""
        if not text or not text.strip():
            return self._empty_analysis()

        with self._lock:
            # Check cache first
            cache_key = f"analysis_{hash(text)}"
            cached_result = self.readability_cache.get(cache_key)
            if cached_result:
                return cached_result

            # Perform analysis
            analysis = {
                'word_count': self._count_words(text),
                'character_count': len(text),
                'character_count_no_spaces': len(text.replace(' ', '')),
                'sentence_count': self._count_sentences(text),
                'paragraph_count': self._count_paragraphs(text),
                'average_words_per_sentence': 0,
                'average_sentences_per_paragraph': 0,
                'readability_score': self._calculate_readability(text),
                'word_frequency': self._get_word_frequency(text),
                'repeated_words': self._find_repeated_words(text),
                'long_sentences': self._find_long_sentences(text),
                'complexity_indicators': self._analyze_complexity(text)
            }

            # Calculate averages
            if analysis['sentence_count'] > 0:
                analysis['average_words_per_sentence'] = analysis['word_count'] / analysis['sentence_count']

            if analysis['paragraph_count'] > 0:
                analysis['average_sentences_per_paragraph'] = analysis['sentence_count'] / analysis['paragraph_count']

            # Cache result
            self.readability_cache[cache_key] = analysis

            return analysis

    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            'word_count': 0,
            'character_count': 0,
            'character_count_no_spaces': 0,
            'sentence_count': 0,
            'paragraph_count': 0,
            'average_words_per_sentence': 0,
            'average_sentences_per_paragraph': 0,
            'readability_score': 0,
            'word_frequency': {},
            'repeated_words': [],
            'long_sentences': [],
            'complexity_indicators': {}
        }

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = self.word_pattern.findall(text.lower())
        return len(words)

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = self.sentence_pattern.split(text)
        return len([s for s in sentences if s.strip()])

    def _count_paragraphs(self, text: str) -> int:
        """Count paragraphs in text."""
        paragraphs = self.paragraph_pattern.split(text)
        return len([p for p in paragraphs if p.strip()])

    def _calculate_readability(self, text: str) -> float:
        """Calculate basic readability score (simplified Flesch score)."""
        try:
            words = self._count_words(text)
            sentences = self._count_sentences(text)

            if words == 0 or sentences == 0:
                return 0.0

            # Count syllables (simplified)
            syllables = self._count_syllables(text)

            if syllables == 0:
                return 0.0

            # Simplified Flesch Reading Ease score
            score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
            return max(0, min(100, score))

        except Exception as e:
            logging.error(f"Error calculating readability: {str(e)}")
            return 0.0

    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (simplified approach)."""
        vowels = 'aeiouy'
        syllable_count = 0
        words = self.word_pattern.findall(text.lower())

        for word in words:
            word_syllables = 0
            prev_was_vowel = False

            for char in word:
                if char in vowels:
                    if not prev_was_vowel:
                        word_syllables += 1
                    prev_was_vowel = True
                else:
                    prev_was_vowel = False

            # Handle silent 'e'
            if word.endswith('e') and word_syllables > 1:
                word_syllables -= 1

            # Every word has at least one syllable
            if word_syllables == 0:
                word_syllables = 1

            syllable_count += word_syllables

        return syllable_count

    def _get_word_frequency(self, text: str) -> Dict[str, int]:
        """Get word frequency analysis."""
        words = self.word_pattern.findall(text.lower())
        frequency = Counter(words)

        # Return top 20 most frequent words
        return dict(frequency.most_common(20))

    def _find_repeated_words(self, text: str, threshold: int = 3) -> List[str]:
        """Find words that appear frequently (potential overuse)."""
        words = self.word_pattern.findall(text.lower())
        frequency = Counter(words)

        # Filter out common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'do', 'does', 'did', 'get', 'got', 'go', 'went', 'come', 'came', 'see', 'saw', 'know', 'knew', 'think', 'thought', 'say', 'said', 'tell', 'told', 'ask', 'asked', 'give', 'gave', 'take', 'took', 'make', 'made', 'want', 'wanted', 'use', 'used', 'work', 'worked', 'call', 'called', 'try', 'tried', 'need', 'needed', 'feel', 'felt', 'become', 'became', 'leave', 'left', 'put', 'seem', 'seemed', 'keep', 'kept', 'let', 'begin', 'began', 'help', 'helped', 'show', 'showed', 'hear', 'heard', 'play', 'played', 'run', 'ran', 'move', 'moved', 'live', 'lived', 'bring', 'brought', 'happen', 'happened', 'write', 'wrote', 'sit', 'sat', 'stand', 'stood', 'lose', 'lost', 'pay', 'paid', 'meet', 'met', 'include', 'included', 'continue', 'continued', 'set', 'learn', 'learned', 'change', 'changed', 'lead', 'led', 'understand', 'understood', 'watch', 'watched', 'follow', 'followed', 'stop', 'stopped', 'create', 'created', 'speak', 'spoke', 'read', 'spend', 'spent', 'grow', 'grew', 'open', 'opened', 'walk', 'walked', 'win', 'won', 'teach', 'taught', 'offer', 'offered', 'remember', 'remembered', 'consider', 'considered', 'appear', 'appeared', 'buy', 'bought', 'serve', 'served', 'die', 'died', 'send', 'sent', 'expect', 'expected', 'build', 'built', 'stay', 'stayed', 'fall', 'fell', 'cut', 'reach', 'reached', 'kill', 'killed', 'remain', 'remained'}

        repeated_words = []
        for word, count in frequency.items():
            if count >= threshold and word not in common_words and len(word) > 3:
                repeated_words.append(f"{word} ({count})")

        return repeated_words

    def _find_long_sentences(self, text: str, threshold: int = 25) -> List[str]:
        """Find sentences that might be too long."""
        sentences = self.sentence_pattern.split(text)
        long_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                word_count = len(self.word_pattern.findall(sentence))
                if word_count > threshold:
                    long_sentences.append(f"{sentence[:100]}... ({word_count} words)")

        return long_sentences

    def _analyze_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity indicators."""
        words = self.word_pattern.findall(text.lower())

        # Count complex words (3+ syllables)
        complex_words = 0
        for word in words:
            if self._count_syllables(word) >= 3:
                complex_words += 1

        complex_word_ratio = complex_words / len(words) if words else 0

        # Analyze sentence structure
        sentences = self.sentence_pattern.split(text)
        sentence_lengths = [len(self.word_pattern.findall(s)) for s in sentences if s.strip()]

        return {
            'complex_words': complex_words,
            'complex_word_ratio': complex_word_ratio,
            'average_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            'longest_sentence': max(sentence_lengths) if sentence_lengths else 0,
            'shortest_sentence': min(sentence_lengths) if sentence_lengths else 0
        }

class SynonymCache:
    """Cache for synonym suggestions and word alternatives."""

    def __init__(self):
        """Initialize synonym cache."""
        self.synonyms = {}
        self.antonyms = {}
        self.word_associations = defaultdict(set)
        self._lock = threading.RLock()

        # Load built-in synonyms
        self._load_builtin_synonyms()

        logging.info("SynonymCache initialized")

    def _load_builtin_synonyms(self):
        """Load built-in synonym database."""
        # This is a simplified synonym database
        # In a real implementation, you'd load from a comprehensive database
        builtin_synonyms = {
            'happy': ['joyful', 'cheerful', 'pleased', 'delighted', 'content', 'elated'],
            'sad': ['unhappy', 'sorrowful', 'melancholy', 'dejected', 'mournful', 'glum'],
            'big': ['large', 'huge', 'enormous', 'gigantic', 'massive', 'immense'],
            'small': ['little', 'tiny', 'minute', 'petite', 'compact', 'miniature'],
            'good': ['excellent', 'wonderful', 'great', 'superb', 'outstanding', 'fantastic'],
            'bad': ['terrible', 'awful', 'horrible', 'dreadful', 'poor', 'inferior'],
            'beautiful': ['gorgeous', 'stunning', 'lovely', 'attractive', 'pretty', 'elegant'],
            'ugly': ['hideous', 'repulsive', 'unsightly', 'unattractive', 'grotesque'],
            'fast': ['quick', 'rapid', 'swift', 'speedy', 'hasty', 'brisk'],
            'slow': ['sluggish', 'gradual', 'leisurely', 'unhurried', 'deliberate'],
            'strong': ['powerful', 'robust', 'sturdy', 'mighty', 'forceful', 'potent'],
            'weak': ['feeble', 'frail', 'fragile', 'delicate', 'vulnerable', 'powerless'],
            'smart': ['intelligent', 'clever', 'bright', 'brilliant', 'wise', 'sharp'],
            'stupid': ['foolish', 'silly', 'dumb', 'ignorant', 'senseless', 'mindless'],
            'important': ['significant', 'crucial', 'vital', 'essential', 'critical', 'key'],
            'unimportant': ['trivial', 'insignificant', 'minor', 'petty', 'negligible'],
            'new': ['fresh', 'recent', 'modern', 'latest', 'contemporary', 'current'],
            'old': ['ancient', 'aged', 'elderly', 'vintage', 'antique', 'archaic'],
            'easy': ['simple', 'effortless', 'straightforward', 'uncomplicated', 'basic'],
            'difficult': ['hard', 'challenging', 'tough', 'complex', 'complicated', 'arduous'],
            'love': ['adore', 'cherish', 'treasure', 'worship', 'idolize', 'devotion'],
            'hate': ['loathe', 'despise', 'detest', 'abhor', 'dislike', 'resent'],
            'walk': ['stroll', 'stride', 'march', 'wander', 'roam', 'trek'],
            'run': ['sprint', 'dash', 'race', 'rush', 'hurry', 'bolt'],
            'talk': ['speak', 'converse', 'chat', 'discuss', 'communicate', 'dialogue'],
            'look': ['see', 'observe', 'watch', 'view', 'gaze', 'stare', 'glance'],
            'think': ['ponder', 'consider', 'contemplate', 'reflect', 'meditate', 'reason'],
            'feel': ['sense', 'experience', 'perceive', 'touch', 'handle', 'undergo'],
            'make': ['create', 'produce', 'manufacture', 'construct', 'build', 'craft'],
            'take': ['grab', 'seize', 'capture', 'acquire', 'obtain', 'secure'],
            'give': ['provide', 'offer', 'present', 'donate', 'contribute', 'supply'],
            'get': ['obtain', 'acquire', 'receive', 'gain', 'procure', 'fetch'],
            'find': ['discover', 'locate', 'uncover', 'detect', 'identify', 'spot'],
            'use': ['utilize', 'employ', 'apply', 'operate', 'handle', 'manipulate'],
            'say': ['state', 'declare', 'announce', 'proclaim', 'express', 'utter'],
            'know': ['understand', 'comprehend', 'realize', 'recognize', 'acknowledge'],
            'work': ['labor', 'toil', 'operate', 'function', 'perform', 'execute'],
            'help': ['assist', 'aid', 'support', 'facilitate', 'contribute', 'cooperate'],
            'show': ['display', 'exhibit', 'demonstrate', 'reveal', 'present', 'expose'],
            'try': ['attempt', 'endeavor', 'strive', 'struggle', 'effort', 'venture'],
            'ask': ['inquire', 'question', 'request', 'demand', 'query', 'interrogate'],
            'need': ['require', 'want', 'desire', 'lack', 'crave', 'demand'],
            'want': ['desire', 'wish', 'crave', 'long', 'yearn', 'hunger'],
            'turn': ['rotate', 'spin', 'twist', 'revolve', 'pivot', 'swivel'],
            'put': ['place', 'position', 'set', 'locate', 'situate', 'install'],
            'end': ['finish', 'conclude', 'terminate', 'complete', 'cease', 'stop'],
            'begin': ['start', 'commence', 'initiate', 'launch', 'open', 'embark'],
            'seem': ['appear', 'look', 'sound', 'feel', 'give impression'],
            'become': ['turn into', 'grow into', 'develop into', 'transform', 'evolve'],
            'leave': ['depart', 'exit', 'abandon', 'desert', 'quit', 'withdraw'],
            'call': ['telephone', 'phone', 'ring', 'contact', 'summon', 'invite'],
            'move': ['shift', 'transfer', 'relocate', 'transport', 'migrate', 'travel'],
            'live': ['exist', 'survive', 'reside', 'dwell', 'inhabit', 'occupy'],
            'believe': ['trust', 'have faith', 'accept', 'suppose', 'assume', 'presume'],
            'hold': ['grasp', 'grip', 'clutch', 'carry', 'bear', 'support'],
            'bring': ['carry', 'transport', 'deliver', 'fetch', 'convey', 'bear'],
            'happen': ['occur', 'take place', 'come about', 'transpire', 'arise'],
            'write': ['compose', 'author', 'pen', 'draft', 'script', 'inscribe'],
            'provide': ['supply', 'furnish', 'give', 'offer', 'contribute', 'deliver'],
            'sit': ['be seated', 'rest', 'perch', 'settle', 'occupy'],
            'stand': ['rise', 'get up', 'be upright', 'remain', 'endure'],
            'lose': ['misplace', 'forfeit', 'sacrifice', 'surrender', 'give up'],
            'pay': ['compensate', 'remunerate', 'settle', 'reward', 'reimburse'],
            'meet': ['encounter', 'come across', 'run into', 'greet', 'gather'],
            'include': ['contain', 'comprise', 'encompass', 'incorporate', 'involve'],
            'continue': ['proceed', 'persist', 'carry on', 'maintain', 'sustain'],
            'set': ['place', 'position', 'arrange', 'establish', 'determine'],
            'learn': ['study', 'acquire knowledge', 'master', 'understand', 'discover'],
            'change': ['alter', 'modify', 'transform', 'convert', 'adjust', 'adapt'],
            'lead': ['guide', 'direct', 'head', 'conduct', 'command', 'manage'],
            'understand': ['comprehend', 'grasp', 'realize', 'perceive', 'recognize'],
            'watch': ['observe', 'monitor', 'view', 'see', 'look at', 'examine'],
            'follow': ['pursue', 'chase', 'track', 'trail', 'accompany', 'succeed'],
            'stop': ['halt', 'cease', 'end', 'quit', 'discontinue', 'pause'],
            'create': ['make', 'produce', 'generate', 'form', 'construct', 'build'],
            'speak': ['talk', 'converse', 'communicate', 'express', 'articulate'],
            'read': ['peruse', 'study', 'examine', 'scan', 'browse', 'review'],
            'allow': ['permit', 'enable', 'authorize', 'approve', 'consent'],
            'add': ['include', 'append', 'attach', 'insert', 'incorporate'],
            'spend': ['use', 'consume', 'invest', 'devote', 'allocate', 'expend'],
            'grow': ['increase', 'expand', 'develop', 'mature', 'flourish', 'thrive'],
            'open': ['unlock', 'unseal', 'reveal', 'expose', 'start', 'begin'],
            'walk': ['stroll', 'stride', 'march', 'pace', 'step', 'trek'],
            'win': ['succeed', 'triumph', 'prevail', 'conquer', 'defeat', 'beat'],
            'offer': ['provide', 'give', 'present', 'propose', 'suggest', 'extend'],
            'remember': ['recall', 'recollect', 'reminisce', 'retain', 'keep in mind'],
            'love': ['adore', 'cherish', 'treasure', 'worship', 'care for', 'be fond of'],
            'consider': ['think about', 'ponder', 'contemplate', 'reflect', 'examine'],
            'appear': ['seem', 'look', 'emerge', 'surface', 'show up', 'materialize'],
            'buy': ['purchase', 'acquire', 'obtain', 'get', 'procure', 'invest in'],
            'wait': ['pause', 'delay', 'hold', 'stay', 'remain', 'linger'],
            'serve': ['assist', 'help', 'aid', 'provide', 'supply', 'cater'],
            'die': ['perish', 'expire', 'pass away', 'decease', 'succumb'],
            'send': ['dispatch', 'transmit', 'deliver', 'forward', 'mail', 'ship'],
            'expect': ['anticipate', 'await', 'look forward to', 'predict', 'foresee'],
            'build': ['construct', 'erect', 'create', 'make', 'assemble', 'establish'],
            'stay': ['remain', 'continue', 'persist', 'linger', 'abide', 'dwell'],
            'fall': ['drop', 'tumble', 'collapse', 'descend', 'plunge', 'decline'],
            'cut': ['slice', 'chop', 'sever', 'divide', 'split', 'trim'],
            'reach': ['arrive', 'attain', 'achieve', 'extend', 'stretch', 'contact'],
            'kill': ['murder', 'assassinate', 'eliminate', 'destroy', 'terminate'],
            'remain': ['stay', 'continue', 'persist', 'endure', 'last', 'survive']
        }

        with self._lock:
            self.synonyms.update(builtin_synonyms)

    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a word."""
        with self._lock:
            word_lower = word.lower()
            return self.synonyms.get(word_lower, [])

    def add_synonym(self, word: str, synonym: str):
        """Add a synonym relationship."""
        with self._lock:
            word_lower = word.lower()
            synonym_lower = synonym.lower()

            if word_lower not in self.synonyms:
                self.synonyms[word_lower] = []

            if synonym_lower not in self.synonyms[word_lower]:
                self.synonyms[word_lower].append(synonym_lower)

    def get_word_alternatives(self, word: str, context: str = "") -> List[str]:
        """Get word alternatives based on context."""
        alternatives = self.get_synonyms(word)

        # If no synonyms found, try to find similar words
        if not alternatives:
            alternatives = self._find_similar_words(word)

        return alternatives

    def _find_similar_words(self, word: str) -> List[str]:
        """Find similar words using basic pattern matching."""
        similar_words = []
        word_lower = word.lower()

        # Look for words with similar patterns
        for key in self.synonyms.keys():
            if self._calculate_similarity(word_lower, key) > 0.7:
                similar_words.extend(self.synonyms[key])

        return similar_words[:10]  # Return top 10

    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words."""
        if word1 == word2:
            return 1.0

        # Simple Levenshtein distance approximation
        len1, len2 = len(word1), len(word2)
        if len1 == 0 or len2 == 0:
            return 0.0

        # Count common characters
        common = 0
        for char in set(word1):
            if char in word2:
                common += min(word1.count(char), word2.count(char))

        return common / max(len1, len2)

    def suggest_improvements(self, text: str) -> List[Dict[str, Any]]:
        """Suggest word improvements for text."""
        suggestions = []
        words = re.findall(r'\b[a-zA-Z]+\b', text)

        # Common overused words to replace
        overused_words = {'very', 'really', 'quite', 'just', 'actually', 'basically', 'literally', 'totally', 'absolutely', 'completely', 'extremely', 'incredibly', 'amazing', 'awesome', 'great', 'good', 'nice', 'bad', 'thing', 'stuff', 'get', 'got', 'make', 'do', 'go', 'come', 'put', 'take', 'give', 'have', 'say', 'see', 'know', 'think', 'feel', 'look', 'turn', 'want', 'need', 'use', 'work', 'try', 'ask', 'seem', 'call', 'move', 'live', 'believe', 'hold', 'bring', 'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember', 'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'remain'}

        for word in words:
            word_lower = word.lower()
            if word_lower in overused_words:
                synonyms = self.get_synonyms(word_lower)
                if synonyms:
                    suggestions.append({
                        'word': word,
                        'type': 'overused',
                        'alternatives': synonyms[:5],
                        'reason': f"'{word}' is commonly overused"
                    })

        return suggestions

# Global instances
_text_analyzer = None
_synonym_cache = None

def get_text_analyzer() -> TextAnalyzer:
    """Get global text analyzer instance."""
    global _text_analyzer
    if _text_analyzer is None:
        _text_analyzer = TextAnalyzer()
    return _text_analyzer

def get_synonym_cache() -> SynonymCache:
    """Get global synonym cache instance."""
    global _synonym_cache
    if _synonym_cache is None:
        _synonym_cache = SynonymCache()
    return _synonym_cache
