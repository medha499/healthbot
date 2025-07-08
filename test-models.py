# HealthBot: LangGraph + Agentic Retrieval of Patient EHR
# This code builds a LangGraph that identifies a patient via a key pair,
# then answers natural language questions using AI and their structured health data.

from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
import json

# ----------------------------------------
# Step 1: Simulated Database of Patient Records
# ----------------------------------------
# In production, this would be a Redshift query using patient_id + DOB as the lookup key

# ----------------------------------------
# Step 2: LangGraph State Definition
# ----------------------------------------
class PatientState(dict):
    patient_id: str
    dob: str
    question: str
    patient_data: dict
    answer: str

# ----------------------------------------
# Step 3: Tool to Retrieve Patient Record by ID + DOB
# ----------------------------------------
@tool
def get_patient_data(key: str) -> str:
    """Look up a patient's data using 'patient_id|dob' as the key."""
    pid, dob = key.split("|")
    data = patient_db.get((pid, dob))
    if not data:
        return "No patient found with that ID and date of birth."
    return json.dumps(data)

# ----------------------------------------
# Step 4: Tool to Answer Questions Using Patient Record
# ----------------------------------------
@tool
def answer_question_using_ehr(question: str, patient_json: str) -> str:
    """Answer health-related questions from a structured patient EHR record."""
    data = json.loads(patient_json)
    if "medication" in question.lower():
        meds = data.get("medications", [])
        return "\n".join(f"- {m['medication']}" for m in meds) or "No medications found."
    if "condition" in question.lower() or "diagnose" in question.lower():
        conditions = data.get("conditions", [])
        return "\n".join(f"- {c['description']} (onset: {c['onset'][:10]})" for c in conditions) or "No conditions found."
    if "temperature" in question.lower() or "fever" in question.lower():
        obs = [o for o in data.get("observations", []) if o["unit"] == "Cel"]
        return "\n".join(f"{o['value']}°C on {o['effectiveDateTime'][:10]}" for o in obs) or "No temperature records found."
    return "I couldn’t find that in your health record."

# ----------------------------------------
# Step 5: LLM + Agent Setup
# ----------------------------------------
llm = ChatOpenAI(model="gpt-4", temperature=0)
system_msg = SystemMessage(content="You are a helpful assistant who answers health questions using patient records.")
agent = create_tool_calling_agent(llm, [get_patient_data, answer_question_using_ehr], system_msg)
executor = AgentExecutor(agent=agent, tools=[get_patient_data, answer_question_using_ehr], verbose=True)

# ----------------------------------------
# Step 6: LangGraph Nodes
# ----------------------------------------
def load_session(state: PatientState) -> PatientState:
    print("👤 Enter patient_id:")
    state["patient_id"] = input("> ").strip()
    print("📅 Enter date of birth (YYYY-MM-DD):")
    state["dob"] = input("> ").strip()
    return state

def ask_question(state: PatientState) -> PatientState:
    print("💬 Ask a question about your health (e.g., 'What medications am I on?'):")
    state["question"] = input("> ").strip()
    return state

def run_agent(state: PatientState) -> PatientState:
    lookup_key = f"{state['patient_id']}|{state['dob']}"
    ehr_json = get_patient_data(lookup_key)
    if "No patient found" in ehr_json:
        state["answer"] = ehr_json
    else:
        result = executor.invoke({
            "input": state["question"],
            "patient_json": ehr_json
        })
        state["answer"] = result["output"]
    return state

def show_answer(state: PatientState) -> PatientState:
    print(f"\n🤖 HealthBot Answer:\n{state['answer']}")
    print("\n🔁 Would you like to ask another question? (yes/no)")
    if input("> ").strip().lower() != "yes":
        return state
    return ask_question(state)

# ----------------------------------------
# Step 7: LangGraph Setup
# ----------------------------------------
graph = StateGraph(PatientState)
graph.add_node("load_session", load_session)
graph.add_node("ask_question", ask_question)
graph.add_node("run_agent", run_agent)
graph.add_node("show_answer", show_answer)

graph.set_entry_point("load_session")
graph.add_edge("load_session", "ask_question")
graph.add_edge("ask_question", "run_agent")
graph.add_edge("run_agent", "show_answer")
graph.add_edge("show_answer", "run_agent")  # loop for follow-up Qs
graph.add_edge("show_answer", END)

# ----------------------------------------
# Step 8: Launch App
# ----------------------------------------
app = graph.compile()
app.invoke({})
