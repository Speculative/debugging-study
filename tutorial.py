"""
Tutorial Task: Batch Test Grader

This module grades a batch of student exam submissions. Each student
has answers to multiple sections (multiple-choice, short-answer, essay).
Each section has a different weight toward the final score. A letter
grade is assigned based on the weighted total.

KNOWN ISSUE: Some students are receiving incorrect final scores and
letter grades. Your job is to figure out *why* and identify the root cause.
"""

SECTION_WEIGHTS = {
    "multiple_choice": 0.40,
    "short_answer":    0.35,
    "essay":           0.25,
}

GRADE_THRESHOLDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0,  "F"),
]


def assign_letter_grade(score: float) -> str:
    for threshold, letter in GRADE_THRESHOLDS:
        if score >= threshold:
            return letter
    return "F"


def grade_submissions(submissions: list[dict]) -> list[dict]:
    """
    Grade a batch of student submissions.

    Each submission should have:
        - student: str (student name)
        - sections: dict mapping section name to a score (0-100)

    Returns a list of result dicts with student name, section
    contributions, weighted total, and letter grade.
    """
    weighted_total = 0.0
    results = []

    for submission in submissions:
        student = submission["student"]
        sections = submission["sections"]
        breakdown = {}

        for section_name, raw_score in sections.items():
            weight = SECTION_WEIGHTS[section_name]
            contribution = raw_score * weight
            weighted_total += contribution
            breakdown[section_name] = {
                "raw_score": raw_score,
                "weight": weight,
                "contribution": round(contribution, 2),
            }

        letter = assign_letter_grade(weighted_total)

        results.append({
            "student": student,
            "breakdown": breakdown,
            "weighted_total": round(weighted_total, 2),
            "letter_grade": letter,
        })

    return results


# ---------- test data ----------

SUBMISSIONS = [
    {
        "student": "Alice",
        "sections": {
            "multiple_choice": 85,
            "short_answer": 78,
            "essay": 92,
        },
    },
    {
        "student": "Bob",
        "sections": {
            "multiple_choice": 62,
            "short_answer": 70,
            "essay": 55,
        },
    },
    {
        "student": "Carol",
        "sections": {
            "multiple_choice": 91,
            "short_answer": 88,
            "essay": 95,
        },
    },
    {
        "student": "Dan",
        "sections": {
            "multiple_choice": 45,
            "short_answer": 52,
            "essay": 40,
        },
    },
    {
        "student": "Eve",
        "sections": {
            "multiple_choice": 73,
            "short_answer": 81,
            "essay": 69,
        },
    },
    {
        "student": "Frank",
        "sections": {
            "multiple_choice": 98,
            "short_answer": 95,
            "essay": 88,
        },
    },
]


# ---------- expected vs actual ----------

def expected_result(submission: dict) -> dict:
    """What the result *should* be (independent per-student calculation)."""
    total = 0.0
    for section_name, raw_score in submission["sections"].items():
        total += raw_score * SECTION_WEIGHTS[section_name]
    return {
        "student": submission["student"],
        "expected_total": round(total, 2),
        "expected_grade": assign_letter_grade(total),
    }


if __name__ == "__main__":
    results = grade_submissions(SUBMISSIONS)

    print("=== Grading Results ===\n")
    for result, submission in zip(results, SUBMISSIONS):
        exp = expected_result(submission)
        match = "PASS" if result["weighted_total"] == exp["expected_total"] else "FAIL"
        print(f"[{match}] {result['student']}:")
        print(f"    Calculated: total={result['weighted_total']}, "
              f"grade={result['letter_grade']}")
        print(f"    Expected:   total={exp['expected_total']}, "
              f"grade={exp['expected_grade']}")
        print()