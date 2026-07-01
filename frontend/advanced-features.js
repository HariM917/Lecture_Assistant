// Advanced Features Module
// Sentiment Analysis, Cultural Translation, Meeting Summarization, Questions & Rewards

class AdvancedFeaturesManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.userId = `user_${Math.random().toString(36).substr(2, 9)}`;
        this.userStats = null;
    }

    async analyzeSentiment(text, context = "lecture") {
        try {
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/sentiment/analyze?text=${encodeURIComponent(text)}&context=${context}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Sentiment analysis error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async analyzeSentenceLevel(text) {
        try {
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/sentiment/analyze-sentences?text=${encodeURIComponent(text)}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Sentence sentiment error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async translateWithCulture(text, sourceLang, targetLang, context = "general") {
        try {
            const params = new URLSearchParams({
                text,
                source_lang: sourceLang,
                target_lang: targetLang,
                context
            });
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/translate/cultural?${params}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Cultural translation error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async translateContextAware(text, sourceLang, targetLang, contextType = "general") {
        try {
            const params = new URLSearchParams({
                text,
                source_lang: sourceLang,
                target_lang: targetLang,
                context_type: contextType
            });
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/translate/context-aware?${params}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Context-aware translation error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async summarizeMeeting(transcript, title = "Meeting", duration = 0) {
        try {
            const params = new URLSearchParams({
                transcript,
                title,
                duration
            });
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/meeting/summarize?${params}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Meeting summarization error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async generateQuestions(content, numQuestions = 5, questionTypes = ["multiple_choice"], bloomLevel = "understand") {
        try {
            const params = new URLSearchParams({
                content,
                num_questions: numQuestions,
                bloom_level: bloomLevel
            });
            questionTypes.forEach(qt => params.append('question_types', qt));
            
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/questions/generate?${params}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Question generation error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async initializeRewards() {
        try {
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/rewards/init?user_id=${this.userId}`,
                { method: 'POST' }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Rewards init error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async submitAnswer(questionId, isCorrect, timeTaken = 0) {
        try {
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/rewards/submit-answer?user_id=${this.userId}&question_id=${questionId}&is_correct=${isCorrect}&time_taken=${timeTaken}`,
                { method: 'POST' }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const result = await response.json();
            if (result.user_stats) this.userStats = result.user_stats;
            return result;
        } catch (error) {
            console.error('Answer submission error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async getUserStats() {
        try {
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/rewards/stats/${this.userId}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const result = await response.json();
            if (result.data) this.userStats = result.data;
            return result;
        } catch (error) {
            console.error('User stats error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async getLeaderboard(limit = 10) {
        try {
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/rewards/leaderboard?limit=${limit}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Leaderboard error:', error);
            return { status: 'error', error: error.message };
        }
    }

    async awardPoints(points, reason) {
        try {
            const response = await fetch(
                `${this.api.baseUrl}/api/lecture/advanced/rewards/award-points?user_id=${this.userId}&points=${points}&reason=${encodeURIComponent(reason)}`,
                { method: 'POST' }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const result = await response.json();
            if (result.user_stats) this.userStats = result.user_stats;
            return result;
        } catch (error) {
            console.error('Award points error:', error);
            return { status: 'error', error: error.message };
        }
    }
}

window.AdvancedFeaturesManager = AdvancedFeaturesManager;
