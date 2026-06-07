# my_routine_app.py - Simplified version (no database dependencies)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Purpose & Growth Tracker",
    page_icon="🙏",
    layout="wide"
)

# ============================================
# SESSION STATE (Simple file-based storage)
# ============================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'habits_data' not in st.session_state:
    st.session_state.habits_data = {}

DATA_FILE = "habit_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


# ============================================
# STEP 1: PRE-LOAD YOUR SPECIFIC HABITS
# ============================================
def initialize_habits():
    habits = {
        "Morning Prayer (4:00-5:00 AM)": {"periodicity": "daily", "streak": 0, "completed": []},
        "Morning Exercise (5:00-5:25 AM)": {"periodicity": "daily", "streak": 0, "completed": []},
        "Leave for work on time (5:45 AM)": {"periodicity": "daily", "streak": 0, "completed": []},
        "Evening Study Session (7:30-8:30 PM)": {"periodicity": "daily", "streak": 0, "completed": []},
        "Evening Prayer & Reflection (9:00-10:00 PM)": {"periodicity": "daily", "streak": 0, "completed": []},
        "In bed by 10:00 PM": {"periodicity": "daily", "streak": 0, "completed": []},
        "Saturday Deep Study Block (3 hours)": {"periodicity": "weekly", "streak": 0, "completed": []},
        "Weekly Review & Planning": {"periodicity": "weekly", "streak": 0, "completed": []},
    }
    return habits


# ============================================
# STEP 2: TIME-BASED REMINDERS
# ============================================
def show_reminder_card():
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute

    reminders = {
        (4, 0): "🙏 Time for Morning Prayer - Begin your day in God's presence",
        (5, 0): "🏃 Time to Exercise! - Bodyweight squats, push-ups, stretches",
        (5, 45): "🚀 Head to Office - Use commute for audio lectures",
        (19, 30): "📚 Evening Study Session - Pomodoro: 25 min study, 5 min break",
        (21, 0): "🙏 Evening Prayer - Review today's checklist",
        (22, 0): "😴 Time for Sleep - Put away phone, 6 hours for tomorrow",
    }

    for (hour, minute), message in reminders.items():
        if current_hour == hour and abs(current_minute - minute) <= 5:
            st.info(f"🔔 **Reminder:** {message}")
            break


# ============================================
# STEP 3: ROUTINE DASHBOARD
# ============================================
def show_routine_dashboard(habits):
    st.header("📅 Today's Routine Schedule")

    current_hour = datetime.now().hour
    today = datetime.now().strftime("%Y-%m-%d")

    # Get today's date for completion tracking
    if today not in st.session_state.habits_data:
        st.session_state.habits_data[today] = {}

    # Define schedule based on day type
    is_saturday = datetime.now().weekday() == 5
    is_sunday = datetime.now().weekday() == 6

    if is_saturday:
        schedule = {
            "6:00 AM": {"activity": "🙏 Morning Prayer", "duration": "45 min", "key": "Morning Prayer"},
            "6:45 AM": {"activity": "🏃 Extended Exercise", "duration": "45 min", "key": "Morning Exercise"},
            "9:00 AM": {"activity": "📖 Deep Study Block", "duration": "3 hours", "key": "Saturday Deep Study"},
            "9:00 PM": {"activity": "✅ Weekly Review", "duration": "60 min", "key": "Weekly Review"},
        }
    elif is_sunday:
        schedule = {
            "6:00 AM": {"activity": "🙏 Morning Prayer", "duration": "60 min", "key": "Morning Prayer"},
            "8:00 AM": {"activity": "⛪ Church Service", "duration": "6 hours", "key": "Church"},
            "4:00 PM": {"activity": "📚 Light Study & Planning", "duration": "90 min", "key": "Light Study"},
            "9:00 PM": {"activity": "🙏 Evening Prayer", "duration": "60 min", "key": "Evening Prayer"},
        }
    else:
        schedule = {
            "4:00 AM": {"activity": "🙏 Morning Prayer", "duration": "60 min", "key": "Morning Prayer"},
            "5:00 AM": {"activity": "🏃 Morning Exercise", "duration": "25 min", "key": "Morning Exercise"},
            "5:45 AM": {"activity": "🚀 Leave for Office", "duration": "commute", "key": "Leave for work"},
            "7:30 PM": {"activity": "📚 Evening Study", "duration": "60 min", "key": "Evening Study"},
            "9:00 PM": {"activity": "🙏 Evening Prayer", "duration": "60 min", "key": "Evening Prayer"},
            "10:00 PM": {"activity": "😴 Bedtime", "duration": "6+ hours", "key": "In bed by 10:00 PM"},
        }

    for time, details in schedule.items():
        time_hour = int(time.split(":")[0])
        is_next = (time_hour - current_hour) in [0, 1] if 0 <= time_hour <= 23 else False

        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])

            with col1:
                st.write(f"**{time}**")
            with col2:
                st.write(f"{details['activity']}")
                st.caption(f"Duration: {details['duration']}")
            with col3:
                # Get streak from habits
                habit_key = details['key']
                if habit_key in habits:
                    streak = habits[habit_key].get('streak', 0)
                    st.write(f"🔥 Streak: {streak}")
                else:
                    st.write("🔥 Streak: 0")
            with col4:
                completed_key = f"{today}_{details['key']}"
                is_completed = st.session_state.habits_data[today].get(details['key'], False)

                if is_completed:
                    st.success("✅ Done!")
                else:
                    if st.button("✅ Check-off", key=completed_key):
                        st.session_state.habits_data[today][details['key']] = True
                        save_data(st.session_state.habits_data)
                        # Update streak
                        if details['key'] in habits:
                            habits[details['key']]['streak'] += 1
                        st.success(f"Great job! {details['activity']} completed! 🎉")
                        st.rerun()

            if is_next:
                st.info("👉 **Next up!** Prepare for this activity")
            st.divider()


