# Advanced Features Documentation & API Reference

## 🎯 New Advanced Features

### 1. **Sentiment Analysis** 📊
Analyze the emotional tone and sentiment of lecture content at word and sentence levels.

#### Endpoints:
```bash
POST /api/lecture/advanced/sentiment/analyze
  ?text=string&context=lecture|meeting|casual

POST /api/lecture/advanced/sentiment/analyze-batch
  body: {texts: [string], context: string}

POST /api/lecture/advanced/sentiment/analyze-sentences
  ?text=string
```

#### Response Example:
```json
{
  "status": "success",
  "data": {
    "overall": 0.75,
    "confidence": 0.88,
    "emotions": {
      "joy": 0.4,
      "sadness": 0.1,
      "anger": 0.05,
      "fear": 0.02,
      "surprise": 0.15,
      "neutral": 0.28
    },
    "intensity": "medium",
    "keywords": ["excellent", "amazing", "wonderful"],
    "sentiment_label": "positive",
    "context": "lecture"
  }
}
```

#### Use Cases:
- Track lecture engagement levels
- Identify passionate topics
- Detect difficult/frustrating content
- Monitor student emotional response

---

### 2. **Cultural Context Translator** 🌍
Translate with awareness of idioms, cultural nuances, slangs, and emotional expressions.

#### Endpoints:
```bash
POST /api/lecture/advanced/translate/cultural
  ?text=string&source_lang=en&target_lang=ta&context=general|academic|casual
```

#### Features:
- **Idiomatic Expression Handling**: "break the ice" → Indian equivalent
- **Slang Processing**: Converts casual language appropriately
- **Emotion Awareness**: Maintains cultural emotional meaning
- **Formality Levels**: Adapts to formal, informal, or academic context

#### Response Example:
```json
{
  "status": "success",
  "data": {
    "original_text": "Neural networks are a piece of cake",
    "translated_text": "[Tamil]: Neural networks are very easy concepts",
    "source_language": "en",
    "target_language": "ta",
    "idioms_detected": {
      "idiom": "piece of cake",
      "translations": {"ta": "மிகவும் சுலபமான விஷயம்"}
    },
    "slang_detected": [],
    "emotions_detected": [],
    "formality_level": "academic",
    "cultural_notes": ["Contains idiomatic expressions - literal translation may not convey meaning"],
    "confidence": 0.85
  }
}
```

#### Supported Languages:
- English (en), Tamil (ta), Hindi (hi), Telugu (te), Kannada (kn), Malayalam (ml)

---

### 3. **Meeting Summarizer** 📝
Specialized summarization for meeting transcripts with action items, decisions, and risks.

#### Endpoints:
```bash
POST /api/lecture/advanced/meeting/summarize
  ?transcript=string&title=string&duration=integer

POST /api/lecture/advanced/meeting/summarize-batch
  body: {transcripts: [string], thread_id: string}
```

#### Features:
- **Action Item Extraction**: Identifies who-what-when tasks
- **Decision Tracking**: Captures key decisions and rationale
- **Risk Identification**: Highlights concerns and blockers
- **Participant Mapping**: Tracks who said what
- **Next Meeting Suggestion**: Recommends follow-up meetings

#### Response Example:
```json
{
  "status": "success",
  "data": {
    "meeting_title": "Project Planning",
    "date": "2026-03-30T10:00:00",
    "duration_minutes": 45,
    "participants": ["Dr. Smith", "John", "Sarah"],
    "total_participants": 3,
    "narrative_summary": "Meeting discussed 3 topics. Main focus: Project Timeline, Resource Allocation, Risk Mitigation. 2 key decisions made. 5 action items assigned.",
    "topics_discussed": ["Project Timeline", "Resource Allocation", "Risk Mitigation"],
    "key_decisions": [
      {
        "decision": "Decided to extend timeline by 2 weeks",
        "context": "...",
        "rationale": "Need more resources for QA"
      }
    ],
    "action_items": [
      {
        "description": "Complete resource allocation by March 31",
        "owner": "Dr. Smith",
        "deadline": "2026-03-31",
        "priority": "high",
        "status": "pending"
      }
    ],
    "risks_identified": [
      {
        "risk": "Critical: Resource shortage",
        "severity": "high",
        "mitigation": "Allocate additional resources or adjust timeline"
      }
    ],
    "next_meeting_suggested": {
      "suggested": true,
      "reason": "1 urgent action item pending",
      "timeline": "3-5 days",
      "type": "Status Update"
    },
    "urgency_level": "critical"
  }
}
```

