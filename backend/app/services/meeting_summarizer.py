"""
Meeting Summarizer
Specialized summarization for meetings including action items, decisions, and participants
"""
from typing import Dict, Any, List
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MeetingSummarizer:
    """Specialized summarization for meeting transcripts"""

    def __init__(self):
        self.action_keywords = [
            'action', 'task', 'todo', 'do', 'need to', 'must', 'should',
            'will', 'going to', 'responsible for', 'assigned to', 'owner',
            'deadline', 'due', 'by', 'complete', 'implement'
        ]

        self.decision_keywords = [
            'decide', 'agreed', 'consensus', 'approve', 'approved', 'reject',
            'rejected', 'declined', 'go ahead', 'greenlit', 'confirmed',
            'confirmed', 'resolved', 'resolved', 'final', 'officially'
        ]

        self.risk_keywords = [
            'risk', 'issue', 'concern', 'challenge', 'problem', 'blocker',
            'blocked', 'stuck', 'difficult', 'problematic', 'failure',
            'failure risk', 'dependency'
        ]

        self.participant_pattern = r'([A-Z][a-z]+ [A-Z][a-z]*|[A-Z][a-z]+):\s*'

    def summarize_meeting(self, transcript: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Summarize a meeting transcript
        
        Args:
            transcript: Full meeting transcript
            metadata: Optional dict with meeting_title, date, duration, etc.
        """
        try:
            if not transcript:
                return self._empty_summary()

            # Extract structured information
            participants = self._extract_participants(transcript)
            action_items = self._extract_action_items(transcript)
            decisions = self._extract_decisions(transcript)
            risks = self._extract_risks(transcript)
            topics = self._extract_topics(transcript)
            key_quotes = self._extract_key_quotes(transcript)

            # Generate narrative summary
            narrative = self._generate_narrative(topics, decisions, action_items)

            summary = {
                'meeting_title': metadata.get('title', 'Meeting') if metadata else 'Meeting',
                'date': metadata.get('date', datetime.now().isoformat()) if metadata else datetime.now().isoformat(),
                'duration_minutes': metadata.get('duration_minutes', 0) if metadata else 0,
                'participants': participants,
                'total_participants': len(participants),
                'narrative_summary': narrative,
                'topics_discussed': topics,
                'key_decisions': decisions,
                'action_items': action_items,
                'risks_identified': risks,
                'key_quotes': key_quotes,
                'next_meeting_suggested': self._suggest_next_meeting(action_items),
                'sentiment_overall': 'positive' if len(decisions) > 0 else 'neutral',
                'urgency_level': self._calculate_urgency(action_items, risks)
            }

            logger.info(f"Meeting summarized: {len(participants)} participants, {len(action_items)} actions")
            return summary

        except Exception as e:
            logger.error(f"Meeting summarization error: {e}")
            return self._empty_summary()

    def _extract_participants(self, transcript: str) -> List[str]:
        """Extract participant names from transcript"""
        matches = re.findall(self.participant_pattern, transcript)
        participants = list(set(m.strip() for m in matches if m.strip()))
        return participants[:10]  # Top 10 participants

    def _extract_action_items(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract action items from transcript"""
        action_items = []
        lines = transcript.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in self.action_keywords):
                # Extract owner if mentioned
                owner = None
                match = re.search(self.participant_pattern, line)
                if match:
                    owner = match.group(1)

                # Extract deadline if mentioned
                deadline = None
                deadline_match = re.search(r'(by|due|before)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', line_lower)
                if deadline_match:
                    deadline = deadline_match.group(2)

                action_items.append({
                    'description': line.strip(),
                    'owner': owner,
                    'deadline': deadline,
                    'priority': 'high' if any(word in line_lower for word in ['urgent', 'asap', 'critical']) else 'medium',
                    'status': 'pending'
                })

        return action_items[:20]  # Top 20 action items

    def _extract_decisions(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract decisions made during meeting"""
        decisions = []
        lines = transcript.split('\n')

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in self.decision_keywords):
                decisions.append({
                    'decision': line.strip(),
                    'context': self._get_context(line, lines),
                    'rationale': self._extract_rationale(line, lines)
                })

        return decisions[:15]  # Top 15 decisions

    def _extract_risks(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract risks and concerns mentioned"""
        risks = []
        lines = transcript.split('\n')

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in self.risk_keywords):
                risks.append({
                    'risk': line.strip(),
                    'severity': 'high' if any(word in line_lower for word in ['critical', 'severe', 'major']) else 'medium',
                    'mitigation': self._suggest_mitigation(line)
                })

        return risks[:10]  # Top 10 risks

    def _extract_topics(self, transcript: str) -> List[str]:
        """Extract main topics discussed"""
        # Simple heuristic: capitalize phrases at beginning of lines or after colons
        topics = []
        lines = transcript.split('\n')

        for line in lines:
            # Look for lines that might be topic headers
            if re.match(r'^[A-Z][a-zA-Z\s]+:', line):
                topic = line.split(':')[0].strip()
                if topic not in topics and len(topic) < 50:
                    topics.append(topic)

        return topics[:10] if topics else ['General Discussion', 'Project Updates', 'Planning']

    def _extract_key_quotes(self, transcript: str) -> List[Dict[str, str]]:
        """Extract important quotes from meeting"""
        quotes = []
        lines = transcript.split('\n')

        for line in lines:
            if len(line) > 30 and any(word in line for word in ['important', 'key', 'critical', 'must', 'should']):
                speaker = None
                match = re.match(self.participant_pattern, line)
                if match:
                    speaker = match.group(1)
                    quote = line[len(match.group(0)):].strip()
                else:
                    quote = line.strip()

                quotes.append({
                    'speaker': speaker or 'Unknown',
                    'quote': quote[:100]
                })

        return quotes[:5]  # Top 5 quotes

    def _generate_narrative(self, topics: List[str], decisions: List[Dict], actions: List[Dict]) -> str:
        """Generate a narrative summary"""
        narrative = f"Meeting discussed {len(topics)} topics. "
        
        if topics:
            narrative += f"Main focus: {', '.join(topics[:3])}. "
        
        if decisions:
            narrative += f"{len(decisions)} key decision(s) made. "
        
        if actions:
            narrative += f"{len(actions)} action item(s) assigned. "
        
        narrative += "See details below for specifics."
        return narrative

    def _suggest_next_meeting(self, action_items: List[Dict]) -> Dict[str, Any]:
        """Suggest when next meeting should be held"""
        urgent_actions = [a for a in action_items if a['priority'] == 'high']
        
        if urgent_actions:
            return {
                'suggested': True,
                'reason': f"{len(urgent_actions)} urgent action items pending",
                'timeline': '3-5 days',
                'type': 'Status Update'
            }
        
        return {
            'suggested': False,
            'timeline': '1-2 weeks',
            'type': 'Regular Check-in'
        }

    def _calculate_urgency(self, actions: List[Dict], risks: List[Dict]) -> str:
        """Calculate overall meeting urgency"""
        urgent_actions = sum(1 for a in actions if a['priority'] == 'high')
        high_risks = sum(1 for r in risks if r['severity'] == 'high')

        total_score = urgent_actions * 2 + high_risks * 1.5

        if total_score > 5:
            return 'critical'
        elif total_score > 2:
            return 'high'
        else:
            return 'normal'

    def _get_context(self, line: str, all_lines: List[str]) -> str:
        """Get context around a line"""
        idx = all_lines.index(line) if line in all_lines else 0
        context_lines = all_lines[max(0, idx-1):min(len(all_lines), idx+2)]
        return ' '.join(context_lines)

    def _extract_rationale(self, decision: str, all_lines: List[str]) -> str:
        """Extract rationale for decision"""
        if 'because' in decision.lower():
            return decision.split('because')[1].strip()
        return 'Rationale not explicitly stated'

    def _suggest_mitigation(self, risk: str) -> str:
        """Suggest mitigation for identified risk"""
        if 'resource' in risk.lower():
            return 'Allocate additional resources or adjust timeline'
        elif 'dependency' in risk.lower():
            return 'Identify and communicate with dependent teams'
        elif 'timeline' in risk.lower():
            return 'Establish buffer and communicate delays early'
        else:
            return 'Create mitigation plan and assign owner'

    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty meeting summary"""
        return {
            'meeting_title': 'Meeting',
            'date': datetime.now().isoformat(),
            'duration_minutes': 0,
            'participants': [],
            'total_participants': 0,
            'narrative_summary': 'No transcript provided',
            'topics_discussed': [],
            'key_decisions': [],
            'action_items': [],
            'risks_identified': [],
            'key_quotes': [],
            'next_meeting_suggested': {'suggested': False},
            'sentiment_overall': 'neutral',
            'urgency_level': 'normal'
        }

    # Helper method for batch summarization
    def summarize_multiple_meetings(self, transcripts: List[str], thread_id: str = None) -> Dict[str, Any]:
        """Summarize multiple meetings and create aggregate view"""
        summaries = [self.summarize_meeting(t) for t in transcripts]
        
        # Aggregate action items across meetings
        all_actions = []
        for summary in summaries:
            all_actions.extend(summary['action_items'])

        # Find recurring topics
        all_topics = []
        for summary in summaries:
            all_topics.extend(summary['topics_discussed'])

        return {
            'meeting_count': len(transcripts),
            'summaries': summaries,
            'aggregated_actions': sorted(all_actions, key=lambda x: x['priority'], reverse=True)[:20],
            'recurring_topics': self._find_recurring_topics(all_topics),
            'thread_id': thread_id,
            'last_updated': datetime.now().isoformat()
        }

    def _find_recurring_topics(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Find topics that appear across multiple meetings"""
        from collections import Counter
        topic_counts = Counter(topics)
        recurring = [
            {'topic': topic, 'frequency': count}
            for topic, count in topic_counts.most_common(5) if count > 1
        ]
        return recurring