# ============================================
# STEP 4: ACADEMIC PROGRESS TRACKER
# ============================================
def show_academic_dashboard():
    st.header("📚 Academic Progress - 3 Courses/Month")

    col1, col2, col3 = st.columns(3)

    with col1:
        weekday_hours = 5
        st.metric("Weekday Study", f"{weekday_hours} hrs", "Mon-Fri evenings")

    with col2:
        saturday_hours = 4.5
        st.metric("Saturday Deep Study", f"{saturday_hours} hrs", "9 AM block + review")

    with col3:
        total_weekly = weekday_hours + saturday_hours
        st.metric("Total Weekly", f"{total_weekly} hrs", "Target: 19 hrs")

    st.subheader("Monthly Course Progress")
    courses_completed = st.slider("Courses completed this month", 0, 3, 0)

    progress = courses_completed / 3
    st.progress(progress)

    if courses_completed == 3:
        st.balloons()
        st.success("🎉 EXCELLENT! You've achieved your 3 courses per month goal!")
    else:
        st.info(f"🎯 Target: 3 courses this month ({courses_completed}/3 completed)")

    # Study streak
    st.subheader("🔥 Current Study Streak")
    study_days = st.number_input("How many consecutive days have you studied?", 0, 30, 0, key="study_streak")
    if study_days >= 5:
        st.success(f"Great! {study_days} day study streak! Keep going!")
    elif study_days > 0:
        st.info(f"{study_days} day study streak")
    else:
        st.warning("Start your 7:30 PM study session today!")


# ============================================
# STEP 5: ACCOUNTABILITY CHECKLIST
# ============================================
def show_accountability_checklist():
    st.header("✅ Daily Accountability Checklist")
    st.caption("Review this every night before evening prayer")

    checklist_items = [
        "Morning prayer completed (4-5 AM)",
        "Exercise done (at least 15 minutes)",
        "Breakfast taken (or fast observed)",
        "Left for work on time (5:45 AM)",
        "Worked diligently and professionally",
        "Evening study session completed (1 hr)",
        "Evening prayer done (9-10 PM)",
        "In bed by 10:00 PM"
    ]

    completed_count = 0

    for item in checklist_items:
        checked = st.checkbox(item, key=f"check_{item[:20]}")
        if checked:
            completed_count += 1

    progress = completed_count / len(checklist_items)
    st.progress(progress)

    if progress == 1.0:
        st.balloons()
        st.success("🎉 PERFECT DAY! 'Consistency in small things builds extraordinary lives.'")
        st.markdown("📖 *'Commit your works to the LORD, and your plans will succeed.' — Proverbs 16:3*")
    elif progress >= 0.75:
        st.success(f"✅ Great progress! {completed_count}/{len(checklist_items)} completed")
    elif progress >= 0.5:
        st.warning(f"⚠️ {completed_count}/{len(checklist_items)} - Tomorrow you can do better")
    else:
        st.error(f"❌ Only {completed_count}/{len(checklist_items)} - Review what held you back")

    if st.button("💾 Save Today's Accountability"):
        st.success("Accountability record saved! Proverbs 16:3")


# ============================================
# ANALYTICS DASHBOARD
# ============================================
def show_analytics(habits):
    st.header("📊 Your Progress Analytics")

    data = []
    for habit_name, habit_data in habits.items():
        data.append({
            'Habit': habit_name,
            'Streak': habit_data.get('streak', 0),
            'Periodicity': habit_data.get('periodicity', 'daily')
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    fig = px.bar(df, x='Habit', y='Streak',
                 title='Current Streaks by Habit',
                 color='Streak', color_continuous_scale='greens')
    st.plotly_chart(fig, use_container_width=True)


# ============================================
# SIDEBAR - AUTHENTICATION & NAVIGATION
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/prayer-beads.png", width=80)
    st.title("Purpose & Growth")
    st.caption("*Discipline · Diligence · Accountability*")
    st.divider()
    st.write("**Verse for today:**")
    st.info("*'Commit your works to the LORD, and your plans will succeed.'* — Proverbs 16:3")
    st.divider()

    if not st.session_state.authenticated:
        auth_choice = st.radio("Select Authentication Option", ["Login", "Guest Mode"])

        if auth_choice == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.habits = initialize_habits()
                st.rerun()
        else:
            if st.button("Continue as Guest"):
                st.session_state.authenticated = True
                st.session_state.username = "Guest"
                st.session_state.habits = initialize_habits()
                st.rerun()
    else:
        st.success(f"Welcome, {st.session_state.username}!")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

    st.divider()
    page = st.radio("Navigate", [
        "📅 Today's Routine",
        "📚 Academic Progress",
        "✅ Accountability",
        "📊 Analytics"
    ])

# ============================================
# MAIN CONTENT
# ============================================
if st.session_state.authenticated:
    show_reminder_card()

    if page == "📅 Today's Routine":
        show_routine_dashboard(st.session_state.habits)
    elif page == "📚 Academic Progress":
        show_academic_dashboard()
    elif page == "✅ Accountability":
        show_accountability_checklist()
    elif page == "📊 Analytics":
        show_analytics(st.session_state.habits)
else:
    st.info("👋 Please login or continue as Guest to start tracking your habits")

# Footer
st.markdown("---")
st.caption("Purpose & Growth Habit Tracker | Built with Python, Streamlit, and Faith")