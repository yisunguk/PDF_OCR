import os
from datetime import datetime
import streamlit as st
import fitz  # PyMuPDF
import pdfplumber  # pdfplumber 기반 텍스트 추출용

st.set_page_config(page_title="PDF 텍스트 추출기", layout="centered")
st.title("📄 PDF 텍스트 추출기(페이지별 Json 변환))")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for k, v in {"timestamp": None, "json_path": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])
extract_method = st.selectbox("텍스트 추출 방식 선택", ["PyMuPDF", "pdfplumber"])

if uploaded_file:
    if not st.session_state.timestamp:
        st.session_state.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    temp_pdf = os.path.join(BASE_DIR, f"temp_{st.session_state.timestamp}.pdf")
    with open(temp_pdf, "wb") as f:
        f.write(uploaded_file.getbuffer())

    filename_base = os.path.splitext(uploaded_file.name)[0]
    json_path = os.path.join(BASE_DIR, "output", "json",
                             f"{filename_base}_text_result_{st.session_state.timestamp}.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    if st.button("🚀 텍스트 추출 실행"):
        try:
            st.info("텍스트 추출 중…")

            result = {
                "pdf_path": temp_pdf,
                "pages": []
            }

            if extract_method == "PyMuPDF":
                doc = fitz.open(temp_pdf)
                for i, page in enumerate(doc):
                    text = page.get_text().strip()
                    result["pages"].append({
                        "page_number": i + 1,
                        "char_count": len(text),
                        "text": text
                    })
                doc.close()

            else:  # pdfplumber
                doc = pdfplumber.open(temp_pdf)
                for i, page in enumerate(doc.pages):
                    text = page.extract_text() or ""
                    result["pages"].append({
                        "page_number": i + 1,
                        "char_count": len(text),
                        "text": text
                    })
                doc.close()

            with open(json_path, "w", encoding="utf-8") as f:
                import json
                json.dump(result, f, ensure_ascii=False, indent=2)

            st.success("완료! 결과 JSON 생성됨.")
            with open(json_path, "rb") as f:
                st.download_button("📥 결과 JSON 다운로드", f, file_name=os.path.basename(json_path),
                                   mime="application/json")
            st.session_state.json_path = json_path

        except Exception as e:
            st.error(f"실패: {e}")

if st.session_state.json_path:
    st.info("최근 생성된 결과 JSON")
    st.code(st.session_state.json_path)
