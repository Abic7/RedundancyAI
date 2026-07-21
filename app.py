"""Streamlit UI for RedundancyAI chatbot."""

import streamlit as st
import logging
from datetime import datetime
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="RedundancyAI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.rag_chain import RAGChain
from src.logger import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# SIDEBAR - Information & Configuration
# ============================================================================

with st.sidebar:
    st.title("⚖️ RedundancyAI")
    st.markdown("---")

    st.subheader("About")
    st.markdown(
        """
        **RedundancyAI** is an open-source chatbot for Australian redundancy
        entitlements. Every answer is verified against Fair Work documents.

        **Current Version:** v1.0 MVP
        """
    )

    st.markdown("---")

    st.subheader("⚠️ Disclaimer")
    st.warning(
        "**NOT Legal Advice** — This is an experimental tool. "
        "Always verify with [Fair Work Australia](https://www.fairwork.gov.au) "
        "or call **13 13 94**."
    )

    st.markdown("---")

    st.subheader("Settings")
    show_debug = st.checkbox("Show debug info", value=False)
    show_sources = st.checkbox("Show source details", value=True)

    st.markdown("---")

    st.subheader("Resources")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("[📚 Fair Work Australia](https://www.fairwork.gov.au)")
    with col2:
        st.markdown("[🐙 GitHub Repo](https://github.com/Abic7/RedundancyAI)")

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ============================================================================
# SESSION STATE - Initialize RAG chain and chat history
# ============================================================================

@st.cache_resource
def load_rag_chain():
    """Load RAG chain once per session."""
    with st.spinner("Loading RAG chain..."):
        try:
            chain = RAGChain()
            return chain, None
        except Exception as e:
            return None, str(e)


# Load chain
chain, error = load_rag_chain()

if error:
    st.error(f"Failed to load RAG chain: {error}")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "responses" not in st.session_state:
    st.session_state.responses = []


# ============================================================================
# MAIN CONTENT - Chat Interface
# ============================================================================

st.title("❓ Ask About Redundancy")
st.markdown(
    "Ask any question about Australian redundancy pay and Fair Work entitlements. "
    "I'll answer using official Fair Work documents."
)

st.markdown("---")

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message("user"):
        st.write(msg)

    if i < len(st.session_state.responses):
        response = st.session_state.responses[i]
        with st.chat_message("assistant"):
            # Main answer
            st.write(response["answer"])

            # Confidence indicator
            confidence = response["confidence"]
            confidence_pct = confidence * 100

            if confidence >= 0.7:
                confidence_color = "🟢"
                confidence_label = "High confidence"
            elif confidence >= 0.4:
                confidence_color = "🟡"
                confidence_label = "Medium confidence"
            else:
                confidence_color = "🔴"
                confidence_label = "Low confidence"

            st.markdown(f"{confidence_color} **Confidence:** {confidence_pct:.0f}%")

            # Source details (optional)
            if show_sources and response["sources"]:
                with st.expander("📖 Sources", expanded=False):
                    for source in response["sources"]:
                        st.markdown(f"**{source['name']}**")
                        if source.get("url"):
                            st.markdown(f"🔗 [{source['url']}]({source['url']})")

            # Injection detection warning
            if response.get("injection_detected"):
                st.warning("⚠️ Potential injection attempt detected in your question.")

            # Hallucination warning
            if response.get("hallucination_detected"):
                st.warning("⚠️ Potential hallucination detected - answer may be unreliable.")

            # Debug info (optional)
            if show_debug:
                with st.expander("🔧 Debug Info", expanded=False):
                    st.json({
                        "confidence": round(confidence, 3),
                        "sources": [s["name"] for s in response["sources"]],
                        "hallucination_detected": response.get("hallucination_detected", False),
                        "injection_detected": response.get("injection_detected", False),
                        "metadata": response.get("metadata", {}),
                    })

        st.markdown("---")


# ============================================================================
# INPUT - Chat input
# ============================================================================

user_input = st.chat_input("Ask a question about redundancy or Fair Work entitlements...")

if user_input:
    # Add to chat history
    st.session_state.messages.append(user_input)

    # Query RAG chain
    with st.spinner("Searching Fair Work documents..."):
        try:
            response = chain.answer_question(user_input)
            st.session_state.responses.append(response)

            # Log the question (hashed for privacy)
            logger.info(f"Question answered: confidence={response['confidence']:.3f}")

            # Rerun to display response
            st.rerun()

        except Exception as e:
            st.error(f"Error processing question: {e}")
            logger.error(f"Query failed: {e}", exc_info=True)
            # Remove the message we just added
            st.session_state.messages.pop()


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
    <p>RedundancyAI v1.0 | Open Source | <a href='https://github.com/Abic7/RedundancyAI'>GitHub</a></p>
    <p>Built with LangChain, Chroma, and Fair Work Australia documents</p>
    </div>
    """,
    unsafe_allow_html=True,
)
