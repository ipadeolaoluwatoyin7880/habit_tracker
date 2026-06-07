import streamlit as st

st.set_page_config(page_title="Purpose & Growth Tracker", page_icon="🙏")

st.title("Purpose & Growth Habit Tracker")
st.write("Welcome to your daily habit tracker!")

st.header("Today's Habits")

habits = [
    "🙏 Morning Prayer (4:00-5:00 AM)",
    "🏃 Morning Exercise (5:00-5:25 AM)",
    "🚀 Leave for work on time (5:45 AM)",
    "📚 Evening Study Session (7:30-8:30 PM)",
    "🙏 Evening Prayer (9:00-10:00 PM)",
    "😴 In bed by 10:00 PM",
]

completed_count = 0

for habit in habits:
    if st.checkbox(habit, key=habit):
        completed_count += 1
        st.success(f"✅ Completed: {habit}")

st.divider()
st.metric("Habits Completed Today", f"{completed_count}/{len(habits)}")

if completed_count == len(habits):
    st.balloons()
    st.success("🎉 PERFECT DAY! All habits completed!")

st.caption("*'Commit your works to the LORD, and your plans will succeed.' — Proverbs 16:3*")