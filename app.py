import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

st.set_page_config(
    page_title="AI Customer Support Ticket Analyzer",
    page_icon="🏦",
    layout="centered"
)

st.title("AI Customer Support Ticket Analyzer")
st.write(
    "Analyze banking-related customer support messages by category, sentiment, priority, "
    "summary, escalation need, and suggested response."
)

customer_message = st.text_area(
    "Paste customer support message here:",
    height=180,
    placeholder="Example: I was charged twice this month and nobody has responded to my support ticket."
)

system_prompt = """
You are an AI assistant for a bank or credit union customer support team.

Analyze the customer support message and return your answer ONLY as valid JSON.

Use this exact JSON structure:
{
  "category": "",
  "sentiment": "",
  "priority": "",
  "escalation_needed": "",
  "summary": "",
  "suggested_response": ""
}

Rules:
- Category must be one of: Billing, Fraud, Account Access, Card Issue, Loan, Mobile App, Customer Service, Other.
- Sentiment must be one of: Positive, Neutral, Negative.
- Priority must be one of: Low, Medium, High.
- Escalation_needed must be one of: Yes, No.
- Summary should be 1 to 2 sentences.
- Suggested_response should sound professional, empathetic, and appropriate for a financial institution.
- Do not include legal, financial, or account-specific advice.
- Do not claim that you personally escalated, resolved, investigated, refunded, or changed anything. Use wording like "This issue should be escalated" instead of "I will escalate this."
"""

def analyze_ticket(message: str) -> dict:
    response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ],
)

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "category": "Error",
            "sentiment": "Error",
            "priority": "Error",
            "escalation_needed": "Error",
            "summary": "The AI response could not be parsed as JSON.",
            "suggested_response": content
        }

if st.button("Analyze Ticket"):
    if not customer_message.strip():
        st.warning("Please enter a customer support message first.")
    else:
        with st.spinner("Analyzing ticket..."):
            try:
                result = analyze_ticket(customer_message)

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Category", result.get("category", "N/A"))
                col2.metric("Sentiment", result.get("sentiment", "N/A"))
                col3.metric("Priority", result.get("priority", "N/A"))
                col4.metric("Escalation", result.get("escalation_needed", "N/A"))

                st.subheader("Summary")
                st.write(result.get("summary", "N/A"))

                st.subheader("Suggested Customer Response")
                st.write(result.get("suggested_response", "N/A"))

                with st.expander("View Raw JSON"):
                    st.json(result)

            except Exception as e:
                st.error("Something went wrong. Check your Azure endpoint, API key, deployment name, and API version.")
                st.code(str(e))