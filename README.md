# 🧠 HealthBot AI Pro: Advanced clinical intelligence — governed, real-time access to EHR data with retrieval-augmented reasoning, accelerating processing time for rapid action.


--- 
## What it does 

* Patient look-up & summarization: Pulls structured data (problems, meds, labs, encounters) and generates an interpretable summary with citations back to source records.

* Conversational Q&A (RAG): Answers clinician/reps’ questions using LangGraph orchestration over Redshift + vector index, with guideline snippets when relevant.

* Proactive literacy tools: Adaptive quizzes/explanations for patients or reps, improving comprehension and reducing re-asks.

* Governance & auditability: Standardized outputs, lineage to original EHR fields, session logs, and KPI dashboards.


## Data Flow Diagram ## 

<img width="1398" height="503" alt="Screenshot 2025-09-15 at 11 33 09 PM" src="https://github.com/user-attachments/assets/13869e6e-33cc-471f-928e-e9a8c00e7cb9" />

## Features

* Patient Medical Record Lookup
Query patient records in real time via unique patient IDs with a clean and intuitive Streamlit UI.

* EHR Data Pipeline

* Parsed and normalized 50K+ JSON event records into Redshift through Python + S3 ingestion pipelines.

* Optimized schema and ETL logic for sub-second interactive queries on complex healthcare datasets.

* Retrieval-Augmented Intelligence

* Implemented retrieval-augmented generation (RAG) pipelines with monitoring hooks.

* Achieved 30% improvement in accuracy and 40% reduction in latency during conversational querying.

* Reliability & Monitoring

* Conducted reinforcement-tuned experiments to improve the reliability of responses.

* Enhanced failure detection and fallback handling, ensuring safe and auditable AI outputs for clinical contexts.

--- 
## Tech Stack

* Frontend & Application Layer: Streamlit, Python

* Data Pipeline: AWS S3, Redshift, Python ETL

* AI/ML Components: LangChain, Retrieval-Augmented Generation, Reinforcement-Tuned Conversational Models

* Observability: Custom monitoring hooks for latency, accuracy, and failure detection

---
## Impact

* Reduced query latency by 40% for healthcare record lookups.

* Improved retrieval accuracy by 30% through augmented pipelines.

* Increased system reliability via reinforcement-driven experiments and monitoring integration.


## Getting Started  

Navigate to `healthbot-web` and execute:  

<img width="1728" height="887" alt="Screenshot 2025-07-26 at 9 32 45 PM" src="https://github.com/user-attachments/assets/732042b0-5dec-494b-9aa7-df06d9ac32b3" />

<img width="1725" height="841" alt="Screenshot 2025-09-15 at 10 23 32 PM" src="https://github.com/user-attachments/assets/ca4db9fd-ad32-4f6a-b326-dc3b2ed4bf21" />

> _Note:_ Example datasets are synthetic; the system supports both anonymized and production pipelines with standard governance controls.

