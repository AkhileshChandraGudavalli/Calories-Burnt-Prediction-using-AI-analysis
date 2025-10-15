import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pickle
import os
from backend import CaloriePredictor, NutritionAdvisor, LogBook, AIAnalyzer

# Page configuration
st.set_page_config(
    page_title="Calorie Burn Predictor & Fitness Tracker",
    page_icon="🔥",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

# Load model
@st.cache_resource
def load_model():
    if os.path.exists('calorie_model.pkl'):
        with open('calorie_model.pkl', 'rb') as f:
            return pickle.load(f)
    else:
        return CaloriePredictor()

predictor = load_model()
logbook = LogBook()
advisor = NutritionAdvisor()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔥 Calorie Burn Predictor & Fitness Tracker 🔥</div>', unsafe_allow_html=True)

# Sidebar - User Profile
with st.sidebar:
    st.header("👤 User Profile")
    
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age (years)", min_value=10, max_value=100, value=30)
    height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
    
    # Calculate BMI
    bmi = weight / ((height / 100) ** 2)
    bmi_category = advisor.get_bmi_category(bmi)
    
    st.metric("Current BMI", f"{bmi:.1f}", bmi_category)
    
    # Store profile
    st.session_state.user_profile = {
        'gender': gender,
        'age': age,
        'height': height,
        'weight': weight,
        'bmi': bmi
    }
    
    st.divider()
    st.caption("💡 Keep your profile updated for accurate predictions!")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 Predict Calories", 
    "📊 Logbook & Analytics", 
    "🥗 Nutrition Tips", 
    "💪 Exercise Recommendations",
    "🎯 Monthly Goals"
])

# Tab 1: Predict Calories
with tab1:
    st.header("Calorie Burn Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        exercise_type = st.selectbox(
            "Exercise Type",
            ["Running", "Walking", "Cycling", "Swimming", "Gym"]
        )
        duration = st.slider("Duration (minutes)", 5, 180, 30)
        heart_rate = st.slider("Heart Rate (bpm)", 60, 200, 120)
    
    with col2:
        body_temp = st.number_input(
            "Body Temperature (°C)", 
            min_value=35.0, 
            max_value=42.0, 
            value=37.0,
            step=0.1
        )
        
        st.info(f"""
        **Your Stats:**
        - Gender: {gender}
        - Age: {age} years
        - BMI: {bmi:.1f} ({bmi_category})
        """)
    
    if st.button("🔥 Calculate Calories Burned", type="primary", use_container_width=True):
        calories = predictor.predict_calories(
            gender, age, height, weight, duration,
            heart_rate, body_temp, exercise_type
        )
        
        st.success(f"### 🎉 Estimated Calories Burned: **{calories:.0f} kcal**")
        
        # Save to logbook
        log_entry = {
            'calories_burned': calories,
            'exercise_type': exercise_type,
            'duration': duration,
            'heart_rate': heart_rate,
            'body_temp': body_temp,
            'weight': weight,
            'bmi': bmi
        }
        logbook.add_entry(log_entry)
        st.balloons()
        
        # Show comparison
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Calories", f"{calories:.0f} kcal")
        with col2:
            st.metric("Duration", f"{duration} min")
        with col3:
            st.metric("Cal/min", f"{calories/duration:.1f}")

