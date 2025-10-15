import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import json
from datetime import datetime, timedelta
import os

class CaloriePredictor:
    def __init__(self):
        self.model = None
        self.gender_encoder = LabelEncoder()
        self.exercise_encoder = LabelEncoder()
        self.train_model()
        
    def train_model(self):
        """Train the calorie prediction model with synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic training data
        data = {
            'gender': np.random.choice(['Male', 'Female'], n_samples),
            'age': np.random.randint(18, 70, n_samples),
            'height': np.random.randint(150, 200, n_samples),
            'weight': np.random.randint(50, 120, n_samples),
            'duration': np.random.randint(10, 120, n_samples),
            'heart_rate': np.random.randint(60, 180, n_samples),
            'body_temp': np.random.uniform(36.5, 38.5, n_samples),
            'exercise_type': np.random.choice(['Running', 'Walking', 'Cycling', 'Swimming', 'Gym'], n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate BMI
        df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
        
        # Generate realistic calorie burn based on factors
        base_calories = df['duration'] * 5
        gender_factor = np.where(df['gender'] == 'Male', 1.2, 1.0)
        age_factor = 1 - (df['age'] - 18) * 0.005
        hr_factor = (df['heart_rate'] - 60) / 100
        temp_factor = (df['body_temp'] - 36.5) * 2
        weight_factor = df['weight'] / 70
        
        exercise_multiplier = df['exercise_type'].map({
            'Running': 1.5, 'Swimming': 1.4, 'Cycling': 1.3, 'Gym': 1.2, 'Walking': 0.8
        })
        
        df['calories'] = (base_calories * gender_factor * age_factor * weight_factor * 
                         exercise_multiplier * (1 + hr_factor + temp_factor) + 
                         np.random.normal(0, 20, n_samples))
        
        # Prepare features
        df['gender_encoded'] = self.gender_encoder.fit_transform(df['gender'])
        df['exercise_encoded'] = self.exercise_encoder.fit_transform(df['exercise_type'])
        
        X = df[['gender_encoded', 'age', 'height', 'weight', 'duration', 
                'heart_rate', 'body_temp', 'bmi', 'exercise_encoded']]
        y = df['calories']
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
    def predict_calories(self, gender, age, height, weight, duration, 
                        heart_rate, body_temp, exercise_type):
        """Predict calories burned"""
        bmi = weight / ((height / 100) ** 2)
        gender_encoded = self.gender_encoder.transform([gender])[0]
        exercise_encoded = self.exercise_encoder.transform([exercise_type])[0]
        
        features = np.array([[gender_encoded, age, height, weight, duration, 
                            heart_rate, body_temp, bmi, exercise_encoded]])
        
        calories = self.model.predict(features)[0]
        return max(0, calories)


class NutritionAdvisor:
    @staticmethod
    def get_bmi_category(bmi):
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    @staticmethod
    def get_nutrition_tips(bmi, goal="maintain"):
        category = NutritionAdvisor.get_bmi_category(bmi)
        
        tips = {
            "Underweight": [
                "Increase calorie intake with nutrient-dense foods",
                "Eat 5-6 smaller meals throughout the day",
                "Include healthy fats: nuts, avocados, olive oil",
                "Add protein shakes between meals",
                "Focus on strength training exercises"
            ],
            "Normal weight": [
                "Maintain balanced diet with all food groups",
                "Eat plenty of fruits and vegetables (5+ servings daily)",
                "Stay hydrated with 8-10 glasses of water",
                "Control portion sizes",
                "Regular exercise 150+ minutes per week"
            ],
            "Overweight": [
                "Create calorie deficit of 500-750 calories/day",
                "Increase protein intake to preserve muscle mass",
                "Reduce refined carbs and sugary drinks",
                "Eat more fiber-rich foods for satiety",
                "Combine cardio and strength training"
            ],
            "Obese": [
                "Consult healthcare provider for personalized plan",
                "Focus on sustainable lifestyle changes",
                "Track daily food intake and calories",
                "Start with low-impact exercises like walking/swimming",
                "Consider working with a registered dietitian"
            ]
        }
        
        return tips.get(category, tips["Normal weight"])
    
    @staticmethod
    def get_recommended_exercises(bmi, fitness_level="intermediate"):
        category = NutritionAdvisor.get_bmi_category(bmi)
        
        exercises = {
            "Underweight": {
                "strength": ["Weight lifting", "Resistance bands", "Bodyweight exercises"],
                "cardio": ["Light jogging", "Swimming", "Cycling"],
                "duration": "30-45 min, 3-4x/week"
            },
            "Normal weight": {
                "strength": ["Full-body workouts", "HIIT", "Functional training"],
                "cardio": ["Running", "Cycling", "Swimming", "Dancing"],
                "duration": "45-60 min, 4-5x/week"
            },
            "Overweight": {
                "strength": ["Circuit training", "Bodyweight exercises", "Light weights"],
                "cardio": ["Brisk walking", "Elliptical", "Water aerobics", "Cycling"],
                "duration": "40-60 min, 5-6x/week"
            },
            "Obese": {
                "strength": ["Seated exercises", "Wall push-ups", "Chair squats"],
                "cardio": ["Walking", "Swimming", "Water aerobics", "Stationary bike"],
                "duration": "20-30 min initially, gradually increase"
            }
        }
        
        return exercises.get(category, exercises["Normal weight"])
    
    @staticmethod
    def get_monthly_suggestions(current_bmi, target_bmi, weight, height):
        """Generate monthly improvement plan"""
        bmi_diff = current_bmi - target_bmi
        height_m = height / 100
        weight_to_lose = bmi_diff * (height_m ** 2)
        
        # Healthy weight loss: 0.5-1 kg per week (2-4 kg per month)
        months_needed = max(1, int(abs(weight_to_lose) / 3))
        
        suggestions = {
            "current_status": {
                "bmi": round(current_bmi, 2),
                "category": NutritionAdvisor.get_bmi_category(current_bmi),
                "weight": weight
            },
            "target": {
                "bmi": round(target_bmi, 2),
                "weight": round(weight - weight_to_lose, 1),
                "timeline": f"{months_needed} months"
            },
            "monthly_plan": []
        }
        
        for month in range(1, min(months_needed + 1, 7)):
            monthly_weight_loss = weight_to_lose / months_needed
            calorie_deficit = 500 if weight_to_lose > 0 else -500
            
            plan = {
                "month": month,
                "target_weight": round(weight - (monthly_weight_loss * month), 1),
                "daily_calorie_adjustment": calorie_deficit,
                "exercise_goal": f"{150 + (month * 30)} minutes/week",
                "focus_areas": []
            }
            
            if month <= 2:
                plan["focus_areas"] = ["Build sustainable habits", "Start food tracking", "Increase water intake"]
            elif month <= 4:
                plan["focus_areas"] = ["Increase exercise intensity", "Add strength training", "Meal prep weekly"]
            else:
                plan["focus_areas"] = ["Maintain consistency", "Add variety to workouts", "Focus on maintenance"]
            
            suggestions["monthly_plan"].append(plan)
        
        return suggestions


class LogBook:
    def __init__(self, filename="calorie_log.json"):
        self.filename = filename
        self.load_logs()
    
    def load_logs(self):
        """Load existing logs from file"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.logs = json.load(f)
        else:
            self.logs = []
    
    def save_logs(self):
        """Save logs to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def add_entry(self, entry):
        """Add new log entry"""
        entry['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry['date'] = datetime.now().strftime("%Y-%m-%d")
        self.logs.append(entry)
        self.save_logs()
    
    def get_logs(self, days=30):
        """Get logs for specified number of days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return [log for log in self.logs if log.get('date', '') >= cutoff_date]
    
    def get_stats(self, days=30):
        """Calculate statistics from logs"""
        logs = self.get_logs(days)
        if not logs:
            return None
        
        df = pd.DataFrame(logs)
        
        stats = {
            "total_calories": df['calories_burned'].sum(),
            "avg_calories": df['calories_burned'].mean(),
            "total_sessions": len(df),
            "avg_heart_rate": df['heart_rate'].mean(),
            "total_duration": df['duration'].sum(),
            "most_common_exercise": df['exercise_type'].mode()[0] if len(df) > 0 else "N/A"
        }
        
        return stats
    
    def get_daily_aggregates(self, days=30):
        """Get daily aggregated data for charts"""
        logs = self.get_logs(days)
        if not logs:
            return pd.DataFrame()
        
        df = pd.DataFrame(logs)
        daily = df.groupby('date').agg({
            'calories_burned': 'sum',
            'duration': 'sum',
            'heart_rate': 'mean'
        }).reset_index()
        
        return daily


