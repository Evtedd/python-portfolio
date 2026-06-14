import httpx
import streamlit as st

from app.config import settings

st.set_page_config(page_title="Resume Matcher", layout="wide")
st.title("Resume & Vacancy Matcher")

api_url = settings.api_url.rstrip("/")

with st.sidebar:
    st.header("Статистика")
    try:
        stats = httpx.get(f"{api_url}/stats", timeout=10).json()
        st.metric("Анализов", stats["total_matches"])
        st.metric("Средний match", f"{stats['average_score']}%")
        st.metric("Откликов", stats["applied_count"])
    except httpx.HTTPError:
        st.warning("API недоступен")

resume = st.file_uploader("Резюме PDF или TXT", type=["pdf", "txt"])
vacancy_input = st.text_input("Ссылка или id вакансии HH")
vacancy_text = st.text_area("Или текст вакансии", height=220)

if st.button("Оценить соответствие", type="primary") and resume:
    files = {"resume": (resume.name, resume.getvalue(), resume.type or "text/plain")}
    data = {"vacancy_input": vacancy_input, "vacancy_text": vacancy_text}
    response = httpx.post(f"{api_url}/match", files=files, data=data, timeout=60)
    if response.status_code >= 400:
        st.error(response.json().get("detail", "Ошибка анализа"))
    else:
        result = response.json()
        st.metric("Match", f"{result['score']}%")
        st.write(result["reasoning"])
        st.subheader("Совпавшие навыки")
        st.write(", ".join(result["matched_skills"]) or "Нет")
        st.subheader("Чего не хватает")
        st.write(", ".join(result["missing_skills"]) or "Нет")
        st.subheader("Сопроводительное письмо")
        st.write(result["cover_letter"])
        st.checkbox("Удалёнка", value=result["is_remote"], disabled=True)
        st.checkbox("Подозрительная вакансия", value=result["is_suspicious"], disabled=True)

st.subheader("История")
try:
    matches = httpx.get(f"{api_url}/matches", timeout=10).json()
    for item in matches[:20]:
        st.write(f"#{item['id']}: {item['score']}%: {item['created_at']}")
except httpx.HTTPError:
    st.info("История появится после запуска API.")
