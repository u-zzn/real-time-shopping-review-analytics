"""
analysis_results/ 폴더의 CSV 파일(spark_analysis.py 출력)을 읽어 PNG 그래프 8개를 생성합니다.
CSV가 없는 경우 샘플 CSV에서 직접 계산하여 대체합니다.
"""

import platform
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # HDP Sandbox 등 디스플레이 없는 환경을 위한 백엔드 설정
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 플랫폼별 한글 폰트 설정 (HDP Sandbox에서는 DejaVu Sans 폴백)
_sys = platform.system()
if _sys == "Darwin":
    matplotlib.rcParams["font.family"] = ["AppleGothic", "DejaVu Sans"]
elif _sys == "Linux":
    matplotlib.rcParams["font.family"] = ["NanumGothic", "UnDotum", "DejaVu Sans"]
else:
    matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
sns.set_theme(style="whitegrid", rc={"axes.unicode_minus": False})

RESULTS_DIR = Path("analysis_results")
RESULTS_DIR.mkdir(exist_ok=True)
SAMPLE_PATH = "data/sample/shopping_reviews_sample.csv"
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]


def _sample_df():
    df = pd.read_csv(SAMPLE_PATH)
    df["sentiment"] = df["rating"].apply(
        lambda r: "Positive" if r >= 4 else ("Negative" if r <= 2 else "Neutral")
    )
    df["review_length"] = df["review_text"].astype(str).str.len()
    return df


def load(csv_name, fallback_fn):
    p = RESULTS_DIR / csv_name
    return pd.read_csv(p) if p.exists() else fallback_fn()


# Plot 1: Rating Distribution
def _rating_fb():
    d = _sample_df()["rating"].value_counts().sort_index().reset_index()
    d.columns = ["rating", "review_count"]
    return d

rating = load("analysis_rating_distribution.csv", _rating_fb)
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(rating["rating"].astype(str), rating["review_count"], color=PALETTE[0])
ax.set_title("Rating Distribution", fontsize=14, fontweight="bold")
ax.set_xlabel("Rating (Stars)")
ax.set_ylabel("Number of Reviews")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
            str(int(bar.get_height())), ha="center", fontsize=10)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "plot1_rating_distribution.png", dpi=150)
plt.close()

# Plot 2: Top 10 Categories
def _cat_fb():
    d = _sample_df()["category"].value_counts().head(10).reset_index()
    d.columns = ["category", "review_count"]
    return d

cat = load("analysis_category_distribution.csv", _cat_fb).head(10)
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="category", y="review_count", data=cat,
            hue="category", palette="Blues_d", legend=False, ax=ax)
plt.setp(ax.get_xticklabels(), rotation=40, ha="right", fontsize=9)
ax.set_title("Top 10 Categories by Review Volume", fontsize=14, fontweight="bold")
ax.set_xlabel("Category")
ax.set_ylabel("Number of Reviews")
plt.tight_layout()
plt.savefig(RESULTS_DIR / "plot2_category_distribution.png", dpi=150)
plt.close()

# Plot 3: Average Rating by Category
def _avg_fb():
    df = _sample_df()
    d = (df.groupby("category")["rating"]
           .agg(avg_rating="mean", review_count="count")
           .reset_index()
           .query("review_count >= 5")
           .sort_values("avg_rating", ascending=False))
    return d

avg = load("analysis_avg_rating_by_category.csv", _avg_fb).head(12)
mean_val = avg["avg_rating"].mean()
fig, ax = plt.subplots(figsize=(11, 5))
sns.barplot(x="category", y="avg_rating", data=avg,
            hue="category", palette="Greens_d", legend=False, ax=ax)
ax.axhline(mean_val, color="red", linestyle="--", alpha=0.7,
           label=f"Overall avg: {mean_val:.2f}")
plt.setp(ax.get_xticklabels(), rotation=40, ha="right", fontsize=9)
ax.set_ylim(0, 5.5)
ax.set_title("Average Rating by Category", fontsize=14, fontweight="bold")
ax.set_xlabel("Category")
ax.set_ylabel("Average Rating (1–5)")
ax.legend()
for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.05,
            f"{p.get_height():.2f}", ha="center", fontsize=8)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "plot3_avg_rating_by_category.png", dpi=150)
plt.close()

# Plot 4: Sentiment Distribution (pie)
def _sent_fb():
    d = _sample_df()["sentiment"].value_counts().reset_index()
    d.columns = ["sentiment", "review_count"]
    return d

sent = load("analysis_sentiment_distribution.csv", _sent_fb)
sent_colors = {"Positive": "#55A868", "Neutral": "#4C72B0", "Negative": "#C44E52"}
colors = [sent_colors.get(s, "#888") for s in sent["sentiment"]]
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(sent["review_count"], labels=sent["sentiment"], autopct="%1.1f%%",
       colors=colors, startangle=140, textprops={"fontsize": 11})
