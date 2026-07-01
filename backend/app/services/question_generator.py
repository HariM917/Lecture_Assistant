"""
Question Generator & Rewards System
Generate questions from lecture content and track engagement with rewards
"""
from typing import Dict, Any, List, Optional
from enum import Enum
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class QuestionType(Enum):
    """Types of questions that can be generated"""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    DEFINITION = "definition"
    APPLICATION = "application"
    SYNTHESIS = "synthesis"


class RewardType(Enum):
    """Types of rewards available"""
    POINTS = "points"
    BADGE = "badge"
    STREAK = "streak"
    ACHIEVEMENT = "achievement"


class QuestionGenerator:
    """Generate quiz questions from lecture content"""

    def __init__(self):
        self.bloom_levels = {
            'remember': ['what', 'who', 'where', 'when', 'define', 'list'],
            'understand': ['explain', 'describe', 'summarize', 'classify', 'compare'],
            'apply': ['solve', 'calculate', 'demonstrate', 'use', 'implement'],
            'analyze': ['distinguish', 'differentiate', 'organize', 'integrate'],
            'evaluate': ['judge', 'assess', 'critique', 'argue', 'defend'],
            'create': ['combine', 'compile', 'compose', 'design', 'hypothesize']
        }

        self.question_templates = {
            QuestionType.MULTIPLE_CHOICE: [
                "What is the {entity}?",
                "Which of the following best describes {entity}?",
                "According to the lecture, {entity} is most closely related to:",
                "How does {entity} relate to {related_concept}?"
            ],
            QuestionType.SHORT_ANSWER: [
                "Explain {concept} in your own words.",
                "What are the key characteristics of {entity}?",
                "How would you apply {concept} in {context}?",
                "Describe the relationship between {entity} and {related}."
            ],
            QuestionType.TRUE_FALSE: [
                "{statement}",
            ],
            QuestionType.DEFINITION: [
                "Define {term}",
                "What does {term} mean in the context of {domain}?",
            ],
            QuestionType.APPLICATION: [
                "How would you use {concept} to solve {problem}?",
                "Provide an example of {concept} in {domain}",
            ],
            QuestionType.SYNTHESIS: [
                "How do {concept1} and {concept2} work together?",
                "Create a solution combining {concept1} and {concept2}",
            ]
        }

    def generate_questions(self, content: str, num_questions: int = 5, 
                          question_types: List[QuestionType] = None,
                          bloom_level: str = 'understand') -> List[Dict[str, Any]]:
        """
        Generate quiz questions from lecture content
        
        Args:
            content: Lecture transcript or content
            num_questions: Number of questions to generate
            question_types: Specific question types to generate
            bloom_level: Cognitive level (remember, understand, apply, analyze, evaluate, create)
        """
        try:
            if question_types is None:
                question_types = [QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER]

            # Extract key entities and concepts
            entities = self._extract_entities(content)
            concepts = self._extract_concepts(content)
            keywords = self._extract_keywords(content)

            questions = []
            question_type_cycle = question_types * ((num_questions // len(question_types)) + 1)

            for i in range(num_questions):
                q_type = question_type_cycle[i]
                question = self._generate_single_question(
                    q_type, entities, concepts, keywords, bloom_level, content
                )
                if question:
                    questions.append(question)

            logger.info(f"Generated {len(questions)} questions from content")
            return questions

        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return []

    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities from content"""
        # Simple heuristic: capitalized words
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        return list(set(entities))[:10]

    def _extract_concepts(self, content: str) -> List[str]:
        """Extract main concepts (frequent noun phrases)"""
        # Simple approach: words that appear multiple times
        words = content.lower().split()
        from collections import Counter
        word_freq = Counter(w for w in words if len(w) > 5)
        concepts = [word for word, _ in word_freq.most_common(15)]
        return concepts

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # Find capitalized terms and technical words
        keywords = re.findall(r'\b[A-Z_]+\b', content)
        return list(set(keywords))[:10]

    def _generate_single_question(self, q_type: QuestionType, entities: List[str],
                                 concepts: List[str], keywords: List[str],
                                 bloom_level: str, content: str) -> Optional[Dict[str, Any]]:
        """Generate a single question"""
        entity = entities[0] if entities else "concept"
        concept = concepts[0] if concepts else "topic"
        related = concepts[1] if len(concepts) > 1 else "related concept"

        if q_type == QuestionType.MULTIPLE_CHOICE:
            return {
                'id': self._generate_id(),
                'type': q_type.value,
                'question': f"What is the significance of {entity} in the lecture?",
                'bloom_level': bloom_level,
                'options': [
                    f"{entity} is mentioned as a key concept",
                    f"{entity} is an example of {concept}",
                    f"{entity} is a prerequisite for {related}",
                    "All of the above"
                ],
                'correct_answer': 0,
                'difficulty': bloom_level,
                'explanation': f"According to the lecture, {entity} is central to understanding {concept}.",
                'points': self._calculate_points(bloom_level),
                'hints': [f"Look for where {entity} is discussed", f"Consider its relationship to {concept}"]
            }

        elif q_type == QuestionType.SHORT_ANSWER:
            return {
                'id': self._generate_id(),
                'type': q_type.value,
                'question': f"Explain how {entity} relates to {concept}.",
                'bloom_level': bloom_level,
                'difficulty': bloom_level,
                'expected_keywords': [entity.lower(), concept.lower()],
                'points': self._calculate_points(bloom_level),
                'explanation': "Your answer should demonstrate understanding of the relationship.",
                'hints': ["Think about cause and effect", "Consider real-world applications"]
            }

        elif q_type == QuestionType.TRUE_FALSE:
            return {
                'id': self._generate_id(),
                'type': q_type.value,
                'question': f"{entity} is primarily used for {concept}.",
                'bloom_level': bloom_level,
                'correct_answer': True,
                'difficulty': bloom_level,
                'points': self._calculate_points(bloom_level),
                'explanation': f"This statement is true because {entity} plays a role in {concept}."
            }

        elif q_type == QuestionType.APPLICATION:
            return {
                'id': self._generate_id(),
                'type': q_type.value,
                'question': f"How would you apply {concept} when working with {entity}?",
                'bloom_level': bloom_level,
                'difficulty': bloom_level,
                'expected_keywords': [concept.lower(), entity.lower()],
                'points': self._calculate_points(bloom_level),
                'explanation': "Demonstrate your ability to apply theoretical knowledge in practice."
            }

        return None

    def _generate_id(self) -> str:
        """Generate unique question ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def _calculate_points(self, bloom_level: str) -> int:
        """Calculate points based on difficulty"""
        points_map = {
            'remember': 5,
            'understand': 10,
            'apply': 15,
            'analyze': 20,
            'evaluate': 25,
            'create': 30
        }
        return points_map.get(bloom_level, 10)


class RewardsSystem:
    """Manage rewards and gamification for student engagement"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.points = 0
        self.badges = []
        self.achievements = []
        self.streak = 0
        self.level = 1
        self.history = []

        self.badge_definitions = {
            'first_question': {'name': 'First Step', 'icon': '🎯', 'points': 10},
            'streak_5': {'name': 'On Fire', 'icon': '🔥', 'points': 50},
            'streak_10': {'name': 'Unstoppable', 'icon': '⚡', 'points': 100},
            'perfect_score': {'name': 'Perfect', 'icon': '⭐', 'points': 100},
            'fast_answer': {'name': 'Speed Demon', 'icon': '🚀', 'points': 25},
            'comprehensive': {'name': 'Thorough', 'icon': '🧠', 'points': 75},
        }

        self.achievement_definitions = {
            'level_2': {'name': 'Rising Star', 'required_points': 100},
            'level_3': {'name': 'Scholar', 'required_points': 250},
            'level_5': {'name': 'Master', 'required_points': 500},
            'diversity': {'name': 'Polymath', 'topics': 5},
        }

    def award_points(self, points: int, reason: str) -> Dict[str, Any]:
        """Award points for an action"""
        self.points += points
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': reason,
            'points': points,
            'total': self.points
        })
        logger.info(f"User {self.user_id} awarded {points} points: {reason}")

        return {
            'points_awarded': points,
            'total_points': self.points,
            'reason': reason,
            'level_progress': self._get_level_progress()
        }

    def submit_answer(self, question_id: str, is_correct: bool, time_taken_seconds: int = 0) -> Dict[str, Any]:
        """Handle answer submission and rewards"""
        rewards = {'points': 0, 'badges': [], 'achievements': []}

        if is_correct:
            # Base points
            points = 10
            rewards['points'] += points

            # Time bonus
            if time_taken_seconds < 30:
                time_bonus = 5
                rewards['points'] += time_bonus
                rewards['badges'].append(self._try_award_badge('fast_answer'))

            # Update streak
            self.streak += 1

            # Check streak badges
            if self.streak == 5:
                badge = self._try_award_badge('streak_5')
                if badge:
                    rewards['badges'].append(badge)
                    rewards['points'] += badge['points']

            if self.streak == 10:
                badge = self._try_award_badge('streak_10')
                if badge:
                    rewards['badges'].append(badge)
                    rewards['points'] += badge['points']

        else:
            # Small points for attempting
            rewards['points'] += 2
            self.streak = 0

        # Award points
        self.award_points(rewards['points'], f"Answered question {question_id}")

        # Check for level up
        new_level = self._check_level_up()
        if new_level > self.level:
            rewards['level_up'] = {
                'from': self.level,
                'to': new_level,
                'bonus_points': new_level * 10
            }
            self.level = new_level
            self.points += new_level * 10

        return rewards

    def _try_award_badge(self, badge_type: str) -> Optional[Dict[str, Any]]:
        """Try to award a badge if not already earned"""
        if badge_type in self.badges:
            return None  # Already have this badge

        if badge_type in self.badge_definitions:
            badge = self.badge_definitions[badge_type]
            self.badges.append(badge_type)
            return badge

        return None

    def _check_level_up(self) -> int:
        """Check if user has leveled up"""
        points_per_level = 100
        new_level = (self.points // points_per_level) + 1
        return new_level

    def _get_level_progress(self) -> Dict[str, Any]:
        """Get progress toward next level"""
        points_per_level = 100
        current_level = (self.points // points_per_level) + 1
        points_in_level = self.points % points_per_level
        progress_percent = (points_in_level / points_per_level) * 100

        return {
            'current_level': current_level,
            'points_in_level': points_in_level,
            'points_to_next_level': points_per_level - points_in_level,
            'progress_percent': progress_percent
        }

    def get_user_stats(self) -> Dict[str, Any]:
        """Get complete user statistics"""
        return {
            'user_id': self.user_id,
            'total_points': self.points,
            'level': self.level,
            'badges': self.badges,
            'streak': self.streak,
            'achievements': self.achievements,
            'level_progress': self._get_level_progress(),
            'recent_history': self.history[-5:],
            'total_answers': len(self.history),
            'accuracy': self._calculate_accuracy()
        }

    def _calculate_accuracy(self) -> float:
        """Calculate overall accuracy from history"""
        if not self.history:
            return 0.0

        correct = sum(1 for h in self.history if h['points'] >= 10)
        total = len(self.history)
        return (correct / total) * 100 if total > 0 else 0.0

    def leaderboard_entry(self) -> Dict[str, Any]:
        """Get entry for leaderboard"""
        return {
            'user_id': self.user_id,
            'points': self.points,
            'level': self.level,
            'streak': self.streak,
            'badge_count': len(self.badges),
            'accuracy': self._calculate_accuracy(),
            'timestamp': datetime.now().isoformat()
        }
