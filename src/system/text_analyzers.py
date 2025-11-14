"""
Advanced Text Analyzers for AAWT
Provides grammar checking, style analysis, and readability scoring with external API support.
"""

import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import re

logger = logging.getLogger(__name__)


class GrammarAnalyzer:
    """Advanced grammar analysis with vocabulary assessment."""
    
    def __init__(self, settings_manager=None):
        """Initialize grammar analyzer."""
        self.settings = settings_manager
        self.stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
        }
    
    def analyze_grammar(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive grammar analysis.
        
        Returns:
            Dictionary with grammar analysis results
        """
        words = self._extract_words(text)
        sentences = self._extract_sentences(text)
        
        return {
            'complex_words': self._identify_complex_words(words),
            'repeated_words': self._find_repeated_words(words),
            'sentence_issues': self._check_sentence_structure(sentences),
            'style_issues': self._check_style(text, sentences),
            'vocabulary_score': self._calculate_vocabulary_score(words),
            'grammar_issues': self._find_grammar_issues(text, sentences)
        }
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract meaningful words from text."""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _identify_complex_words(self, words: List[str]) -> List[Dict[str, Any]]:
        """Identify complex vocabulary."""
        complex_words = []
        
        for word in set(words):
            syllables = self._count_syllables(word)
            if syllables >= 3 or len(word) >= 10:
                complex_words.append({
                    'word': word,
                    'syllables': syllables,
                    'length': len(word),
                    'difficulty': 'high' if syllables >= 4 else 'medium'
                })
        
        return sorted(complex_words, key=lambda x: x['syllables'], reverse=True)[:20]
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        
        # Remove trailing 'e'
        if word.endswith('e'):
            word = word[:-1]
        
        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        return max(1, syllable_count)
    
    def _find_repeated_words(self, words: List[str], threshold: int = 3) -> List[Tuple[str, int]]:
        """Find frequently repeated words."""
        word_counts = Counter(words)
        repeated = [(word, count) for word, count in word_counts.items() if count >= threshold]
        return sorted(repeated, key=lambda x: x[1], reverse=True)[:20]
    
    def _check_sentence_structure(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """Check for sentence structure issues."""
        issues = []
        
        for i, sentence in enumerate(sentences, 1):
            words = re.findall(r'\b\w+\b', sentence)
            word_count = len(words)
            
            # Check for sentence fragments (too short)
            if word_count < 3:
                issues.append({
                    'type': 'fragment',
                    'sentence_num': i,
                    'text': sentence[:100],
                    'description': 'Sentence may be a fragment (too short)'
                })
            
            # Check for run-on sentences (too long)
            elif word_count > 30:
                issues.append({
                    'type': 'run-on',
                    'sentence_num': i,
                    'text': sentence[:100] + '...',
                    'description': f'Long sentence ({word_count} words) - consider breaking up'
                })
            
            # Check for missing punctuation
            if not sentence.strip().endswith(('.', '!', '?')):
                issues.append({
                    'type': 'punctuation',
                    'sentence_num': i,
                    'text': sentence[:100],
                    'description': 'Missing terminal punctuation'
                })
        
        return issues
    
    def _check_style(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Check for style issues."""
        issues = []
        
        # Check for passive voice
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are']
        passive_count = sum(1 for indicator in passive_indicators if indicator in text.lower())
        
        if passive_count > len(sentences) * 0.3:
            issues.append({
                'type': 'passive_voice',
                'description': f'High passive voice usage detected ({passive_count} instances)',
                'suggestion': 'Consider using more active voice constructions'
            })
        
        # Check for clichés
        cliches = ['at the end of the day', 'in this day and age', 'needless to say', 
                  'all in all', 'when all is said and done']
        for cliche in cliches:
            if cliche in text.lower():
                issues.append({
                    'type': 'cliche',
                    'description': f'Cliché detected: "{cliche}"',
                    'suggestion': 'Consider a more original expression'
                })
        
        # Check for weak verbs
        weak_verbs = ['got', 'get', 'went', 'said', 'made', 'put']
        text_lower = text.lower()
        for verb in weak_verbs:
            count = text_lower.count(f' {verb} ')
            if count > 5:
                issues.append({
                    'type': 'weak_verb',
                    'description': f'Overuse of weak verb "{verb}" ({count} times)',
                    'suggestion': 'Consider stronger, more specific verbs'
                })
        
        return issues
    
    def _calculate_vocabulary_score(self, words: List[str]) -> Dict[str, Any]:
        """Calculate vocabulary sophistication score."""
        total_words = len(words)
        unique_words = len(set(words))
        
        # Calculate average word length
        avg_length = sum(len(w) for w in words) / total_words if total_words > 0 else 0
        
        # Count complex words
        complex_count = sum(1 for w in words if len(w) >= 8 or self._count_syllables(w) >= 3)
        
        # Calculate vocabulary richness score (0-100)
        diversity_score = (unique_words / total_words * 100) if total_words > 0 else 0
        complexity_score = (complex_count / total_words * 100) if total_words > 0 else 0
        
        overall_score = (diversity_score * 0.6 + complexity_score * 0.4)
        
        return {
            'overall_score': round(overall_score, 2),
            'diversity_score': round(diversity_score, 2),
            'complexity_score': round(complexity_score, 2),
            'avg_word_length': round(avg_length, 2),
            'unique_words': unique_words,
            'total_words': total_words,
            'complex_words': complex_count,
            'level': self._get_vocabulary_level(overall_score)
        }
    
    def _get_vocabulary_level(self, score: float) -> str:
        """Get vocabulary level description."""
        if score >= 70:
            return 'Advanced'
        elif score >= 50:
            return 'Intermediate'
        else:
            return 'Basic'
    
    def _find_grammar_issues(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Find common grammar issues."""
        issues = []
        
        # Check for double spaces
        if '  ' in text:
            issues.append({
                'type': 'spacing',
                'description': 'Double spaces detected',
                'suggestion': 'Replace double spaces with single spaces'
            })
        
        # Check for missing commas in lists
        list_pattern = r'\b\w+\s+\w+\s+and\s+\w+\b'
        if re.search(list_pattern, text):
            issues.append({
                'type': 'comma',
                'description': 'Possible missing Oxford comma in list',
                'suggestion': 'Consider adding commas before "and" in lists'
            })
        
        # Check for sentence starting with conjunction
        conjunction_starters = ['And', 'But', 'Or', 'So']
        for sentence in sentences:
            for conj in conjunction_starters:
                if sentence.strip().startswith(conj + ' '):
                    issues.append({
                        'type': 'conjunction_start',
                        'description': f'Sentence starts with conjunction: {conj}',
                        'suggestion': 'Consider rephrasing or combining with previous sentence'
                    })
                    break
        
        return issues[:10]  # Limit to top 10 issues
    
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a word using Words API or fallback."""
        if not self.settings or not self.settings.get('api.words_api_key'):
            return self._get_local_synonyms(word)
        
        try:
            api_key = self.settings.get('api.words_api_key')
            url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/synonyms"
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('synonyms', [])[:10]
        except Exception as e:
            logger.warning(f"Words API failed, using fallback: {e}")
        
        return self._get_local_synonyms(word)
    
    def _get_local_synonyms(self, word: str) -> List[str]:
        """Get local synonym suggestions."""
        # Basic synonym mapping for common words
        synonym_map = {
            'good': ['excellent', 'fine', 'great', 'wonderful', 'superb'],
            'bad': ['poor', 'terrible', 'awful', 'dreadful', 'horrible'],
            'big': ['large', 'huge', 'enormous', 'massive', 'giant'],
            'small': ['tiny', 'little', 'minute', 'petite', 'miniature'],
            'said': ['stated', 'mentioned', 'declared', 'remarked', 'noted'],
            'went': ['traveled', 'proceeded', 'walked', 'moved', 'journeyed'],
            'got': ['obtained', 'acquired', 'received', 'gained', 'secured'],
            'made': ['created', 'produced', 'constructed', 'built', 'formed'],
            'happy': ['joyful', 'pleased', 'content', 'delighted', 'cheerful'],
            'sad': ['unhappy', 'sorrowful', 'melancholy', 'dejected', 'gloomy']
        }
        
        return synonym_map.get(word.lower(), [])


class ReadabilityAnalyzer:
    """Advanced readability analysis with API support."""
    
    def __init__(self, settings_manager=None):
        """Initialize readability analyzer."""
        self.settings = settings_manager
    
    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive readability analysis.
        
        Returns:
            Dictionary with readability metrics
        """
        # Try external API first
        if self.settings and self.settings.get('api.apyhub_key'):
            api_result = self._analyze_with_api(text)
            if api_result:
                return api_result
        
        # Fallback to local analysis
        return self._analyze_locally(text)
    
    def _analyze_with_api(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze with ApyHub API."""
        try:
            api_key = self.settings.get('api.apyhub_key')
            url = "https://api.apyhub.com/analyze/readability"
            headers = {
                "apy-token": api_key,
                "Content-Type": "application/json"
            }
            data = {"text": text}
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"ApyHub API failed: {e}")
        
        return None
    
    def _analyze_locally(self, text: str) -> Dict[str, Any]:
        """Perform local readability analysis."""
        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        word_count = len(words)
        sentence_count = max(len(sentences), 1)
        
        # Count syllables
        total_syllables = sum(self._count_syllables(w) for w in words)
        
        # Flesch Reading Ease
        if word_count > 0 and sentence_count > 0:
            fre_score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (total_syllables / word_count)
            fre_score = max(0, min(100, fre_score))
        else:
            fre_score = 0
        
        # Flesch-Kincaid Grade Level
        if word_count > 0 and sentence_count > 0:
            fk_grade = 0.39 * (word_count / sentence_count) + 11.8 * (total_syllables / word_count) - 15.59
            fk_grade = max(0, fk_grade)
        else:
            fk_grade = 0
        
        return {
            'flesch_reading_ease': round(fre_score, 2),
            'flesch_kincaid_grade': round(fk_grade, 2),
            'grade_level': self._get_grade_level(fre_score),
            'difficulty': self._get_difficulty(fre_score),
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_words_per_sentence': round(word_count / sentence_count, 2) if sentence_count > 0 else 0,
            'syllable_count': total_syllables,
            'avg_syllables_per_word': round(total_syllables / word_count, 2) if word_count > 0 else 0,
            'reading_time_minutes': round(word_count / 250, 2),
            'audience_suitability': self._get_audience_suitability(fre_score)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        
        if word.endswith('e'):
            word = word[:-1]
        
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        return max(1, syllable_count)
    
    def _get_grade_level(self, score: float) -> str:
        """Get grade level from Flesch Reading Ease score."""
        if score >= 90:
            return '5th Grade'
        elif score >= 80:
            return '6th Grade'
        elif score >= 70:
            return '7th-8th Grade'
        elif score >= 60:
            return '9th-10th Grade'
        elif score >= 50:
            return '11th-12th Grade'
        elif score >= 30:
            return 'College'
        else:
            return 'College Graduate'
    
    def _get_difficulty(self, score: float) -> str:
        """Get difficulty level from score."""
        if score >= 80:
            return 'Easy'
        elif score >= 60:
            return 'Moderate'
        else:
            return 'Difficult'
    
    def _get_audience_suitability(self, score: float) -> Dict[str, bool]:
        """Determine audience suitability."""
        return {
            'children': score >= 80,
            'young_adults': score >= 70,
            'general': score >= 60,
            'academic': score >= 30,
            'professional': True  # All levels acceptable for professional
        }
