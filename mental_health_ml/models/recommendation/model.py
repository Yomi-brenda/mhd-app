import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResourceRecommender:
    def __init__(self):
        self.resources = []
        self.content_vectors = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def load_resources(self, resources_data):
        """Load resources with metadata"""
        self.resources = resources_data
        
        # Extract content features for content-based filtering
        content_texts = [f"{r['title']} {r['description']} {' '.join(r['tags'])}" 
                        for r in resources_data]
        self.content_vectors = self.vectorizer.fit_transform(content_texts)
    
    def get_similar_resources(self, resource_id, n=5):
        """Get similar resources based on content"""
        resource_idx = next((i for i, r in enumerate(self.resources) if r['id'] == resource_id), None)
        if resource_idx is None:
            return []
            
        # Calculate similarity with all resources
        resource_vector = self.content_vectors[resource_idx]
        similarities = cosine_similarity(resource_vector, self.content_vectors).flatten()
        
        # Get top similar resources (excluding the resource itself)
        similar_indices = np.argsort(similarities)[::-1][1:n+1]
        return [self.resources[i] for i in similar_indices]
    
    def recommend_for_user(self, user_profile, user_history=None, n=5):
        """Recommend resources based on user profile and history"""
        # Extract user attributes for matching
        user_needs = user_profile.get('needs', [])
        user_interests = user_profile.get('interests', [])
        user_mental_state = user_profile.get('mental_state', {})
        
        # Create user query
        user_query = ' '.join(user_needs + user_interests)
        if user_mental_state:
            # Add mental state indicators if available
            for state, level in user_mental_state.items():
                if level > 0.5:  # Only include significant states
                    user_query += f" {state}"
        
        # If no user information, return generic popular resources
        if not user_query:
            # Sort by popularity and return top n
            popular_resources = sorted(self.resources, key=lambda x: x.get('popularity', 0), reverse=True)
            return popular_resources[:n]
        
        # Vectorize user query
        user_vector = self.vectorizer.transform([user_query])
        
        # Calculate similarity with all resources
        similarities = cosine_similarity(user_vector, self.content_vectors).flatten()
        
        # Get recommendation indices
        recommended_indices = np.argsort(similarities)[::-1][:n]
        
        # Filter out resources user has already seen
        if user_history:
            seen_ids = set(user_history)
            recommended_resources = []
            i = 0
            while len(recommended_resources) < n and i < len(recommended_indices):
                res = self.resources[recommended_indices[i]]
                if res['id'] not in seen_ids:
                    recommended_resources.append(res)
                i += 1
            return recommended_resources
        
        return [self.resources[i] for i in recommended_indices]
    
    def recommend_for_assessment(self, assessment_results, n=5):
        """Recommend resources based on assessment results (updated thresholds)"""
        query_terms = []

        anxiety_score = assessment_results.get('anxiety_score', 0)
        depression_score = assessment_results.get('depression_score', 0)
        wellbeing_score = assessment_results.get('wellbeing_score', 0)

        # Anxiety scoring
        if 8 <= anxiety_score <= 15:
            query_terms.extend(['mild anxiety', 'relaxation'])
        elif 16 <= anxiety_score <= 25:
            query_terms.extend(['moderate anxiety', 'stress relief', 'coping techniques'])
        elif anxiety_score >= 26:
            query_terms.extend(['severe anxiety', 'panic', 'immediate support'])

        # Depression scoring
        if 14 <= depression_score <= 19:
            query_terms.extend(['mild depression', 'self-help', 'low mood'])
        elif 20 <= depression_score <= 28:
            query_terms.extend(['moderate depression', 'therapy', 'support group'])
        elif depression_score >= 29:
            query_terms.extend(['severe depression', 'crisis support', 'professional help'])

        # Well-being scoring (WEMWBS)
        if 41 <= wellbeing_score <= 50:
            query_terms.extend(['low wellbeing', 'self-care', 'mindfulness'])
        elif 51 <= wellbeing_score <= 59:
            query_terms.extend(['moderate wellbeing', 'personal growth', 'resilience'])
        elif wellbeing_score >= 60:
            query_terms.extend(['positive wellbeing', 'optimism', 'mental fitness'])

        # Default terms if none detected
        if not query_terms:
            query_terms = ['mental health', 'wellness', 'self-improvement']

        # Create TF-IDF vector from query
        assessment_query = ' '.join(query_terms)
        query_vector = self.vectorizer.transform([assessment_query])

        # Calculate similarity and get top recommendations
        similarities = cosine_similarity(query_vector, self.content_vectors).flatten()
        recommended_indices = np.argsort(similarities)[::-1][:n]

        return [self.resources[i] for i in recommended_indices]
