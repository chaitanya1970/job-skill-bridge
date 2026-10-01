import streamlit as st
import pandas as pd
import os
import sys
from collections import Counter


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.append(PROJECT_ROOT)


# ============================================================
# IMPORT RECOMMENDATION ENGINE
# ============================================================

from src.recommender import (
    recommend_jobs,
    build_learning_path
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Job Skill Bridge",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# LOAD PROCESSED DATA
# ============================================================

@st.cache_data
def load_data():

    data_path = os.path.join(
        PROJECT_ROOT,
        "data",
        "processed",
        "jobs_clean.pkl"
    )

    return pd.read_pickle(data_path)


df = load_data()


# ============================================================
# CALCULATE MARKET SKILL FREQUENCY
# ============================================================

@st.cache_data
def calculate_skill_frequency(data):

    counter = Counter()

    for skills in data["skills_clean"]:

        for skill in skills:

            counter[str(skill).lower()] += 1

    return counter


skill_frequency = calculate_skill_frequency(df)


# ============================================================
# HEADER
# ============================================================

st.title("🎯 Job Skill Bridge")

st.subheader(
    "Personalized Job & Skill Intelligence"
)

st.write(
    "Find relevant jobs and discover the skills "
    "that can improve your career opportunities."
)


# ============================================================
# MAIN NAVIGATION
# ============================================================

tab_recommend, tab_market = st.tabs(
    [
        "🎯 Recommendations",
        "📊 Market Intelligence"
    ]
)


# ============================================================
# TAB 1 — RECOMMENDATIONS
# ============================================================

with tab_recommend:

    st.header(
        "👤 Build Your Candidate Profile"
    )

    # --------------------------------------------------------
    # INPUT SECTION
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        candidate_role = st.selectbox(
            "Target Career",
            [
                "Data Engineering",
                "Data Analytics",
                "AI / ML",
                "Software Development",
                "Cloud / DevOps"
            ]
        )

        candidate_location = st.text_input(
            "Preferred Location",
            value="Hyderabad"
        )

    with col2:

        candidate_experience = st.number_input(
            "Years of Experience",
            min_value=0,
            max_value=20,
            value=0,
            step=1
        )

        skills_input = st.text_input(
            "Your Skills",
            value="Python, SQL, Pandas, Power BI"
        )

    st.caption(
        "Enter your skills separated by commas."
    )

    st.divider()

    # --------------------------------------------------------
    # FIND JOBS BUTTON
    # --------------------------------------------------------

    if st.button(
        "🔎 Find My Jobs",
        type="primary",
        use_container_width=True
    ):

        candidate_skills = [
            skill.strip().lower()
            for skill in skills_input.split(",")
            if skill.strip()
        ]

        # ----------------------------------------------------
        # INPUT VALIDATION
        # ----------------------------------------------------

        if not candidate_skills:

            st.warning(
                "Please enter at least one skill."
            )

        elif not candidate_location.strip():

            st.warning(
                "Please enter a preferred location."
            )

        else:

            # ------------------------------------------------
            # PROFILE SUMMARY
            # ------------------------------------------------

            st.subheader(
                "👤 Your Candidate Profile"
            )

            profile1, profile2, profile3 = st.columns(3)

            with profile1:

                st.write(
                    "**Target Career**"
                )

                st.write(
                    candidate_role
                )

            with profile2:

                st.write(
                    "**Preferred Location**"
                )

                st.write(
                    candidate_location
                )

            with profile3:

                st.write(
                    "**Experience**"
                )

                st.write(
                    f"{candidate_experience} years"
                )

            st.write(
                "**Your Skills**"
            )

            st.write(
                " • ".join(
                    skill.title()
                    for skill in candidate_skills
                )
            )

            st.divider()

            # ------------------------------------------------
            # RECOMMENDATION ENGINE
            # ------------------------------------------------

            recommendations = recommend_jobs(
                df=df,
                candidate_skills=candidate_skills,
                candidate_role=candidate_role,
                candidate_location=candidate_location,
                candidate_experience=candidate_experience,
                top_n=10,
                minimum_skill_match=25
            )

            st.header(
                "🎯 Recommended Jobs"
            )

            # ------------------------------------------------
            # NO RESULTS
            # ------------------------------------------------

            if recommendations.empty:

                st.warning(
                    "No sufficiently relevant jobs were found."
                )

                st.info(
                    "Try adding more skills, changing your "
                    "location, or selecting another career."
                )

            # ------------------------------------------------
            # RESULTS
            # ------------------------------------------------

            else:

                st.success(
                    f"{len(recommendations)} relevant "
                    "opportunities found."
                )

                # ============================================
                # JOB CARDS
                # ============================================

                for index, (_, job) in enumerate(
                    recommendations.iterrows(),
                    start=1
                ):

                    with st.container(
                        border=True
                    ):

                        # ------------------------------------
                        # JOB INFORMATION
                        # ------------------------------------

                        st.subheader(
                            f"{index}. 💼 {job['title']}"
                        )

                        st.write(
                            f"🏢 **{job['companyName']}**"
                        )

                        st.write(
                            f"📍 {job['location']}"
                        )

                        # ------------------------------------
                        # SCORES
                        # ------------------------------------

                        score1, score2, score3 = st.columns(3)

                        with score1:

                            st.metric(
                                "🎯 Match Score",
                                f"{job['final_score']:.1f}%"
                            )

                        with score2:

                            st.metric(
                                "🧩 Skill Match",
                                f"{job['skill_match']:.1f}%"
                            )

                        with score3:

                            st.metric(
                                "📈 Experience Fit",
                                f"{job['experience_score']:.0f}%"
                            )

                        # ------------------------------------
                        # MATCH CATEGORY
                        # ------------------------------------

                        if (
                            job["match_category"]
                            == "Strong Match"
                        ):

                            st.success(
                                "🟢 Strong Skill Match"
                            )

                        else:

                            st.info(
                                "🟡 Moderate Skill Match"
                            )

                        # ------------------------------------
                        # MATCHED SKILLS
                        # ------------------------------------

                        st.write(
                            "### ✅ Skills You Already Have"
                        )

                        matched_skills = job[
                            "matched_skills"
                        ]

                        if matched_skills:

                            st.write(
                                " • ".join(
                                    skill.title()
                                    for skill in matched_skills
                                )
                            )

                        else:

                            st.write(
                                "No direct skill matches."
                            )

                        # ------------------------------------
                        # SKILL GAPS
                        # ------------------------------------

                        st.write(
                            "### 🧩 Skill Gaps"
                        )

                        skill_gaps = job[
                            "skill_gaps"
                        ]

                        if skill_gaps:

                            # Rank missing skills according
                            # to their overall market demand.

                            prioritized_gaps = sorted(
                                skill_gaps,
                                key=lambda skill:
                                    skill_frequency.get(
                                        skill.lower(),
                                        0
                                    ),
                                reverse=True
                            )

                            display_gaps = (
                                prioritized_gaps[:8]
                            )

                            for rank, skill in enumerate(
                                display_gaps,
                                start=1
                            ):

                                demand = (
                                    skill_frequency.get(
                                        skill.lower(),
                                        0
                                    )
                                )

                                st.write(
                                    f"**{rank}. "
                                    f"{skill.title()}** "
                                    f"— demanded in "
                                    f"**{demand:,} jobs**"
                                )

                        else:

                            st.success(
                                "🎉 No major skill gaps identified."
                            )

                        # ------------------------------------
                        # LEARNING PATH
                        # ------------------------------------

                        st.write(
                            "### 🚀 What Should You Learn Next?"
                        )

                        learning_path = build_learning_path(
                            skill_gaps=skill_gaps,
                            skill_frequency=skill_frequency,
                            max_skills=5
                        )

                        if learning_path:

                            for item in learning_path:

                                st.write(
                                    f"**Priority "
                                    f"{item['priority']} → "
                                    f"{item['skill'].title()}**"
                                )

                                st.caption(
                                    f"Market demand: "
                                    f"{item['job_demand']:,} "
                                    f"job postings"
                                )

                        else:

                            st.success(
                                "🎉 Your current skills cover "
                                "the identified requirements."
                            )

                        # ------------------------------------
                        # WHY THIS JOB?
                        # ------------------------------------

                        st.write(
                            "### 💡 Why This Job?"
                        )

                        if job[
                            "skill_match"
                        ] >= 50:

                            st.write(
                                "✓ Strong overlap with your skills"
                            )

                        else:

                            st.write(
                                "✓ Partial overlap with your skills"
                            )

                        if job[
                            "location_score"
                        ] == 100:

                            st.write(
                                "✓ Matches your preferred location"
                            )

                        elif job[
                            "location_score"
                        ] == 80:

                            st.write(
                                "✓ Remote opportunity"
                            )

                        if job[
                            "experience_score"
                        ] >= 100:

                            st.write(
                                "✓ Experience requirement fits"
                            )

                        elif job[
                            "experience_score"
                        ] >= 80:

                            st.write(
                                "✓ Experience requirement is close"
                            )


# ============================================================
# TAB 2 — MARKET INTELLIGENCE
# ============================================================

with tab_market:

    st.header(
        "📊 Job Market Intelligence"
    )

    st.write(
        "Explore hiring patterns, skill demand, "
        "career categories, and job locations "
        "across the dataset."
    )

    st.divider()

    # --------------------------------------------------------
    # MARKET METRICS
    # --------------------------------------------------------

    total_jobs = len(df)

    fresher_jobs = len(
        df[
            df["minimumExperience"] <= 1
        ]
    )

    python_jobs = skill_frequency.get(
        "python",
        0
    )

    hyderabad_jobs = df[
        df["location"].str.contains(
            "Hyderabad",
            case=False,
            na=False
        )
    ].shape[0]

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:

        st.metric(
            "📋 Total Jobs",
            f"{total_jobs:,}"
        )

    with metric2:

        st.metric(
            "🎓 Fresher-Friendly",
            f"{fresher_jobs:,}"
        )

    with metric3:

        st.metric(
            "🐍 Python Jobs",
            f"{python_jobs:,}"
        )

    with metric4:

        st.metric(
            "📍 Hyderabad Jobs",
            f"{hyderabad_jobs:,}"
        )

    st.divider()

    # --------------------------------------------------------
    # TOP SKILLS
    # --------------------------------------------------------

    st.subheader(
        "🔥 Most Demanded Skills"
    )

    top_skills = skill_frequency.most_common(
        10
    )

    skills_df = pd.DataFrame(
        top_skills,
        columns=[
            "Skill",
            "Job Postings"
        ]
    )

    skills_df = skills_df.set_index(
        "Skill"
    )

    st.bar_chart(
        skills_df
    )

    st.divider()

    # --------------------------------------------------------
    # CAREER CATEGORY DEMAND
    # --------------------------------------------------------

    st.subheader(
        "💼 Technology Career Demand"
    )

    role_counts = (
        df[
            df["role_category"] != "Other"
        ]["role_category"]
        .value_counts()
    )

    st.bar_chart(
        role_counts
    )

    st.divider()

    # --------------------------------------------------------
    # TOP LOCATIONS
    # --------------------------------------------------------

    st.subheader(
        "📍 Top Job Locations"
    )

    location_counts = (
        df["location"]
        .value_counts()
        .head(10)
    )

    st.bar_chart(
        location_counts
    )

    st.divider()

    st.caption(
        "Market intelligence is calculated from the "
        "processed job-market dataset."
    )