ax.set_title("Review Sentiment Distribution", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(RESULTS_DIR / "plot4_sentiment_distribution.png", dpi=150)
plt.close()

# Plot 5: Language Distribution
def _lang_fb():
    d = _sample_df()["language"].value_counts().reset_index()
    d.columns = ["language", "review_count"]
    return d

lang_labels = {"de": "German", "en": "English", "es": "Spanish",
               "fr": "French", "ja": "Japanese", "zh": "Chinese"}
lang = load("analysis_language_distribution.csv", _lang_fb)
lang = lang.dropna(subset=["language"])
lang = lang[lang["language"].astype(str).str.match(r'^[a-z]{2}$')]
lang["label"] = lang["language"].astype(str).map(lambda x: lang_labels.get(x, x))
n = len(lang)
bar_colors = (PALETTE * (n // len(PALETTE) + 1))[:n]
fig, ax = plt.subplots(figsize=(min(16, max(8, n * 1.2)), 5))
ax.bar(lang["label"], lang["review_count"], color=bar_colors)
ax.set_title("Review Language Distribution", fontsize=14, fontweight="bold")
ax.set_xlabel("Language")
ax.set_ylabel("Number of Reviews")
for i, v in enumerate(lang["review_count"]):
    ax.text(i, v + lang["review_count"].max() * 0.01, str(int(v)),
            ha="center", fontsize=10)
fig.savefig(RESULTS_DIR / "plot5_language_distribution.png", dpi=150, bbox_inches="tight")
plt.close()

# Plot 6: Negative Review Rate by Top Categories (horizontal bar)
def _neg_fb():
    df = _sample_df()
    d = df.groupby("category").agg(
        total_reviews=("rating", "count"),
        negative_count=("sentiment", lambda x: (x == "Negative").sum()),
    ).reset_index().query("total_reviews >= 5")
    d["negative_rate_pct"] = (d["negative_count"] / d["total_reviews"] * 100).round(1)
    return d.sort_values("total_reviews", ascending=False).head(10)

neg = load("analysis_negative_rate_by_category.csv", _neg_fb)
neg = neg.sort_values("negative_rate_pct", ascending=True)
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(neg["category"], neg["negative_rate_pct"], color=PALETTE[3])
ax.set_xlabel("Negative Review Rate (%)")
ax.set_title("Negative Review Rate by Top Categories",
             fontsize=14, fontweight="bold")
for i, v in enumerate(neg["negative_rate_pct"]):
    ax.text(v + 0.4, i, f"{v:.1f}%", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "plot6_negative_rate_by_category.png", dpi=150)
plt.close()

# Plot 7: Category × Language Heatmap
def _heatmap_fb():
    df = _sample_df()
    d = (df.groupby(["category", "language"])["rating"]
           .agg(avg_rating="mean", review_count="count")
           .reset_index()
           .query("review_count >= 3")
           .assign(avg_rating=lambda x: x["avg_rating"].round(2)))
    return d

heat_long = load("analysis_category_language_heatmap.csv", _heatmap_fb)

top_cats = load("analysis_category_distribution.csv", _cat_fb)["category"].head(8).tolist()
heat_filtered = heat_long[
    heat_long["category"].isin(top_cats) &
    heat_long["language"].astype(str).str.match(r'^[a-z]{2}$')
]

pivot = heat_filtered.pivot_table(
    index="category", columns="language", values="avg_rating", aggfunc="mean"
).reindex(top_cats).dropna(how="all")
pivot.columns = [lang_labels.get(c, c) for c in pivot.columns]

if not pivot.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn",
                vmin=1, vmax=5, linewidths=0.5, ax=ax)
    ax.set_title("Average Rating by Category and Language",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Language")
    ax.set_ylabel("Category")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "plot7_category_language_heatmap.png", dpi=150)
    plt.close()

# Plot 8: ML Model Coefficients
coef_csv = RESULTS_DIR / "analysis_model_coefficients.csv"
if coef_csv.exists():
    coef = pd.read_csv(coef_csv).sort_values("coefficient", ascending=True)
    colors_coef = ["#C44E52" if c < 0 else "#55A868" for c in coef["coefficient"]]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(coef["feature"], coef["coefficient"], color=colors_coef)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Coefficient  (positive → Positive sentiment)")
    ax.set_title("Logistic Regression — Feature Coefficients\n"
                 "(Sentiment Prediction: Positive vs. Negative)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "plot8_model_coefficients.png", dpi=150)
    plt.close()

print(f"Plots saved to {RESULTS_DIR}/")