---

### 4. **AI Context Memory Translator** 🧠
Translate while maintaining context consistency across multiple translations.

#### Endpoints:
```bash
POST /api/lecture/advanced/translate/context-aware
  ?text=string&source_lang=en&target_lang=ta&context_type=general

POST /api/lecture/advanced/translate/batch-with-context
  body: {texts: [string], source_lang: string, target_lang: string}

GET /api/lecture/advanced/translate/memory-report
```

#### Features:
- **Entity Consistency**: Same proper nouns translated identically
- **Terminology Memory**: Technical terms stay consistent
- **Context Stacking**: Maintains conversation context
- **Memory Efficiency**: Learns from previous translations

#### Memory Report Example:
```json
{
  "status": "success",
  "data": {
    "total_translations": 42,
    "context_level": 3,
    "entities_consistency_maintained": 12,
    "terminology_consistency_maintained": 8,
    "memory_efficiency": 0.475,
    "timestamp": "2026-03-30T10:15:00"
  }
}
```

---

### 5. **Question Generator** ❓
Automatically generate quiz questions from lecture content across Bloom's taxonomy levels.

#### Endpoints:
```bash
POST /api/lecture/advanced/questions/generate
  ?content=string&num_questions=5&bloom_level=understand&question_types=multiple_choice,short_answer
```

#### Question Types:
- `multiple_choice`: 4 options with one correct answer
- `short_answer`: Free-form response (keywords validated)
- `true_false`: Binary true/false statements
- `definition`: Define terminology
- `application`: Apply concepts to scenarios
- `synthesis`: Combine multiple concepts

#### Bloom's Levels:
- `remember` (5 points): Recall facts
- `understand` (10 points): Comprehend concepts
- `apply` (15 points): Use in new situations
- `analyze` (20 points): Break down components
- `evaluate` (25 points): Judge and assess
- `create` (30 points): Synthesize and build

#### Response Example:
```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "id": "abc12345",
      "type": "multiple_choice",
      "question": "What is the significance of neural networks in machine learning?",
      "bloom_level": "understand",
      "options": [
        "Neural networks are mentioned as a key concept",
        "Neural networks are an example of deep learning",
        "Neural networks are a prerequisite for transformers",
        "All of the above"
      ],
      "correct_answer": 0,
      "difficulty": "understand",
      "explanation": "According to the lecture, neural networks are central to understanding deep learning.",
      "points": 10,
      "hints": [
        "Look for where neural networks are discussed",
        "Consider their relationship to deep learning"
      ]
    }
  ]
}
```

---

### 6. **Rewards & Gamification System** 🏆

#### Endpoints:

**Initialize Rewards:**
```bash
POST /api/lecture/advanced/rewards/init
  ?user_id=string
```

**Submit Answer:**
```bash
POST /api/lecture/advanced/rewards/submit-answer
  ?user_id=string&question_id=string&is_correct=boolean&time_taken=integer
```

**Get User Stats:**
```bash
GET /api/lecture/advanced/rewards/stats/{user_id}
```

**Get Leaderboard:**
```bash
GET /api/lecture/advanced/rewards/leaderboard?limit=10
```

**Award Points:**
```bash
POST /api/lecture/advanced/rewards/award-points
  ?user_id=string&points=integer&reason=string
```

#### Reward Mechanics:
- **Base Points**: 10 points per correct answer
- **Time Bonus**: +5 points if answered < 30 seconds
- **Streak Rewards**: 
  - 5 correct: "On Fire" badge (+50 points)
  - 10 correct: "Unstoppable" badge (+100 points)
- **Level System**: Every 100 points = 1 level
- **Badges Available**:
  - First Step: Complete first question
  - On Fire: 5-question streak
  - Unstoppable: 10-question streak
  - Perfect: 100% score on a question set
  - Speed Demon: Answer < 30 seconds
  - Thorough: Comprehensive answer

