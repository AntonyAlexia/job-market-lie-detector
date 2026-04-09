Job Market Intelligence & Skill Gap Analysis System

This project analyzes discrepancies between job postings and real-world skill usage for Data Analyst roles.

I built an end-to-end analytics system that identifies hidden skill gaps in the job market and provides actionable insights for job seekers and recruiters.

💡 Problem Statement

Job descriptions often do not reflect actual day-to-day analyst work.
This leads to:

candidates focusing on the wrong skills
companies filtering out strong applicants
inefficient hiring processes
🛠️ What I Built
Scraped live job postings using Python + JSearch API
Extracted 500+ skills using LLaMA3 (Groq AI)
Designed a skill-gap analysis framework
Compared job requirements vs real-world usage
Built an interactive dashboard using Streamlit
📂 Project Structure
job_postings_raw.csv → raw scraped data
job_postings_with_skills.csv → extracted skills dataset
lie_detector_final.csv → final skill gap analysis
app.py → Streamlit dashboard
📊 Key Insights
SQL is used by ~90% of analysts but mentioned in only ~60% of job postings
Excel, communication, and problem-solving are heavily underrepresented
Job postings overemphasize tools like Spark, Hadoop, and Java

👉 There is a clear mismatch between hiring expectations and actual job requirements.
