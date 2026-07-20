import warnings

# Import libraries' custom deprecation warnings if available, else fallback
try:
    from pymilvus import PyMilvusDeprecationWarning
except Exception:
    class PyMilvusDeprecationWarning(Warning):
        pass

# LangChain 0.2 moved this to langchain_core; older versions use langchain
try:
    from langchain_core._api.deprecation import LangChainDeprecationWarning
except Exception:
    try:
        from langchain._api.deprecation import LangChainDeprecationWarning
    except Exception:
        class LangChainDeprecationWarning(Warning):
            pass

# Suppress standard and library-specific deprecations
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
warnings.filterwarnings("ignore", category=PyMilvusDeprecationWarning)

# Optional extra guards (pattern or module-based)
warnings.filterwarnings("ignore", message=".*was deprecated in LangChain.*")
warnings.filterwarnings("ignore", module="langchain_community.vectorstores.milvus")

import streamlit as st
from dotenv import load_dotenv
from utils.answer import stream_answer

warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv(override=True)

# Page configuration
st.set_page_config(
    page_title="DPDT-AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Reduce top padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }

    .main-header {
        text-align: center;
        color: #333;
        margin-top: 0px;
        margin-bottom: 5px;
        font-size: 1.8rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 15px;
        margin-top: 0px;
    }
    .question-box {
        background-color: #e3f2fd;
        padding: 12px;
        border-radius: 10px;
        border-left: 4px solid #2196F3;
        margin-bottom: 20px;
    }
    .question-text {
        color: #1976D2;
        font-weight: 400;
        font-size: 0.95rem;
    }
    .confidence-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-left: 8px;
    }
    .confidence-high {
        background-color: #c8e6c9;
        color: #2e7d32;
    }
    .confidence-medium {
        background-color: #fff9c4;
        color: #f57f17;
    }
    .confidence-low {
        background-color: #ffccbc;
        color: #d84315;
    }
    /* Standardize section headers */
    h3 {
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    /* Make chat message text smaller */
    .stChatMessage {
        font-size: 0.95rem;
    }
    /* Left-align sidebar buttons */
    .stSidebar button {
        text-align: left !important;
        justify-content: flex-start !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources_by_index" not in st.session_state:
    # Store sources for each Q&A pair by index: {0: [docs], 1: [docs], ...}
    st.session_state.sources_by_index = {}
if "confidence_by_index" not in st.session_state:
    # Store confidence scores for each answer by index: {0: 0.85, 1: 0.92, ...}
    st.session_state.confidence_by_index = {}
if "query_analysis_by_index" not in st.session_state:
    # Store query analysis metadata for each answer: {0: {...}, 1: {...}, ...}
    st.session_state.query_analysis_by_index = {}
if "expansion_by_index" not in st.session_state:
    # Store query expansion results for each answer: {0: {...}, 1: {...}, ...}
    st.session_state.expansion_by_index = {}
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "question_answered" not in st.session_state:
    st.session_state.question_answered = True

# Header
st.markdown('<h1 class="main-header">DPDT-AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">DPDT AI Platform</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["💬 Chat", "ℹ️ About"])

with tab2:
    st.markdown("### About DPDT-AI")
    st.markdown("""
    This assistant helps you find information from DPDT documents including:
    - **Best Practices**: Guidelines and standard operating procedures
    - **Developability Assessments**: Candidate evaluation reports
    - **Technical Reports**: Research findings and study results

    #### How to Use
    1. Type your question in the chat input at the bottom
    2. The assistant will retrieve relevant context from the knowledge base
    3. Answers are provided with source documents for verification

    #### Features
    - **Context-based answers**: Only responds using information from uploaded documents
    - **Source citations**: View the exact documents used to generate each answer
    - **Conversation history**: Track your questions and download the full conversation
    - **Recently asked questions**: Quick access to previously asked questions

    #### Knowledge Base
    The assistant has access to technical documents across multiple categories within the Drug Product Development and Technology (DPDT) group at Regeneron.

    #### Important Notes
    - The assistant only answers questions based on the provided knowledge base
    - If information is not available in the documents, the assistant will let you know
    - All answers include source document references for transparency
    """)

with tab1:
    # Display Q&A pairs in an interleaved pattern
    # Q1 (right) -> A1 + Sources (left) -> Q2 (right) -> A2 + Sources (left) -> ...

    q_index = 0
    a_index = 0

    # Determine which messages to display
    # If there's an unanswered question, skip the last user message (it will be shown separately)
    messages_to_display = st.session_state.messages
    if st.session_state.current_question and not st.session_state.question_answered:
        # Find the last user message and don't display it in the loop
        messages_to_display = []
        for msg in st.session_state.messages:
            if msg["role"] == "assistant" or (msg["role"] == "user" and msg["content"] != st.session_state.current_question):
                messages_to_display.append(msg)

    for i, msg in enumerate(messages_to_display):
        if msg["role"] == "user":
            q_index += 1
            # Display question on the right
            col_left_q, col_right_q = st.columns([2, 1])
            with col_right_q:
                st.markdown(f'<div class="question-box"><p class="question-text"><strong>Q{q_index}:</strong> {msg["content"]}</p></div>', unsafe_allow_html=True)
            with col_left_q:
                st.write("")  # Empty space on left

        elif msg["role"] == "assistant":
            a_index += 1
            # Display answer on the left
            col_left_a, col_right_a = st.columns([2, 1])
            with col_left_a:
                # Get confidence score, query analysis, and expansion info for this answer
                confidence = st.session_state.confidence_by_index.get(a_index - 1, None)
                query_analysis = st.session_state.query_analysis_by_index.get(a_index - 1, None)
                expansion = st.session_state.expansion_by_index.get(a_index - 1, None)

                # Format confidence badge
                confidence_html = ""
                if confidence is not None:
                    if confidence >= 0.75:
                        badge_class = "confidence-high"
                        confidence_label = f"High Confidence ({confidence:.2f})"
                    elif confidence >= 0.50:
                        badge_class = "confidence-medium"
                        confidence_label = f"Medium Confidence ({confidence:.2f})"
                    else:
                        badge_class = "confidence-low"
                        confidence_label = f"Low Confidence ({confidence:.2f})"
                    confidence_html = f'<span class="confidence-badge {badge_class}">{confidence_label}</span>'

                # Add query type badge if available
                query_type_html = ""
                if query_analysis and 'query_type' in query_analysis:
                    query_type = query_analysis['query_type'].capitalize()
                    k_used = query_analysis.get('recommended_k', 'N/A')
                    query_type_html = f'<span class="confidence-badge" style="background-color: #e1f5fe; color: #01579b; margin-left: 5px;" title="Retrieved {k_used} documents">{query_type}</span>'

                # Add expansion indicator if query was enhanced
                expansion_html = ""
                if expansion:
                    was_rewritten = expansion.get('was_rewritten', False)
                    has_acronyms = len(expansion.get('acronym_expansions', [])) > 0
                    has_synonyms = len(expansion.get('synonyms_added', [])) > 0

                    if was_rewritten or has_acronyms or has_synonyms:
                        expansion_icon = "🔍"
                        expansion_title = "Query enhanced: "
                        if was_rewritten:
                            expansion_title += "reformulated, "
                        if has_acronyms:
                            expansion_title += f"{len(expansion['acronym_expansions'])} acronyms, "
                        if has_synonyms:
                            expansion_title += f"{len(expansion['synonyms_added'])} synonyms"
                        expansion_title = expansion_title.rstrip(", ")
                        expansion_html = f'<span class="confidence-badge" style="background-color: #f3e5f5; color: #4a148c; margin-left: 5px;" title="{expansion_title}">{expansion_icon} Enhanced</span>'

                st.markdown(f"**A{a_index}:** {confidence_html}{query_type_html}{expansion_html}", unsafe_allow_html=True)
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])

                # Display query expansion details if available
                if expansion and (expansion.get('was_rewritten') or expansion.get('acronym_expansions') or expansion.get('synonyms_added')):
                    with st.expander(f"🔍 Query Enhancement Details for A{a_index}", expanded=False):
                        if expansion.get('was_rewritten'):
                            st.markdown(f"**Original Query:** {expansion['original_query']}")
                            st.markdown(f"**Enhanced Query:** {expansion['expanded_query']}")
                            if expansion.get('rewrite_explanation'):
                                st.info(expansion['rewrite_explanation'])

                        if expansion.get('acronym_expansions'):
                            st.markdown("**Acronyms Expanded:**")
                            for exp in expansion['acronym_expansions']:
                                st.markdown(f"- {exp}")

                        if expansion.get('synonyms_added'):
                            st.markdown("**Synonyms Added:**")
                            st.markdown(f"- {', '.join(expansion['synonyms_added'])}")

                # Display sources for this answer
                if a_index - 1 in st.session_state.sources_by_index:
                    docs = st.session_state.sources_by_index[a_index - 1]
                    if docs:
                        with st.expander(f"📚 Sources for A{a_index} ({len(docs)} found)", expanded=False):
                            for doc in docs:
                                source = doc.metadata.get("source", "unknown")
                                source_filename = source.split("\\")[-1] if "\\" in source else source.split("/")[-1]

                                with st.expander(f"📄 {source_filename}", expanded=False):
                                    st.markdown(f'**Full Path:** `{source}`')
                                    st.markdown("---")
                                    st.markdown(doc.page_content)
                        st.markdown("---")
            with col_right_a:
                st.write("")  # Empty space on right

    # Show current processing question if unanswered
    if st.session_state.current_question and not st.session_state.question_answered:
        col_left_current, col_right_current = st.columns([2, 1])
        with col_right_current:
            st.markdown(f'<div class="question-box"><p class="question-text"><strong>Q{q_index + 1}:</strong> {st.session_state.current_question}</p></div>', unsafe_allow_html=True)
        with col_left_current:
            st.write("")  # Empty space on left

    # Chat input at the bottom
    if prompt := st.chat_input("Ask anything..."):
        # Set the current question
        st.session_state.current_question = prompt
        st.session_state.question_answered = False

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Rerun to show the question at the top right
        st.rerun()

    # Process the current question if there is one and it hasn't been answered yet
    if st.session_state.current_question and not st.session_state.question_answered:
        # Create columns for the streaming answer
        col_left_stream, col_right_stream = st.columns([2, 1])

        with col_left_stream:
            # Show loading spinner
            with st.spinner("🔍 Retrieving relevant information..."):
                # Display assistant response with streaming
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    full_response = ""
                    docs_retrieved = None
                    confidence_score = None
                    query_analysis = None
                    expansion_result = None

                    # Get prior messages (all except the last one)
                    prior_messages = st.session_state.messages[:-1]
                    current_question = st.session_state.messages[-1]["content"]

                    # Stream the response
                    for token, docs, confidence, analysis, expansion in stream_answer(current_question, prior_messages):
                        full_response += token
                        response_placeholder.markdown(full_response + "▌")

                        # Capture the docs, confidence, analysis, and expansion from the first chunk
                        if docs_retrieved is None and docs:
                            docs_retrieved = docs
                            confidence_score = confidence
                            query_analysis = analysis
                            expansion_result = expansion
                            # Calculate the answer index (number of assistant messages so far)
                            answer_index = len([m for m in st.session_state.messages if m["role"] == "assistant"])
                            st.session_state.sources_by_index[answer_index] = docs
                            st.session_state.confidence_by_index[answer_index] = confidence
                            st.session_state.query_analysis_by_index[answer_index] = analysis
                            st.session_state.expansion_by_index[answer_index] = expansion

                    # Final response without cursor
                    response_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Mark question as answered and clear current question
            st.session_state.question_answered = True
            st.session_state.current_question = None
            st.rerun()

        with col_right_stream:
            st.write("")  # Empty space on right