#### User Stats Response:
```json
{
  "status": "success",
  "data": {
    "user_id": "user_abc123",
    "total_points": 425,
    "level": 4,
    "badges": ["first_question", "streak_5", "speed_answer"],
    "streak": 3,
    "achievements": [],
    "level_progress": {
      "current_level": 4,
      "points_in_level": 25,
      "points_to_next_level": 75,
      "progress_percent": 25.0
    },
    "recent_history": [...],
    "total_answers": 47,
    "accuracy": 78.5
  }
}
```

---

## 📊 Usage Examples

### Example 1: Analyze Lecture Sentiment
```javascript
const advanced = new AdvancedFeaturesManager(apiClient);

const result = await advanced.analyzeSentiment(
  "This neural network concept is absolutely fantastic and changed my perspective!",
  "lecture"
);

console.log(result.data.sentiment_label); // "very_positive"
console.log(result.data.emotions);       // {joy: 0.6, surprise: 0.2, ...}
```

### Example 2: Cultural Translation
```javascript
const result = await advanced.translateWithCulture(
  "Machine learning is a piece of cake when you understand the fundamentals",
  "en", "ta", "academic"
);

console.log(result.data.original_text);    // Original English
console.log(result.data.translated_text);  // Tamil with cultural awareness
console.log(result.data.idioms_detected);  // Breakdown of idioms found
```

### Example 3: Meeting Summarization
```javascript
const result = await advanced.summarizeMeeting(
  lectureTranscript,
  "Q1 Planning Meeting",
  120
);

console.log(result.data.action_items);      // Tasks to complete
console.log(result.data.key_decisions);     // Decisions made
console.log(result.data.risks_identified);  // Risks and mitigations
```

### Example 4: Generate Quiz Questions
```javascript
const questions = await advanced.generateQuestions(
  lectureContent,
  5,
  ["multiple_choice", "short_answer"],
  "understand"
);

questions.data.forEach(q => {
  console.log(q.question);
  console.log(q.points);      // Points for correct answer
  console.log(q.explanation); // Why this is correct
});
```

### Example 5: Track Student Progress
```javascript
// Initialize rewards for student
await advanced.initializeRewards();

// Submit answer
const reward = await advanced.submitAnswer(
  "question_123",
  true,  // is_correct
  45     // time_taken_seconds
);

console.log(reward.data.points_awarded);   // 15 (base 10 + time bonus 5)
console.log(reward.user_stats.total_points);
console.log(reward.user_stats.streak);

// Get leaderboard
const leaderboard = await advanced.getLeaderboard(10);
leaderboard.data.forEach(entry => {
  console.log(`${entry.user_id}: ${entry.points} points (Level ${entry.level})`);
});
```

---

## 🚀 Integration Steps

### Step 1: Update Main HTML
```html
<!-- In frontend/index.html, add before closing </body> -->
<script src="advanced-features.js"></script>
```

### Step 2: Initialize in app.js
```javascript
// In LectureAssistantApp.init()
this.advanced = new AdvancedFeaturesManager(this.api);
await this.advanced.initializeRewards();
```

### Step 3: Use in Event Handlers
```javascript
// Analyze sentiment after transcription
const sentiment = await this.advanced.analyzeSentiment(transcript);
console.log(`Sentiment: ${sentiment.data.sentiment_label}`);

// Generate questions from lecture
const questions = await this.advanced.generateQuestions(transcript);
```

---

## 💡 Best Practices

1. **Sentiment Analysis**: Use to identify difficult topics or gauge student engagement
2. **Cultural Translation**: Always use for multilingual lectures to preserve meaning
3. **Meeting Summarization**: Extract action items after lectures/meetings for follow-up
4. **Context Memory**: Enable for long lecture sessions to ensure term consistency
5. **Question Generation**: Use at different Bloom levels to cater to various learners
6. **Rewards**: Award points consistently to maintain student motivation

---

## 📈 Performance Notes

- Sentiment analysis: ~50ms per text
- Translation: ~100-200ms depending on text length
- Meeting summarization: ~200-500ms for full transcript
- Question generation: ~300-500ms for 5 questions
- All operations are non-blocking and can run in background

---

## 🔐 NOTE: Backend Docker

Don't forget to include the new service files when running Docker:
```bash
docker compose up --build
```

The backend automatically loads all services from the `/services` directory.
