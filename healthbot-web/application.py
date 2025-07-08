import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import psycopg2
import boto3
from typing import Dict, List

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults

# =============================
# 🌱 ENVIRONMENT VARIABLES
# =============================

load_dotenv("secrets.env")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WORKGROUP_NAME = os.getenv("WORKGROUP_NAME", "healthbot-data")
REGION = os.getenv("AWS_REGION", "us-east-1")

if not TAVILY_API_KEY or not OPENAI_API_KEY:
    st.error("TAVILY_API_KEY and OPENAI_API_KEY must be set in your secrets.env file.")
    st.stop()

st.set_page_config(
    page_title="HealthBot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🩺 HealthBot")
st.markdown("""
Welcome to **HealthBot**, your intelligent health assistant.  
Enter your **Patient ID** to see your health summary, and click any condition or medication for an easy-to-understand explanation.
""")

# =============================
# 🤖 AGENTIC COMPONENTS
# =============================

# 🌟 LLM (GPT-4) setup
llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)

# 🌟 Tavily Search Tool (web search)
tavily_tool = TavilySearchResults(api_key=TAVILY_API_KEY)

# 🌟 Summary chain: generates natural-language patient summary
summary_prompt = PromptTemplate.from_template(
    """
    Patient has the following diagnosed conditions: {conditions}.
    Patient is currently taking: {medications}.
    Summarize this in a short, easy-to-understand way for the patient.
    """
)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

# =============================
# 🗄️ DATABASE FUNCTIONS
# =============================

def get_credentials():
    client = boto3.client("redshift-serverless", region_name=REGION)
    response = client.get_credentials(workgroupName=WORKGROUP_NAME, durationSeconds=900)
    return response["dbUser"], response["dbPassword"]

def get_connection():
    db_user, db_password = get_credentials()
    return psycopg2.connect(
        host='healthbot-data.692859942702.us-east-1.redshift-serverless.amazonaws.com',
        port=5439,
        database='healthbot',
        user=db_user,
        password=db_password,
        sslmode='require',
        connect_timeout=10
    )

def fetch_df(query: str, params=None):
    with get_connection() as conn:
        return pd.read_sql(query, conn, params=params)

@st.cache_data(ttl=300)
def get_patient_record(patient_id: str) -> Dict:
    return {
        "patient": fetch_df("SELECT * FROM patients WHERE id=%s", (patient_id,)),
        "conditions": fetch_df("SELECT description FROM conditions WHERE patient_id=%s", (patient_id,)),
        "medications": fetch_df("SELECT medication AS description FROM medications WHERE patient_id=%s", (patient_id,))
    }

# =============================
# 🔷 AGENTIC FUNCTIONS
# =============================

def get_agentic_explanation(term: str) -> str:
    """
    🌟 Agentic behavior: combines web search + LLM reasoning.
    """
    search_results = tavily_tool.run(f"medical condition {term}")
    explanation = llm.predict(f"Explain this in simple, patient-friendly terms: {search_results}")
    return explanation

def summarize_patient_health(conditions: List[str], medications: List[str]) -> str:
    """
    🌟 Agentic behavior: condenses structured data into a natural summary.
    """
    return summary_chain.run({
        "conditions": ", ".join(conditions),
        "medications": ", ".join(medications)
    }).strip()

# =============================
# 🖥️ UI
# =============================

patient_id = st.text_input("Enter Patient ID")

if st.button("Get My Health Summary") and patient_id:
    with st.spinner("🔄 Fetching your records..."):
        record = get_patient_record(patient_id)
    st.session_state.record = record
    st.session_state.loaded = True

if st.session_state.get("loaded"):
    record = st.session_state.record
    conditions = record['conditions']['description'].tolist()
    medications = record['medications']['description'].tolist()

    st.subheader("📄 Patient Summary")
    summary = summarize_patient_health(conditions, medications)
    st.success(summary)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🩺 Diagnosed Conditions")
        for idx, cond in enumerate(conditions):
            if st.button(f"🔗 {cond}", key=f"cond_{idx}"):
                with st.spinner(f"Explaining {cond}..."):
                    explanation = get_agentic_explanation(cond)
                    st.info(explanation)

    with col2:
        st.subheader("💊 Current Medications")
        for idx, med in enumerate(medications):
            if st.button(f"🔗 {med}", key=f"med_{idx}"):
                with st.spinner(f"Explaining {med}..."):
                    explanation = get_agentic_explanation(med)
                    st.info(explanation)

st.markdown("---")
st.caption("ℹ️ This information is for educational purposes only. Please consult your healthcare provider for medical advice.")
