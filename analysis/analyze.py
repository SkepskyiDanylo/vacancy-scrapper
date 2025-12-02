import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def top_vacancies_per_skills_plot(dt: pd.DataFrame, path: Path) -> None:
    dt["skills"] = dt["skills"].apply(
        lambda x: [s.strip() for s in str(x).split(",")] if pd.notna(x) else []
    )
    all_skills = [
        skill for skills_list in dt["skills"] for skill in skills_list if skill
    ]

    skill_counts = Counter(all_skills)

    skills_df = pd.DataFrame(
        skill_counts.items(), columns=["skill", "count"]
    ).sort_values("count", ascending=False)

    top = 10
    plt.figure(figsize=(10, 6))
    plt.barh(skills_df["skill"].head(top)[::-1], skills_df["count"].head(top)[::-1])
    plt.title(f"Top {top} Skills by Vacancy Count")
    plt.xlabel("Vacancies Count")
    plt.ylabel("Skill")
    plt.tight_layout()
    file_path = path / "top_vacancies.png"
    plt.savefig(file_path, dpi=300, bbox_inches="tight")


def top_companies_by_vacancies(dt: pd.DataFrame, path: Path) -> None:
    top_companies = dt["company_name"].value_counts().head(10)

    plt.figure(figsize=(10, 6))
    top_companies.plot(kind="barh")
    plt.title("Top 10 Companies by Vacancy Count")
    plt.xlabel("Vacancies Count")
    plt.ylabel("Company")
    plt.tight_layout()
    file_path = path / "top_companies.png"
    plt.savefig(file_path, dpi=300, bbox_inches="tight")


def experience_distribution(dt: pd.DataFrame, path: Path) -> None:
    dt["experience"] = pd.to_numeric(dt["experience"], errors="coerce")

    plt.figure(figsize=(8, 5))
    dt["experience"].plot(kind="hist", bins=10, rwidth=0.8)
    plt.title("Distribution of Experience (years)")
    plt.xlabel("Years of Experience")
    plt.ylabel("Vacancies Count")
    file_path = path / "experience_distribution.png"
    plt.savefig(file_path, dpi=300, bbox_inches="tight")


def analyze(file: Path, graphs_path: Path) -> None:
    os.makedirs(graphs_path, exist_ok=True)

    dt = pd.read_csv(file)
    dt.replace([None], np.nan, inplace=True)

    top_vacancies_per_skills_plot(dt, graphs_path)
    top_companies_by_vacancies(dt, graphs_path)
    experience_distribution(dt, graphs_path)
