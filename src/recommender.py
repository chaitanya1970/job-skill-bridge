import pandas as pd


def normalize_skills(skills):
    """Normalize candidate/job skills into a clean lowercase list."""
    if skills is None:
        return []

    if isinstance(skills, str):
        skills = skills.split(",")

    return [
        str(skill).strip().lower()
        for skill in skills
        if str(skill).strip()
    ]


def calculate_skill_match(job_skills, candidate_skills):
    """
    Calculate percentage of job-listed skills
    that are possessed by the candidate.
    """
    job_set = set(normalize_skills(job_skills))
    candidate_set = set(normalize_skills(candidate_skills))

    if not job_set:
        return 0.0

    matched = job_set & candidate_set

    return round(
        (len(matched) / len(job_set)) * 100,
        2
    )


def get_matched_skills(job_skills, candidate_skills):
    """Return skills shared by candidate and job."""
    job_set = set(normalize_skills(job_skills))
    candidate_set = set(normalize_skills(candidate_skills))

    return sorted(job_set & candidate_set)


def get_skill_gaps(job_skills, candidate_skills):
    """Return skills required by the job but missing from candidate."""
    job_set = set(normalize_skills(job_skills))
    candidate_set = set(normalize_skills(candidate_skills))

    return sorted(job_set - candidate_set)


def location_score(job_location, candidate_location):
    """
    Score location compatibility.

    100 = exact/preferred location
    80  = remote
    0   = other location
    """
    job_location = str(job_location).lower().strip()
    candidate_location = str(candidate_location).lower().strip()

    if not candidate_location:
        return 50

    if candidate_location in job_location:
        return 100

    if "remote" in job_location:
        return 80

    return 0


def experience_score(min_exp, candidate_exp):
    """
    Score experience compatibility.
    """
    if pd.isna(min_exp):
        return 50

    min_exp = float(min_exp)
    candidate_exp = float(candidate_exp)

    if min_exp <= candidate_exp:
        return 100

    if min_exp <= candidate_exp + 1:
        return 80

    if min_exp <= candidate_exp + 2:
        return 50

    return 20


def classify_match(skill_match):
    """Convert numerical skill match into a readable category."""
    if skill_match >= 50:
        return "Strong Match"

    if skill_match >= 25:
        return "Moderate Match"

    return "Low Match"


def recommend_jobs(
    df,
    candidate_skills,
    candidate_role,
    candidate_location,
    candidate_experience,
    top_n=10,
    minimum_skill_match=25
):
    """
    Main Job Skill Bridge recommendation engine.

    Pipeline:
    1. Role filtering
    2. Experience filtering
    3. Skill matching
    4. Weak-match removal
    5. Location scoring
    6. Experience scoring
    7. Final ranking
    8. Skill-gap extraction
    """

    candidate_skills = normalize_skills(candidate_skills)

    # --------------------------------------------------------
    # 1. FILTER BY TARGET ROLE
    # --------------------------------------------------------

    jobs = df[
        df["role_category"] == candidate_role
    ].copy()

    # --------------------------------------------------------
    # 2. FILTER BY EXPERIENCE
    # --------------------------------------------------------

    jobs = jobs[
        jobs["minimumExperience"].fillna(0)
        <= candidate_experience + 1
    ].copy()

    if jobs.empty:
        return jobs

    # --------------------------------------------------------
    # 3. CALCULATE SKILL MATCH
    # --------------------------------------------------------

    jobs["skill_match"] = jobs["skills_clean"].apply(
        lambda skills: calculate_skill_match(
            skills,
            candidate_skills
        )
    )

    # --------------------------------------------------------
    # 4. REMOVE WEAK SKILL MATCHES
    # --------------------------------------------------------

    jobs = jobs[
        jobs["skill_match"] >= minimum_skill_match
    ].copy()

    if jobs.empty:
        return jobs

    # --------------------------------------------------------
    # 5. LOCATION SCORE
    # --------------------------------------------------------

    jobs["location_score"] = jobs["location"].apply(
        lambda location: location_score(
            location,
            candidate_location
        )
    )

    # --------------------------------------------------------
    # 6. EXPERIENCE SCORE
    # --------------------------------------------------------

    jobs["experience_score"] = jobs[
        "minimumExperience"
    ].apply(
        lambda experience: experience_score(
            experience,
            candidate_experience
        )
    )

    # --------------------------------------------------------
    # 7. MATCHED SKILLS
    # --------------------------------------------------------

    jobs["matched_skills"] = jobs["skills_clean"].apply(
        lambda skills: get_matched_skills(
            skills,
            candidate_skills
        )
    )

    # --------------------------------------------------------
    # 8. SKILL GAPS
    # --------------------------------------------------------

    jobs["skill_gaps"] = jobs["skills_clean"].apply(
        lambda skills: get_skill_gaps(
            skills,
            candidate_skills
        )
    )

    # --------------------------------------------------------
    # 9. FINAL SCORE
    # --------------------------------------------------------

    jobs["final_score"] = (
        jobs["skill_match"] * 0.70
        + jobs["experience_score"] * 0.20
        + jobs["location_score"] * 0.10
    ).round(2)

    # --------------------------------------------------------
    # 10. MATCH CATEGORY
    # --------------------------------------------------------

    jobs["match_category"] = jobs[
        "skill_match"
    ].apply(classify_match)

    # --------------------------------------------------------
    # 11. SORT
    # --------------------------------------------------------

    jobs = jobs.sort_values(
        by=[
            "final_score",
            "skill_match",
            "location_score"
        ],
        ascending=False
    )

    # --------------------------------------------------------
    # 12. RETURN TOP RESULTS
    # --------------------------------------------------------

    return jobs.head(top_n).copy()
def build_learning_path(skill_gaps, skill_frequency, max_skills=5):
    """
    Create a market-demand-driven learning priority list.

    Higher-demand missing skills are prioritized first.
    """

    if not skill_gaps:
        return []

    ranked_skills = sorted(
        skill_gaps,
        key=lambda skill: skill_frequency.get(
            str(skill).lower(),
            0
        ),
        reverse=True
    )

    learning_path = []

    for rank, skill in enumerate(
        ranked_skills[:max_skills],
        start=1
    ):

        demand = skill_frequency.get(
            str(skill).lower(),
            0
        )

        learning_path.append({
            "priority": rank,
            "skill": skill,
            "job_demand": demand
        })

    return learning_path