# Tab 2: Logbook & Analytics
with tab2:
    st.header("📊 Your Fitness Journey")
    
    days_filter = st.selectbox("Time Period", [7, 14, 30, 60, 90], index=2)
    
    logs_df = pd.DataFrame(logbook.get_logs(days_filter))
    
    if not logs_df.empty:
        # Statistics
        stats = logbook.get_stats(days_filter)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Calories", f"{stats['total_calories']:.0f} kcal")
        with col2:
            st.metric("Avg Calories/Session", f"{stats['avg_calories']:.0f} kcal")
        with col3:
            st.metric("Total Sessions", stats['total_sessions'])
        with col4:
            st.metric("Total Duration", f"{stats['total_duration']:.0f} min")
        
        st.divider()
        
        # Charts
        daily_data = logbook.get_daily_aggregates(days_filter)
        
        # Calories burned over time
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=daily_data['date'],
            y=daily_data['calories_burned'],
            mode='lines+markers',
            name='Calories Burned',
            line=dict(color='#FF4B4B', width=3),
            fill='tozeroy'
        ))
        fig1.update_layout(
            title="Daily Calorie Burn Trend",
            xaxis_title="Date",
            yaxis_title="Calories (kcal)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exercise type distribution
            exercise_counts = logs_df['exercise_type'].value_counts()
            fig2 = px.pie(
                values=exercise_counts.values,
                names=exercise_counts.index,
                title="Exercise Type Distribution",
                hole=0.4
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # Heart rate over time
            fig3 = go.Figure()
            fig3.add_trace(go.Box(
                y=logs_df['heart_rate'],
                name='Heart Rate',
                marker_color='#764ba2'
            ))
            fig3.update_layout(
                title="Heart Rate Distribution",
                yaxis_title="BPM",
                height=400
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        st.divider()
        
        # AI Analysis
        st.subheader("🤖 AI Performance Analysis")
        analysis = AIAnalyzer.analyze_performance(logs_df, st.session_state.user_profile)
        
        if analysis['trends']:
            st.markdown("**📈 Trends:**")
            for trend in analysis['trends']:
                st.info(trend)
        
        if analysis['insights']:
            st.markdown("**💡 Insights:**")
            for insight in analysis['insights']:
                st.success(insight)
        
        if analysis['recommendations']:
            st.markdown("**🎯 Recommendations:**")
            for rec in analysis['recommendations']:
                st.warning(rec)
        
        st.divider()
        
        # Recent logs table
        st.subheader("Recent Activity Log")
        display_df = logs_df[['timestamp', 'exercise_type', 'duration', 'calories_burned', 'heart_rate']].tail(10)
        display_df.columns = ['Time', 'Exercise', 'Duration (min)', 'Calories', 'Heart Rate']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.info("📝 No logs yet! Start by predicting your calorie burn in the first tab.")

# Tab 3: Nutrition Tips
with tab3:
    st.header("🥗 Personalized Nutrition Tips")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Your BMI: {bmi:.1f} - {bmi_category}")
        
        # BMI gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi,
            title={'text': "BMI"},
            gauge={
                'axis': {'range': [15, 40]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [15, 18.5], 'color': "lightblue"},
                    {'range': [18.5, 25], 'color': "lightgreen"},
                    {'range': [25, 30], 'color': "yellow"},
                    {'range': [30, 40], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': bmi
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Current Weight", f"{weight} kg")
        st.metric("Height", f"{height} cm")
        
        # Ideal weight range
        ideal_min = 18.5 * ((height/100) ** 2)
        ideal_max = 24.9 * ((height/100) ** 2)
        st.metric("Ideal Weight Range", f"{ideal_min:.1f} - {ideal_max:.1f} kg")
    
    st.divider()
    
    # Nutrition tips
    st.subheader("📋 Nutrition Recommendations")
    tips = advisor.get_nutrition_tips(bmi)
    
    for i, tip in enumerate(tips, 1):
        st.markdown(f"**{i}.** {tip}")
    
    st.divider()
    
    # Calorie recommendations
    st.subheader("🔢 Daily Calorie Guidelines")
    
    # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor equation
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BMR (Base)", f"{bmr:.0f} kcal/day")
    with col2:
        st.metric("Maintain Weight", f"{bmr * 1.55:.0f} kcal/day")
    with col3:
        if bmi > 25:
            st.metric("Weight Loss Goal", f"{bmr * 1.55 - 500:.0f} kcal/day")
        else:
            st.metric("Weight Gain Goal", f"{bmr * 1.55 + 500:.0f} kcal/day")

# Tab 4: Exercise Recommendations
with tab4:
    st.header("💪 Recommended Exercises")
    
    fitness_level = st.select_slider(
        "Select Your Fitness Level",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate"
    )
    
    exercises = advisor.get_recommended_exercises(bmi, fitness_level.lower())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏋️ Strength Training")
        for exercise in exercises['strength']:
            st.markdown(f"- {exercise}")
    
    with col2:
        st.subheader("🏃 Cardio Exercises")
        for exercise in exercises['cardio']:
            st.markdown(f"- {exercise}")
    
    st.info(f"**⏱️ Recommended Duration:** {exercises['duration']}")
    
    st.divider()
    
    # Exercise intensity zones based on heart rate
    st.subheader("❤️ Heart Rate Training Zones")
    
    max_hr = 220 - age
    
    zones = {
        "Warm-up": (0.5, 0.6),
        "Fat Burn": (0.6, 0.7),
        "Cardio": (0.7, 0.8),
        "Peak": (0.8, 0.9),
        "Max": (0.9, 1.0)
    }
    
    for zone_name, (low, high) in zones.items():
        low_hr = int(max_hr * low)
        high_hr = int(max_hr * high)
        st.markdown(f"**{zone_name} Zone:** {low_hr} - {high_hr} bpm")
    
    st.divider()
    
    # Weekly workout plan suggestion
    st.subheader("📅 Sample Weekly Workout Plan")
    
    plan = {
        "Monday": "Strength Training (Upper Body) - 45 min",
        "Tuesday": "Cardio (Running/Cycling) - 30 min",
        "Wednesday": "Strength Training (Lower Body) - 45 min",
        "Thursday": "Active Recovery (Yoga/Walking) - 30 min",
        "Friday": "HIIT/Circuit Training - 30 min",
        "Saturday": "Cardio (Swimming/Sports) - 45 min",
        "Sunday": "Rest or Light Stretching - 20 min"
    }
    
    for day, activity in plan.items():
        st.markdown(f"**{day}:** {activity}")

# Tab 5: Monthly Goals
with tab5:
    st.header("🎯 Monthly BMI Improvement Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Status")
        st.metric("Current BMI", f"{bmi:.1f}")
        st.metric("Category", bmi_category)
        st.metric("Current Weight", f"{weight} kg")
    
    with col2:
        st.subheader("Set Your Target")
        target_bmi = st.number_input(
            "Target BMI",
            min_value=18.5,
            max_value=24.9,
            value=min(24.9, max(18.5, bmi if 18.5 <= bmi <= 24.9 else 22.0)),
            step=0.1
        )
        
        target_weight = target_bmi * ((height / 100) ** 2)
        st.metric("Target Weight", f"{target_weight:.1f} kg")
        
        weight_diff = weight - target_weight
        st.metric("Weight to Adjust", f"{abs(weight_diff):.1f} kg", 
                 delta=f"{-weight_diff:.1f} kg" if weight_diff > 0 else f"+{abs(weight_diff):.1f} kg")
    
    if st.button("🎯 Generate Monthly Plan", type="primary", use_container_width=True):
        suggestions = advisor.get_monthly_suggestions(bmi, target_bmi, weight, height)
        
        st.success(f"**Timeline to Goal:** {suggestions['target']['timeline']}")
        
        st.divider()
        st.subheader("📋 Your Personalized Monthly Plan")
        
        for month_plan in suggestions['monthly_plan']:
            with st.expander(f"📅 Month {month_plan['month']} - Target: {month_plan['target_weight']} kg", expanded=(month_plan['month']==1)):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🎯 Target Weight:** {month_plan['target_weight']} kg")
                    st.markdown(f"**🍽️ Daily Calorie Adjustment:** {month_plan['daily_calorie_adjustment']:+d} kcal")
                
                with col2:
                    st.markdown(f"**💪 Exercise Goal:** {month_plan['exercise_goal']}")
                    st.markdown(f"**📊 Progress Check:** Week 4")
                
                st.markdown("**🎯 Focus Areas:**")
                for focus in month_plan['focus_areas']:
                    st.markdown(f"- {focus}")
                
                # Progress bar for the month
                progress = (month_plan['month'] / len(suggestions['monthly_plan'])) * 100
                st.progress(progress / 100)
        
        st.divider()
        
        # Visualization of weight loss journey
        st.subheader("📈 Projected Weight Journey")
        
        months = [0] + [plan['month'] for plan in suggestions['monthly_plan']]
        weights = [weight] + [plan['target_weight'] for plan in suggestions['monthly_plan']]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months,
            y=weights,
            mode='lines+markers',
            name='Projected Weight',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))
        
        fig.add_hline(y=target_weight, line_dash="dash", 
                     line_color="green", 
                     annotation_text="Target Weight")
        
        fig.update_layout(
            title="Weight Loss/Gain Projection",
            xaxis_title="Month",
            yaxis_title="Weight (kg)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Key success factors
        st.divider()
        st.subheader("🔑 Keys to Success")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🥗 Nutrition**
            - Track daily calories
            - Meal prep weekly
            - Stay hydrated
            - Eat protein-rich foods
            """)
        
        with col2:
            st.markdown("""
            **💪 Exercise**
            - Mix cardio & strength
            - Progressive overload
            - Rest days are crucial
            - Find activities you enjoy
            """)
        
        with col3:
            st.markdown("""
            **🧠 Mindset**
            - Set realistic goals
            - Celebrate small wins
            - Be consistent
            - Track your progress
            """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🔥 <strong>Calorie Burn Predictor & Fitness Tracker</strong> 🔥</p>
        <p>Remember: Consistency is key to achieving your fitness goals!</p>
        <p><em>Consult with healthcare professionals before starting any new exercise or nutrition program.</em></p>
    </div>
""", unsafe_allow_html=True)

# Sidebar footer
with st.sidebar:
    st.divider()
    st.markdown("### 📊 Quick Stats")
    if not logbook.get_logs(7):
        st.info("No activity this week. Start logging!")
    else:
        week_stats = logbook.get_stats(7)
        st.metric("This Week's Calories", f"{week_stats['total_calories']:.0f}")
        st.metric("Sessions", week_stats['total_sessions'])
    
    st.divider()
    st.caption("💡 Tip: Log your workouts daily for best results!")