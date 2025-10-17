import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pickle
import os
import google.generativeai as genai
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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

# Gemini AI Configuration
def initialize_gemini(api_key, model_name="gemini-2.5-pro"):
    """Initialize Gemini AI chatbot"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def get_fitness_context(user_profile, recent_logs):
    """Create context for AI based on user data"""
    context = f"""You are a knowledgeable fitness and nutrition AI assistant. 
    
User Profile:
- Gender: {user_profile.get('gender', 'Not specified')}
- Age: {user_profile.get('age', 'Not specified')} years
- Height: {user_profile.get('height', 'Not specified')} cm
- Weight: {user_profile.get('weight', 'Not specified')} kg
- BMI: {user_profile.get('bmi', 'Not specified'):.1f}

"""
    
    if recent_logs:
        context += f"\nRecent Workout Summary (Last 7 days):\n"
        context += f"- Total sessions: {len(recent_logs)}\n"
        if len(recent_logs) > 0:
            total_calories = sum([log.get('calories_burned', 0) for log in recent_logs])
            avg_hr = sum([log.get('heart_rate', 0) for log in recent_logs]) / len(recent_logs)
            context += f"- Total calories burned: {total_calories:.0f} kcal\n"
            context += f"- Average heart rate: {avg_hr:.0f} bpm\n"
    
    context += """\n
Provide helpful, personalized advice on:
- Fitness and exercise recommendations
- Nutrition and diet guidance
- Calorie burn optimization
- BMI improvement strategies
- Workout planning and motivation
- Health and wellness tips

Keep responses concise, actionable, and encouraging. Always prioritize user safety and recommend consulting healthcare professionals for medical advice."""
    
    return context

def chat_with_gemini(model, user_message, context):
    """Send message to Gemini and get response"""
    try:
        prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔥 Predict Calories", 
    "📊 Logbook & Analytics", 
    "🥗 Nutrition Tips", 
    "💪 Exercise Recommendations",
    "🎯 Monthly Goals",
    "🤖 AI Fitness Coach"
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

# Tab 6: AI Fitness Coach
with tab6:
    st.header("🤖 AI Fitness Coach - Powered by Gemini")
    
    # API Key input
    with st.expander("⚙️ Gemini API Configuration", expanded=not st.session_state.gemini_api_key):
        st.markdown("""
        To use the AI Fitness Coach, you need a Google Gemini API key.
        
        **Get your free API key:**
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy and paste it below
        """)
        
        api_key_input = st.text_input(
            "Enter your Gemini API Key",
            type="password",
            value=st.session_state.gemini_api_key,
            help="Your API key is stored only in this session and never saved permanently"
        )
        
        if st.button("Save API Key"):
            st.session_state.gemini_api_key = api_key_input
            st.success("✅ API Key saved! You can now chat with your AI Fitness Coach.")
            st.rerun()
    
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please configure your Gemini API key above to start chatting.")
        st.info("💡 The AI Coach can help with workout plans, nutrition advice, motivation, and answer fitness questions based on your personal data!")
    else:
        # Initialize Gemini
        gemini_model = initialize_gemini(st.session_state.gemini_api_key)
        
        if gemini_model:
            st.success("✅ AI Fitness Coach is ready to help!")
            
            # Quick action buttons
            st.markdown("### 💬 Quick Questions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💪 Workout suggestions", use_container_width=True):
                    quick_msg = "Based on my profile, what workout should I do today?"
                    st.session_state.chat_history.append({"role": "user", "content": quick_msg})
            
            with col2:
                if st.button("🥗 Meal ideas", use_container_width=True):
                    quick_msg = "Suggest healthy meal ideas for my BMI category"
                    st.session_state.chat_history.append({"role": "user", "content": quick_msg})
            
            with col3:
                if st.button("📈 Progress tips", use_container_width=True):
                    quick_msg = "How can I improve my fitness progress?"
                    st.session_state.chat_history.append({"role": "user", "content": quick_msg})
            
            st.divider()
            
            # Chat interface
            st.markdown("### 💭 Chat with Your AI Coach")
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div style='background-color: #1a1a1a; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <strong>🧑 You:</strong><br>{message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background-color: #0a0a0a; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <strong>🤖 AI Coach:</strong><br>{message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Chat input
            user_message = st.chat_input("Ask your AI Fitness Coach anything...")
            
            if user_message:
                # Add user message to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_message
                })
                
                # Get context
                recent_logs = logbook.get_logs(7)
                context = get_fitness_context(st.session_state.user_profile, recent_logs)
                
                # Get AI response
                with st.spinner("🤔 AI Coach is thinking..."):
                    ai_response = chat_with_gemini(gemini_model, user_message, context)
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                st.rerun()
            
            # Clear chat button
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Example questions
            with st.expander("💡 Example Questions You Can Ask"):
                st.markdown("""
                - "What's the best time to exercise for weight loss?"
                - "How many calories should I eat to reach my target weight?"
                - "Suggest a 30-minute home workout routine"
                - "What are good post-workout snacks?"
                - "How can I stay motivated to exercise regularly?"
                - "Is my heart rate too high during workouts?"
                - "How do I build muscle while losing fat?"
                - "What supplements should I consider?"
                - "How much protein do I need daily?"
                - "Tips for better sleep to aid recovery"
                """)
            
            # AI Coach Features
            st.divider()
            st.markdown("### 🎯 AI Coach Capabilities")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Personalized Advice:**
                - Based on your BMI and fitness level
                - Considers your workout history
                - Adapts to your goals
                
                **Workout Planning:**
                - Custom exercise routines
                - Intensity recommendations
                - Form and technique tips
                """)
            
            with col2:
                st.markdown("""
                **Nutrition Guidance:**
                - Meal planning ideas
                - Macronutrient breakdowns
                - Healthy eating tips
                
                **Motivation & Support:**
                - Overcome plateaus
                - Stay consistent
                - Celebrate milestones
                """)
        else:
            st.error("❌ Failed to initialize AI Coach. Please check your API key.")

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