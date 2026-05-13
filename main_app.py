# Import necessary libraries
import streamlit as st
import PyPDF2
import dspy
import re
import chromadb

# Configure the page settings for the wide dashboard
st.set_page_config(
    page_title="Resume Wrecking Crew",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject dark theme CSS, multi-agent card styles, and yellow spinner text
st.markdown("""
    <style>
    .stApp { background-color: #050508; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    #MainMenu, footer, header {visibility: hidden;}
    h1 {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 900 !important;
        letter-spacing: -2px;
        text-align: left;
        font-size: 3.2rem !important;
        color: #ffffff;
        text-transform: uppercase;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 10px;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: left; color: #60a5fa; font-size: 1rem;
        font-family: 'Courier New', Courier, monospace;
        margin-top: 5px; margin-bottom: 2rem;
    }
    .control-panel {
        background-color: #0a0f1c; padding: 2rem; border-radius: 10px;
        border: 1px solid #1e40af; box-shadow: 0 0 15px rgba(30, 64, 175, 0.2);
    }
    .stSelectbox label { color: #93c5fd !important; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #3b82f6 !important; border-radius: 8px;
        background-color: #0f172a; transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover { background-color: #1e3a8a; border-color: #60a5fa !important; }
    .uploader-header { color: #60a5fa; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 1.2rem; margin-bottom: -10px; margin-top: 10px; }
    .roast-card {
        background-color: #020617; color: #e2e8f0;
        border-top: 4px solid #3b82f6; border-bottom: 4px solid #3b82f6;
        padding: 2.5rem; border-radius: 4px; box-shadow: inset 0 0 20px rgba(59, 130, 246, 0.1);
        font-family: 'Courier New', Courier, monospace; font-size: 1.1rem; line-height: 1.8; margin-top: 2rem; margin-bottom: 2rem;
    }
    .strategy-card {
        background-color: #020617; color: #e2e8f0;
        border-top: 4px solid #10b981; border-bottom: 4px solid #10b981;
        padding: 2.5rem; border-radius: 4px; box-shadow: inset 0 0 20px rgba(16, 185, 129, 0.1);
        font-family: 'Courier New', Courier, monospace; font-size: 1.1rem; line-height: 1.8; margin-top: 1rem; margin-bottom: 2rem;
    }
    .agent-header { color: #10b981; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 1.2rem; margin-bottom: -10px; margin-top: 20px; text-transform: uppercase; }
    .empty-state {
        display: flex; align-items: center; justify-content: center; height: 30vh;
        color: #1e3a8a; font-family: 'Courier New', Courier, monospace; font-size: 1.5rem;
        text-transform: uppercase; border: 1px dashed #1e3a8a; border-radius: 10px; margin-top: 2rem;
    }
    .custom-footer { text-align: left; margin-top: 5rem; font-size: 0.8rem; color: #475569; font-family: 'Courier New', Courier, monospace; }
    .custom-footer a { color: #3b82f6; text-decoration: none; }
    .custom-footer a:hover { color: #93c5fd; }
    .flex-wrapper { display: flex; justify-content: center; align-items: center; width: 100%; }
    .single-chart { width: 150px; }
    .circular-chart { display: block; margin: 10px auto; max-width: 100%; max-height: 250px; }
    .circle-bg { fill: none; stroke: #1e3a8a; stroke-width: 3.8; }
    .circle { fill: none; stroke-width: 2.8; stroke-linecap: round; animation: progress 1s ease-out forwards; }
    .circular-chart.blue .circle { stroke: #ef4444; }
    .percentage { fill: #e2e8f0; font-family: 'Courier New', Courier, monospace; font-size: 0.5em; text-anchor: middle; font-weight: bold; }
    .metric-title { text-align: center; color: #60a5fa; font-family: 'Courier New', Courier, monospace; font-weight: bold; margin-top: 10px; }
    [data-testid="stSpinner"] p {
        color: #facc15 !important;
        font-weight: bold;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize the AI model backend globally
def setup_ai_backend(api_key_str, user_temp):
    text_generator = dspy.LM(model='groq/llama-3.1-8b-instant', api_key=api_key_str, temperature=user_temp)
    return text_generator

# Connect to the local Vector Database
@st.cache_resource(show_spinner=False) # the app should not re-initialize this connection every time the user clicks a button.
def setup_vector_db():
    db_client = chromadb.PersistentClient(path="./resume_vector_db")
    return db_client.get_collection(name="perfect_resume_bullets")

# Load the database
resume_db = setup_vector_db()

# Agent 1: Extracts clean data from the raw PDF text
class ResumeParser(dspy.Signature):
    # The following """ is not a comment, since DSPy will send it to the LLM
    """Extract and structure the core information from a raw, messy resume."""
    raw_text: str = dspy.InputField(desc="The unformatted text extracted directly from the PDF.")
    structured_summary: str = dspy.OutputField(desc="A clean, concise summary of the candidate's Skills, Experience, and Education.")

# Agent 2: Critiques the parsed data based on the selected persona
class ResumeCritic(dspy.Signature):
    # The following """ is not a comment, since DSPy will send it to the LLM
    """You are a harsh resume critic adopting a specific persona to deliver scathing critiques."""
    roaster_persona: str = dspy.InputField(desc="The specific persona and tone the critic must adopt.")
    structured_summary: str = dspy.InputField(desc="The clean summary of the candidate's resume.")
    generated_critique: str = dspy.OutputField(desc="The roast for the resume. DO NOT repeat the persona name. Start immediately with the critique.")
    cliche_density_score: str = dspy.OutputField(desc="Strictly a single number between 0 and 100 representing buzzword usage.")
    actual_impact_score: str = dspy.OutputField(desc="Strictly a single number between 0 and 100 representing actual measurable impact (keep it low).")

# Agent 3: Creates an actionable roadmap using the retrieved RAG database examples
class ResumeStrategist(dspy.Signature):
    # The following """ is not a comment, since DSPy will send it to the LLM
    """Analyze the critic's roast and rewrite the resume using the provided ideal database examples."""
    generated_critique: str = dspy.InputField(desc="The harsh critique provided by the critic agent.")
    structured_summary: str = dspy.InputField(desc="The original structured resume data.")
    ideal_examples: str = dspy.InputField(desc="High-quality, perfect resume bullet points retrieved from the vector database.")
    action_plan: str = dspy.OutputField(desc="A strict, 3-step numbered roadmap to fix the resume's flaws. Give specific examples to help using the ideal_examples as a guide, without refrencing these ideal examples directly.")

# Orchestrate the pipeline and handle the database search
class MultiAgentPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.parser = dspy.ChainOfThought(ResumeParser)
        self.critic = dspy.ChainOfThought(ResumeCritic)
        self.strategist = dspy.ChainOfThought(ResumeStrategist)

    def forward(self, raw_text, roaster_persona, db_collection):
        parsed = self.parser(raw_text=raw_text)
        criticism = self.critic(roaster_persona=roaster_persona, structured_summary=parsed.structured_summary)
        
        # RAG Search: Find the 3 most relevant perfect examples based on the candidate's summary
        # R of RAG: Using semantic search, ChromaDB compares the vectors of the CV against the vectors of the perfect_resume_bullets.
        db_results = db_collection.query(
            query_texts=[parsed.structured_summary],
            n_results=3
        )
        retrieved_examples = "\n".join(db_results['documents'][0])
        
        # Pass everything, including the 3 best chosen database examples, to the Strategist
        strategy = self.strategist(
            generated_critique=criticism.generated_critique, 
            structured_summary=parsed.structured_summary,
            ideal_examples=retrieved_examples # A of RAG
        )
        return criticism, strategy.action_plan

# Helper function to extract numbers from the AI output metrics
def extract_number(score_str):
    match = re.search(r'\d+', str(score_str))
    return int(match.group()) if match else 50

# Create the layout columns for the user interface (SPLIT SCREEN INTO 2 COLUMNS)
col_controls, col_arena = st.columns([1, 2], gap="large")

# Render the Control Panel on the left side
with col_controls:
    st.markdown("<h1>RESUME WRECKING CREW</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Select your nightmare recruiter and brace for impact.</p>", unsafe_allow_html=True)
    
    
    use_custom_prompt = st.toggle("Turn on if you want a custom prompt")
    if use_custom_prompt:
        # Show a multi-line text area for the user to type their own persona
        selected_persona = st.text_area(
            "Enter Custom Interrogator Persona:",
            placeholder="e.g., A Shakespearean actor who speaks in riddles, or a 1920s mafia boss...",
            height=150
        )
    else:
        selected_persona = st.selectbox(
            "Select Interrogator:",
            [
                "The Tech Bro: Obsessed with buzzwords, ultimate developer mindset",
                "The Gordon Ramsay of HR: Aggressive, screams about formatting, calls your experience 'raw'.",
                "The Corporate Speak Master: hides behind corporate jargon."
            ]
        )
    
    creativity_level = st.slider("Creativity Level:", min_value=0, max_value=10, value=5)
    llm_temp = creativity_level / 10.0 # Temperature is between 0 and 1
    
    st.markdown(f"""
        <div class="custom-footer">
            Transforming weak resumes into job-winning powerhouses.<br><br>
            <a href="https://www.linkedin.com/in/samir-alsabbagh-19b315212/" target="_blank">LinkedIn</a>
        </div>
    """, unsafe_allow_html=True)

# Render the Output Arena on the right side
with col_arena:
    st.markdown("<div class='uploader-header'> UPLOAD FILE </div>", unsafe_allow_html=True)
    user_pdf_doc = st.file_uploader(
        label="UPLOAD TARGET FILE (.PDF)", 
        type="pdf", 
        accept_multiple_files=False,
        label_visibility="hidden"
    )
    
    if user_pdf_doc:
        try:
            with st.spinner(f"Initiating Multi-Agent Workflow: Parser → Critic → Strategist..."):
                active_ai_engine = setup_ai_backend(st.secrets["GROQ_API"], llm_temp)
                doc_parser = PyPDF2.PdfReader(user_pdf_doc)
                extracted_text = ''.join([page.extract_text() for page in doc_parser.pages])
                
                # The MultiAgentPipeline class is only executed when the PDF is read (since Streamlit reads the script from top to bottom).
                pipeline = MultiAgentPipeline()
                with dspy.context(lm=active_ai_engine):
                    critic_result, strategy_result = pipeline(raw_text=extracted_text, roaster_persona=selected_persona, db_collection=resume_db)
                
                final_feedback = critic_result.generated_critique
                cliche_val = extract_number(critic_result.cliche_density_score)
                impact_val = extract_number(critic_result.actual_impact_score)
            
            st.markdown(f"""
                <div class="roast-card">
                    {final_feedback}
                </div>
            """, unsafe_allow_html=True)

            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                st.markdown("<div class='metric-title'>CLICHE DENSITY DETECTED</div>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="flex-wrapper">
                      <div class="single-chart">
                        <svg viewBox="0 0 36 36" class="circular-chart blue">
                          <path class="circle-bg"
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                          <path class="circle"
                            stroke-dasharray="{cliche_val}, 100"
                            d="M18 2.0845
                              a 15.9155 15.9155 0 0 1 0 31.831
                              a 15.9155 15.9155 0 0 1 0 -31.831"
                          />
                          <text x="18" y="20.35" class="percentage">{cliche_val}%</text>
                        </svg>
                      </div>
                    </div>
                """, unsafe_allow_html=True)

            with metric_col2:
                st.markdown("<div class='metric-title' style='margin-bottom: 20px;'>ACTUAL IMPACT SHOWCASED</div>", unsafe_allow_html=True)
                st.progress(impact_val, text=f"{impact_val}% Verified Output")

            st.markdown("<div class='agent-header'> The strategist will redeem your resume </div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="strategy-card">
                    {strategy_result}
                </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Something broke. Probably your unreadable formatting: {e}")
    else:
        st.markdown("<div class='empty-state'>[ AWAITING RESUME UPLOAD ]</div>", unsafe_allow_html=True)