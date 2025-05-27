# data/datasets/generate_sample_data.py
"""
Generate sample training data for the mental health assessment model.
This creates realistic but synthetic data for initial model training.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
import os

class SampleDataGenerator:
    def __init__(self):
        # Define assessment questions and their types
        self.assessment_questions = {
            'q1_mood': 'How would you rate your overall mood in the past week?',
            'q2_anxiety': 'How often have you felt anxious or worried?',
            'q3_sleep': 'How has your sleep quality been?',
            'q4_energy': 'How would you describe your energy levels?',
            'q5_concentration': 'How well have you been able to concentrate?',
            'q6_social': 'How comfortable do you feel in social situations?',
            'q7_appetite': 'How has your appetite been?',
            'q8_hopelessness': 'How often do you feel hopeless about the future?',
            'q9_worthlessness': 'How often do you feel worthless or inadequate?',
            'q10_stress': 'How would you rate your stress levels?'
        }
        
        # Define response patterns for different mental health states
        self.response_patterns = {
            'healthy': {
                'mood_range': (7, 10),
                'anxiety_range': (1, 3),
                'sleep_range': (7, 10),
                'energy_range': (7, 10),
                'concentration_range': (7, 10),
                'social_range': (7, 10),
                'appetite_range': (7, 10),
                'hopelessness_range': (1, 2),
                'worthlessness_range': (1, 2),
                'stress_range': (1, 4)
            },
            'mild_symptoms': {
                'mood_range': (4, 7),
                'anxiety_range': (3, 6),
                'sleep_range': (4, 7),
                'energy_range': (4, 7),
                'concentration_range': (4, 7),
                'social_range': (4, 7),
                'appetite_range': (4, 8),
                'hopelessness_range': (2, 5),
                'worthlessness_range': (2, 5),
                'stress_range': (4, 7)
            },
            'moderate_symptoms': {
                'mood_range': (2, 5),
                'anxiety_range': (5, 8),
                'sleep_range': (2, 5),
                'energy_range': (2, 5),
                'concentration_range': (2, 5),
                'social_range': (2, 5),
                'appetite_range': (2, 8),
                'hopelessness_range': (4, 7),
                'worthlessness_range': (4, 7),
                'stress_range': (6, 9)
            },
            'severe_symptoms': {
                'mood_range': (1, 3),
                'anxiety_range': (7, 10),
                'sleep_range': (1, 3),
                'energy_range': (1, 3),
                'concentration_range': (1, 3),
                'social_range': (1, 3),
                'appetite_range': (1, 6),
                'hopelessness_range': (6, 10),
                'worthlessness_range': (6, 10),
                'stress_range': (8, 10)
            }
        }
        
        # Text responses for qualitative questions
        self.text_responses = {
            'healthy': [
                "I feel pretty good overall",
                "Things are going well for me",
                "I'm generally positive about life",
                "I feel balanced and content",
                "Life feels manageable right now"
            ],
            'mild_symptoms': [
                "I have some ups and downs",
                "Sometimes I feel a bit overwhelmed",
                "I'm managing but it's not always easy",
                "I feel okay most days",
                "Some days are harder than others"
            ],
            'moderate_symptoms': [
                "I'm struggling quite a bit lately",
                "It's been really hard to cope",
                "I feel overwhelmed most of the time",
                "Everything feels like a big effort",
                "I don't feel like myself anymore"
            ],
            'severe_symptoms': [
                "I can barely get through each day",
                "Everything feels hopeless",
                "I don't see the point in anything",
                "I feel completely overwhelmed",
                "I can't handle this anymore"
            ]
        }

    def generate_assessment_response(self, mental_state):
        """Generate a single assessment response based on mental state"""
        pattern = self.response_patterns[mental_state]
        response = {}
        
        # Generate numeric responses (1-10 scale)
        response['q1_mood'] = random.randint(*pattern['mood_range'])
        response['q2_anxiety'] = random.randint(*pattern['anxiety_range'])
        response['q3_sleep'] = random.randint(*pattern['sleep_range'])
        response['q4_energy'] = random.randint(*pattern['energy_range'])
        response['q5_concentration'] = random.randint(*pattern['concentration_range'])
        response['q6_social'] = random.randint(*pattern['social_range'])
        response['q7_appetite'] = random.randint(*pattern['appetite_range'])
        response['q8_hopelessness'] = random.randint(*pattern['hopelessness_range'])
        response['q9_worthlessness'] = random.randint(*pattern['worthlessness_range'])
        response['q10_stress'] = random.randint(*pattern['stress_range'])
        
        # Add a text response
        response['additional_comments'] = random.choice(self.text_responses[mental_state])
        
        return response

    def calculate_labels(self, responses, mental_state):
        """Calculate target labels based on responses and mental state"""
        # Calculate anxiety level (0-1 scale)
        anxiety_level = (responses['q2_anxiety'] + (10 - responses['q6_social']) + responses['q10_stress']) / 30
        
        # Calculate depression level (0-1 scale)
        depression_level = ((10 - responses['q1_mood']) + responses['q8_hopelessness'] + 
                           responses['q9_worthlessness'] + (10 - responses['q4_energy'])) / 40
        
        # Calculate stress level (0-1 scale)
        stress_level = (responses['q10_stress'] + (10 - responses['q5_concentration']) + 
                       (10 - responses['q3_sleep'])) / 30
        
        # Calculate wellbeing score (0-1 scale, higher is better)
        wellbeing_score = (responses['q1_mood'] + responses['q3_sleep'] + responses['q4_energy'] + 
                          responses['q5_concentration'] + responses['q6_social'] + 
                          (10 - responses['q8_hopelessness'])) / 60
        
        # Calculate risk level (0-1 scale)
        risk_indicators = [responses['q8_hopelessness'], responses['q9_worthlessness']]
        risk_level = sum(risk_indicators) / 20
        
        # Apply some noise and ensure realistic ranges
        anxiety_level = max(0, min(1, anxiety_level + random.uniform(-0.1, 0.1)))
        depression_level = max(0, min(1, depression_level + random.uniform(-0.1, 0.1)))
        stress_level = max(0, min(1, stress_level + random.uniform(-0.1, 0.1)))
        wellbeing_score = max(0, min(1, wellbeing_score + random.uniform(-0.1, 0.1)))
        risk_level = max(0, min(1, risk_level + random.uniform(-0.05, 0.05)))
        
        return {
            'anxiety_level': round(anxiety_level, 3),
            'depression_level': round(depression_level, 3),
            'stress_level': round(stress_level, 3),
            'wellbeing_score': round(wellbeing_score, 3),
            'risk_level': round(risk_level, 3),
            'mental_state_category': mental_state
        }

    def generate_dataset(self, n_samples=1000):
        """Generate a complete dataset"""
        data = []
        
        # Define distribution of mental states
        state_distribution = {
            'healthy': 0.4,
            'mild_symptoms': 0.3,
            'moderate_symptoms': 0.2,
            'severe_symptoms': 0.1
        }
        
        print(f"Generating {n_samples} sample assessments...")
        
        for i in range(n_samples):
            # Select mental state based on distribution
            rand = random.random()
            cumulative = 0
            selected_state = 'healthy'
            
            for state, prob in state_distribution.items():
                cumulative += prob
                if rand <= cumulative:
                    selected_state = state
                    break
            
            # Generate response
            responses = self.generate_assessment_response(selected_state)
            labels = self.calculate_labels(responses, selected_state)
            
            # Create data point
            data_point = {
                'user_id': f'user_{i+1:04d}',
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
                'responses': responses,
                'labels': labels
            }
            
            data.append(data_point)
            
            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{n_samples} samples...")
        
        return data

    def save_dataset(self, data, output_dir='data/sample'):
        """Save the generated dataset in multiple formats"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as JSON (complete format)
        json_path = os.path.join(output_dir, 'assessment_data.json')
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved JSON data to {json_path}")
        
        # Convert to CSV format for easy ML training
        csv_data = []
        for item in data:
            row = {
                'user_id': item['user_id'],
                'timestamp': item['timestamp']
            }
            
            # Add response columns
            for q_id, response in item['responses'].items():
                row[f'response_{q_id}'] = response
            
            # Add label columns
            for label, value in item['labels'].items():
                row[label] = value
            
            csv_data.append(row)
        
        # Save as CSV
        df = pd.DataFrame(csv_data)
        csv_path = os.path.join(output_dir, 'assessment_data.csv')
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved CSV data to {csv_path}")
        
        # Create summary statistics
        self.create_data_summary(df, output_dir)
        
        return json_path, csv_path

    def create_data_summary(self, df, output_dir):
        """Create summary statistics of the generated data"""
        summary = {}
        
        # Basic statistics
        summary['total_samples'] = len(df)
        summary['mental_state_distribution'] = df['mental_state_category'].value_counts().to_dict()
        
        # Label statistics
        label_cols = ['anxiety_level', 'depression_level', 'stress_level', 'wellbeing_score', 'risk_level']
        summary['label_statistics'] = {}
        
        for col in label_cols:
            summary['label_statistics'][col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max())
            }
        
        # Response statistics
        response_cols = [col for col in df.columns if col.startswith('response_q')]
        summary['response_statistics'] = {}
        
        for col in response_cols:
            if df[col].dtype in ['int64', 'float64']:
                summary['response_statistics'][col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }
        
        # Save summary
        summary_path = os.path.join(output_dir, 'data_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Saved data summary to {summary_path}")
        
        # Print summary to console
        print("\n📊 Dataset Summary:")
        print(f"Total samples: {summary['total_samples']}")
        print("\nMental state distribution:")
        for state, count in summary['mental_state_distribution'].items():
            print(f"  {state}: {count} ({count/summary['total_samples']*100:.1f}%)")

def main():
    """Main function to generate sample data"""
    print("🎯 Generating Sample Assessment Data")
    print("=" * 40)
    
    generator = SampleDataGenerator()
    
    # Generate training dataset
    print("\n1. Generating training dataset...")
    train_data = generator.generate_dataset(n_samples=800)
    train_json, train_csv = generator.save_dataset(train_data, 'data/sample/train')
    
    # Generate test dataset
    print("\n2. Generating test dataset...")
    test_data = generator.generate_dataset(n_samples=200)
    test_json, test_csv = generator.save_dataset(test_data, 'data/sample/test')
    
    print("\n🎉 Sample data generation complete!")
    print("\nGenerated files:")
    print(f"  Training: {train_csv}")
    print(f"  Test: {test_csv}")
    print("\nNext step: Train the assessment model using this data")

if __name__ == "__main__":
    main()