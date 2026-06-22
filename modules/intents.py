"""
Intent definitions and per-intent question sets.
Each intent has a label, a short description, and a list of question dicts.

Question dict keys:
  key      – session_state key for the answer
  label    – human-readable field name (also used as the column header in files)
  type     – text | email | number | date | select | textarea
  required – bool
  options  – list[str]  (only for type == "select")
"""

INTENTS: dict = {
    "Intent 1": {
        "label": "Intent 1 — Basic Client Registration",
        "description": "Collect essential identity details for a new client.",
        "questions": [
            {"key": "client_name",  "label": "Client Name",  "type": "text",  "required": True},
            {"key": "client_email", "label": "Client Email", "type": "email", "required": True},
            {"key": "company_name", "label": "Company Name", "type": "text",  "required": True},
        ],
    },
    "Intent 2": {
        "label": "Intent 2 — Account Configuration",
        "description": "Set up the client account type and preferences.",
        "questions": [
            {"key": "client_name",  "label": "Client Name",  "type": "text",   "required": True},
            {"key": "client_email", "label": "Client Email", "type": "email",  "required": True},
            {"key": "company_name", "label": "Company Name", "type": "text",   "required": True},
            {"key": "account_type", "label": "Account Type", "type": "select", "required": True,
             "options": ["Basic", "Premium", "Enterprise"]},
        ],
    },
    "Intent 3": {
        "label": "Intent 3 — Service Subscription",
        "description": "Subscribe the client to a service plan and billing cycle.",
        "questions": [
            {"key": "client_name",   "label": "Client Name",   "type": "text",   "required": True},
            {"key": "client_email",  "label": "Client Email",  "type": "email",  "required": True},
            {"key": "company_name",  "label": "Company Name",  "type": "text",   "required": True},
            {"key": "service_plan",  "label": "Service Plan",  "type": "select", "required": True,
             "options": ["Starter", "Growth", "Professional"]},
            {"key": "billing_cycle", "label": "Billing Cycle", "type": "select", "required": True,
             "options": ["Monthly", "Annual"]},
        ],
    },
    "Intent 4": {
        "label": "Intent 4 — Enterprise Onboarding",
        "description": "Onboard an enterprise client with team and contract details.",
        "questions": [
            {"key": "client_name",    "label": "Client Name",         "type": "text",   "required": True},
            {"key": "client_email",   "label": "Client Email",        "type": "email",  "required": True},
            {"key": "company_name",   "label": "Company Name",        "type": "text",   "required": True},
            {"key": "num_users",      "label": "Number of Users",     "type": "number", "required": True},
            {"key": "department",     "label": "Department",          "type": "text",   "required": True},
            {"key": "contract_start", "label": "Contract Start Date", "type": "date",   "required": True},
        ],
    },
    "Intent 5": {
        "label": "Intent 5 — Full Onboarding Suite",
        "description": "Complete onboarding covering all service details and custom requirements.",
        "questions": [
            {"key": "client_name",          "label": "Client Name",          "type": "text",     "required": True},
            {"key": "client_email",         "label": "Client Email",         "type": "email",    "required": True},
            {"key": "company_name",         "label": "Company Name",         "type": "text",     "required": True},
            {"key": "num_users",            "label": "Number of Users",      "type": "number",   "required": True},
            {"key": "department",           "label": "Department",           "type": "text",     "required": True},
            {"key": "contract_start",       "label": "Contract Start Date",  "type": "date",     "required": True},
            {"key": "special_requirements", "label": "Special Requirements", "type": "textarea", "required": False},
        ],
    },
}
