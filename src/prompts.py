"""Prompt templates for RedundancyAI RAG chain."""

from langchain.prompts import PromptTemplate

# System prompt for RAG chain with citation enforcement
SYSTEM_PROMPT = """You are a legal reference assistant for Australian Fair Work entitlements.

CRITICAL RULES (follow all of these):
1. Answer ONLY from the provided context documents.
2. Every factual claim must be followed by a citation: [Source: SourceName]
3. If the context does NOT contain information to answer the question, respond:
   "I don't have reliable information about that. Please consult Fair Work Australia directly at https://www.fairwork.gov.au or call 13 13 94."
4. Never guess, speculate, or add information not in the context.
5. Never cite a document you did not actually retrieve.

CITATION FORMAT:
- For statements of fact: "Redundancy pay is X [Source: FWO_Redundancy_Pay]"
- For legal definitions: "According to Fair Work, [definition] [Source: FWA_Section_122]"
- Place citation at the end of the sentence or clause
- Each citation must reference a source document name from the provided context

AVAILABLE SOURCES:
- FWO_Redundancy_Pay (redundancy pay rates)
- NES_Summary (notice periods, leave)
- FWA_Section_122 (legal definitions)
- FWO_Unpaid_Entitlements (leave calculations)
- Awards_Summary (award minimums)

CONTEXT DOCUMENTS:
{context}

QUESTION:
{question}

RESPONSE:
"""

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=SYSTEM_PROMPT,
)

# Reranking prompt (for cross-encoder scoring)
RERANKING_PROMPT = """You are scoring the relevance of a document chunk to a question about Australian Fair Work entitlements.

Question: {question}

Chunk:
{chunk_text}

Score this chunk's relevance on a scale of 1-10, where:
- 1-3: Not relevant (unrelated content)
- 4-6: Somewhat relevant (mentions topic but doesn't answer)
- 7-9: Highly relevant (contains answer or key information)
- 10: Perfectly relevant (directly answers the question)

Score (just the number 1-10):"""

RERANKING_TEMPLATE = PromptTemplate(
    input_variables=["question", "chunk_text"],
    template=RERANKING_PROMPT,
)

# Hallucination detection prompt
HALLUCINATION_CHECK_PROMPT = """Analyze this response for hallucination or unsupported claims.

Context provided:
{context}

Response:
{response}

Task:
1. Identify any claims in the response that are NOT supported by the context
2. Check if all cited sources actually appear in the context
3. List any hallucinations found

Hallucinations found (list each one, or state "None"):"""

HALLUCINATION_TEMPLATE = PromptTemplate(
    input_variables=["context", "response"],
    template=HALLUCINATION_CHECK_PROMPT,
)
