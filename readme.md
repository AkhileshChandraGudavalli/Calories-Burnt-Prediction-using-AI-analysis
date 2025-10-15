🔥 Calorie Burn Predictor & Fitness Tracker
A comprehensive AI-powered fitness tracking application that predicts calorie burn, provides personalized nutrition tips, recommends exercises, and tracks your fitness journey with detailed analytics.

🌟 Features
1. Calorie Burn Prediction
Machine Learning model trained on 1000+ data points
Factors considered:
Gender, Age, Height, Weight
Exercise type (Running, Walking, Cycling, Swimming, Gym)
Heart rate during exercise
Body temperature
Duration
BMI calculation
2. Comprehensive Logbook
Automatic logging of all workout sessions
Persistent storage using JSON
Historical data tracking (7, 14, 30, 60, 90 days views)
3. Visual Analytics Dashboard
Daily calorie burn trends
Exercise type distribution pie charts
Heart rate analysis with box plots
Interactive Plotly visualizations
4. AI-Powered Performance Analysis
Trend detection (increasing/decreasing performance)
Consistency tracking
Heart rate zone analysis
Personalized recommendations
Exercise variety monitoring
5. Personalized Nutrition Tips
BMI-based recommendations
Category-specific advice (Underweight, Normal, Overweight, Obese)
Daily calorie requirements (BMR calculation)
Weight loss/gain guidance
6. Exercise Recommendations
Customized workout suggestions based on BMI
Strength training exercises
Cardio activities
Heart rate training zones
Sample weekly workout plans
7. Monthly Goal Planning
Target BMI setting
Projected weight journey visualization
Month-by-month breakdown
Focus areas for each phase
Timeline calculations
📋 Prerequisites
Python 3.8 or higher
pip (Python package manager)
🚀 Installation
Step 1: Clone or Download Files
Create a new folder and save the following files:

calories_backend.py - Backend logic and ML model
app.py - Streamlit frontend application
requirements.txt - Python dependencies
Step 2: Install Dependencies
bash
pip install -r requirements.txt
Step 3: Initialize the Model
Run the backend file once to train and save the model:

bash
python calories_backend.py
This will create a calorie_model.pkl file.

Step 4: Run the Application
bash
streamlit run app.py
The application will open in your default web browser at http://localhost:8501

📖 How to Use
Initial Setup
Enter Your Profile (Sidebar):
Gender
Age
Height (cm)
Weight (kg)
Your BMI is calculated automatically
Predicting Calories
Go to "🔥 Predict Calories" tab
Select exercise type
Set duration (minutes)
Enter your heart rate during exercise
Input body temperature (typically 37°C at rest, higher during exercise)
Click "Calculate Calories Burned"
Results are automatically saved to your logbook
Viewing Analytics
Go to "📊 Logbook & Analytics" tab
Select time period (7, 14, 30, 60, or 90 days)
View:
Total and average calorie statistics
Daily calorie burn trends
Exercise distribution
Heart rate analysis
AI-powered insights and recommendations
Recent activity log
Getting Nutrition Tips
Go to "🥗 Nutrition Tips" tab
View your BMI gauge
Read personalized nutrition recommendations
Check daily calorie guidelines (BMR, maintenance, weight loss/gain)
Exercise Recommendations
Go to "💪 Exercise Recommendations" tab
Select your fitness level
View recommended:
Strength training exercises
Cardio activities
Heart rate training zones
Weekly workout plan
Setting Monthly Goals
Go to "🎯 Monthly Goals" tab
Set your target BMI
Click "Generate Monthly Plan"
Review:
Timeline to reach your goal
Month-by-month breakdown
Projected weight journey graph
Success factors
📊 Data Storage
All workout data is stored in calorie_log.json in the same directory as the application. This file is automatically created and updated.

Backup Recommendation: Periodically backup your calorie_log.json file to preserve your workout history.

🧠 Machine Learning Model
The application uses a Random Forest Regressor with:

100 estimators
Trained on synthetic data modeling real-world calorie burn patterns
Features: Gender, Age, Height, Weight, Duration, Heart Rate, Body Temperature, BMI, Exercise Type
Model Accuracy Factors
The model considers:

Gender: Males typically burn ~20% more calories
Age: Metabolism decreases with age
Heart Rate: Higher heart rate = more intensity = more calories
Body Temperature: Indicates workout intensity
Weight: Heavier individuals burn more calories
Exercise Type: Different activities have different calorie burn rates
BMI: Affects overall calorie expenditure
💡 Tips for Best Results
Consistency: Log workouts daily
Accuracy: Measure heart rate accurately (use fitness tracker if possible)
Variety: Mix different exercise types
Progressive Overload: Gradually increase intensity
Rest: Include rest days for recovery
Nutrition: Follow the personalized nutrition tips
Hydration: Drink adequate water daily
Sleep: Ensure 7-9 hours of quality sleep
🎯 BMI Categories
Underweight: < 18.5
Normal weight: 18.5 - 24.9
Overweight: 25.0 - 29.9
Obese: ≥ 30.0
⚠️ Disclaimer
This application provides estimates and general guidance. It is NOT a substitute for professional medical advice. Always consult with:

Your doctor before starting new exercise programs
A registered dietitian for personalized nutrition plans
Healthcare professionals if you have any health conditions
🔧 Troubleshooting
Issue: Model not found error

Solution: Run python calories_backend.py first to create the model
Issue: Import errors

Solution: Ensure all packages are installed: pip install -r requirements.txt
Issue: Port already in use

Solution: Run with different port: streamlit run app.py --server.port 8502
Issue: Logbook not saving

Solution: Ensure write permissions in the application directory
📈 Future Enhancements
Potential features for future versions:

Integration with fitness trackers (Fitbit, Apple Watch)
Social features (share progress with friends)
Meal planning and calorie tracking
Water intake tracking
Sleep quality monitoring
Photo progress tracking
Export reports to PDF
Mobile app version
🤝 Contributing
Suggestions and improvements are welcome! Feel free to:

Report bugs
Suggest new features
Improve documentation
Optimize the ML model
📄 License
This project is created for educational and personal use.

🙏 Acknowledgments
Scikit-learn for ML capabilities
Streamlit for the amazing web framework
Plotly for interactive visualizations
Made with ❤️ for fitness enthusiasts!

Start your fitness journey today! 🏃‍♂️💪🔥

