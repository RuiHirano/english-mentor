import streamlit as st
import yaml
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
WORKSPACE_DIR = Path(__file__).parent.parent / "workspace"

st.set_page_config(page_title="English Mentor Dashboard", page_icon="📚", layout="wide")


def load_yaml(path: Path):
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def parse_session_file(path: Path):
    """セッションファイルからサマリー行を抽出"""
    text = path.read_text()
    info = {"file": path.name}
    for line in text.splitlines():
        if line.startswith("- Skill:"):
            info["skill"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Score:"):
            raw = line.split(":", 1)[1].strip()
            # "3.5/5 (70%)" のようなフォーマット
            if "/" in raw:
                score_part = raw.split("(")[0].strip()
                parts = score_part.split("/")
                info["score"] = float(parts[0])
                info["total"] = float(parts[1])
        elif line.startswith("- Questions:"):
            info["questions"] = int(line.split(":", 1)[1].strip())
    return info


profile = load_yaml(DATA_DIR / "profile.yaml")
progress = load_yaml(DATA_DIR / "progress.yaml")
plan = load_yaml(DATA_DIR / "plan.yaml")
preferences = load_yaml(DATA_DIR / "preferences.yaml")

st.title("📚 English Mentor Dashboard")

# --- プロフィール ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("目標", profile.get("goal") or "未設定")
with col2:
    st.metric("レベル", profile.get("level") or "未設定")
with col3:
    st.metric("1日の目安", f'{profile.get("daily_minutes", 0)}分')

if profile.get("target"):
    st.info(f'🎯 {profile["target"]}')

st.divider()

# --- 進捗データ ---
sessions = progress.get("sessions") or []

if sessions:
    st.header("📈 進捗")

    # スコア推移
    dates = [s.get("date", "")[:10] for s in sessions]
    accuracies = [s.get("accuracy", 0) * 100 for s in sessions]
    skills = [s.get("skill", "") for s in sessions]

    chart_data = {"日付": dates, "正答率 (%)": accuracies, "スキル": skills}
    st.line_chart(chart_data, x="日付", y="正答率 (%)")

    # スキル別正答率
    skill_scores: dict[str, list[float]] = {}
    for s in sessions:
        skill = s.get("skill", "unknown")
        acc = s.get("accuracy", 0)
        skill_scores.setdefault(skill, []).append(acc)

    st.subheader("スキル別 正答率")
    cols = st.columns(min(len(skill_scores), 4))
    for i, (skill, accs) in enumerate(skill_scores.items()):
        avg = sum(accs) / len(accs) * 100
        with cols[i % len(cols)]:
            st.metric(skill, f"{avg:.0f}%", f"{len(accs)}回")

    # 直近セッション
    st.subheader("直近のセッション")
    for s in reversed(sessions[-10:]):
        acc = s.get("accuracy", 0) * 100
        icon = "🟢" if acc >= 80 else "🟡" if acc >= 60 else "🔴"
        st.text(f'{icon} {s.get("date", "?")} | {s.get("skill", "?")} | {acc:.0f}% ({s.get("questions", 0)}問)')
else:
    st.info("まだセッションデータがありません。`./study` で練習を始めましょう！")

st.divider()

# --- 週次レビュー ---
reviews = progress.get("weekly_reviews") or []
if reviews:
    st.header("📋 週次レビュー")
    for r in reversed(reviews[-5:]):
        with st.expander(f'Week {r.get("week", "?")} — 平均正答率 {r.get("avg_accuracy", 0) * 100:.0f}%'):
            if r.get("strengths"):
                st.success(f'💪 強み: {", ".join(r["strengths"])}')
            if r.get("weaknesses"):
                st.warning(f'📝 弱み: {", ".join(r["weaknesses"])}')
            if r.get("recommendation"):
                st.info(f'💡 {r["recommendation"]}')

st.divider()

# --- 現在のプラン ---
if plan.get("week"):
    st.header("📅 今週のプラン")
    st.caption(f'Week: {plan["week"]} — テーマ: {plan.get("theme", "")}')
    schedule = plan.get("schedule") or {}
    days_jp = {"mon": "月", "tue": "火", "wed": "水", "thu": "木", "fri": "金", "sat": "土", "sun": "日"}
    for day, info in schedule.items():
        if isinstance(info, dict):
            st.text(f'{days_jp.get(day, day)}曜: {info.get("skill", "")} — {info.get("theme", "")} ({info.get("count", "")}問)')

st.divider()

# --- リクエスト ---
if preferences.get("focus") or preferences.get("skip"):
    st.header("⚙️ リクエスト")
    if preferences.get("focus"):
        st.write(f'**重点項目**: {", ".join(preferences["focus"])}')
    if preferences.get("skip"):
        st.write(f'**スキップ**: {", ".join(preferences["skip"])}')
