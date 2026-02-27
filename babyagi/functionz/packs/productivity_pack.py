import babyagi
import os
import smtplib
from email.message import EmailMessage
from duckduckgo_search import DDGS

@babyagi.register_function(
    metadata={"description": "Searches the web for real-time information and market insights."}
)
def web_search(query: str, max_results: int = 5):
    """
    Executes a web search and returns the top results.
    """
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            formatted = "\n".join([f"- {r['title']}: {r['href']}\n  {r['body']}" for r in results])
            return formatted if formatted else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

@babyagi.register_function(
    metadata={"description": "Scans the project directory for existing documentation and reports."},
    dependencies=["get_full_directory_contents_cleaned"]
)
def scan_business_docs(directory: str = "."):
    """
    Lists relevant documents in the specified directory.
    """
    try:
        files = [f for f in os.listdir(directory) if f.endswith(('.md', '.txt', '.csv'))]
        if not files:
            return "No relevant business documents found."
    
        return f"Business documents in '{directory}':\n" + "\n".join([f"- {f}" for f in files])
    except Exception as e:
        return f"Disk scan error: {str(e)}"

@babyagi.register_function(
    metadata={"description": "Generates a professional business report or saves important notes."},
)
def write_business_report(filename: str, content: str):
    """
    Writes content to a file in the reports directory.
    """
    try:
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        filepath = os.path.join("reports", filename)
        with open(filepath, "w") as f:
            f.write(content)
        return f"Successfully generated report at: {filepath}"
    except Exception as e:
        return f"Report generation error: {str(e)}"

import requests

@babyagi.register_function(
    metadata={"description": "Triggers an external automation workflow via n8n webhook."},
)
def trigger_n8n_workflow(webhook_url: str, data: dict = None):
    """
    Sends a POST request to an n8n webhook URL to start a workflow.
    Optional 'data' dictionary can be passed as a JSON payload.
    """
    try:
        response = requests.post(webhook_url, json=data or {})
        if response.status_code in [200, 201]:
            return f"n8n Workflow triggered successfully (Status: {response.status_code})."
        else:
            return f"n8n Trigger failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return f"n8n Connection error: {str(e)}"

@babyagi.register_function(
    metadata={"description": "Drafts and sends an email to a specified recipient."},
    key_dependencies=["smtp_email", "smtp_password"]
)
def send_executive_email(recipient: str, subject: str, body: str):
    """
    Sends an email using provided SMTP credentials.
    Note: Requires 'smtp_email' and 'smtp_password' to be set in key_dependencies.
    """
    # In a real scenario, babyagi.get_key('smtp_email') would be used
    # For now, we use placeholders or expect them to be in environment
    smtp_email = os.environ.get("SMTP_EMAIL", "solo-ceo-assistant@example.com")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")

    if not smtp_pass:
        return "Error: SMTP credentials not found. Please configure SMTP_PASSWORD."

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = smtp_email
        msg['To'] = recipient

        # Assuming Gmail for default implementation
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(smtp_email, smtp_pass)
            smtp.send_message(msg)
        
        return f"Email successfully sent to {recipient}."
    except Exception as e:
        return f"Email delivery failed: {str(e)}"