class AIAnalyzer:
    @staticmethod
    def analyze_performance(logs_df, user_profile):
        """Provide AI-driven insights on performance"""
        if logs_df.empty or len(logs_df) < 3:
            return {
                "insights": ["Not enough data yet. Keep logging your workouts!"],
                "recommendations": ["Log at least 3 workouts to get personalized insights"],
                "trends": []
            }
        
        insights = []
        recommendations = []
        trends = []
        
        # Analyze calorie burn trend
        if len(logs_df) >= 7:
            recent_avg = logs_df.tail(7)['calories_burned'].mean()
            older_avg = logs_df.head(7)['calories_burned'].mean()
            
            if recent_avg > older_avg * 1.1:
                trends.append("📈 Increasing calorie burn - Great progress!")
                insights.append(f"Your calorie burn has increased by {((recent_avg/older_avg - 1) * 100):.1f}% over time")
            elif recent_avg < older_avg * 0.9:
                trends.append("📉 Decreasing calorie burn - May need intensity boost")
                recommendations.append("Consider increasing workout intensity or duration")
        
        # Analyze consistency
        total_days = (pd.to_datetime(logs_df['date'].max()) - pd.to_datetime(logs_df['date'].min())).days
        workout_days = logs_df['date'].nunique()
        consistency = (workout_days / max(total_days, 1)) * 100
        
        if consistency > 70:
            insights.append(f"Excellent consistency! You're working out {consistency:.0f}% of days")
        elif consistency > 50:
            insights.append(f"Good consistency at {consistency:.0f}%. Try to maintain this!")
        else:
            insights.append(f"Consistency is {consistency:.0f}%. Aim for at least 3-4 workouts/week")
            recommendations.append("Set specific workout days and times to improve consistency")
        
        # Heart rate analysis
        avg_hr = logs_df['heart_rate'].mean()
        age = user_profile.get('age', 30)
        max_hr = 220 - age
        hr_percentage = (avg_hr / max_hr) * 100
        
        if hr_percentage < 50:
            recommendations.append("Your heart rate suggests low-intensity workouts. Consider increasing intensity")
        elif hr_percentage > 85:
            recommendations.append("High heart rate detected. Ensure adequate rest and recovery")
        else:
            insights.append(f"Your average heart rate ({avg_hr:.0f} bpm) is in a good training zone")
        
        # Exercise variety
        exercise_variety = logs_df['exercise_type'].nunique()
        if exercise_variety < 2:
            recommendations.append("Add variety to your workouts for better overall fitness")
        else:
            insights.append(f"Good exercise variety with {exercise_variety} different activities")
        
        # BMI-based recommendations
        bmi = user_profile.get('bmi', 22)
        if bmi > 25:
            recommendations.append("Focus on calorie deficit and combine cardio with strength training")
        elif bmi < 18.5:
            recommendations.append("Ensure adequate calorie intake and focus on strength training")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "trends": trends
        }


# Save models
def save_models():
    predictor = CaloriePredictor()
    with open('calorie_model.pkl', 'wb') as f:
        pickle.dump(predictor, f)
    print("Model saved successfully!")


if __name__ == "__main__":
    save_models()
    print("Backend initialized successfully!")