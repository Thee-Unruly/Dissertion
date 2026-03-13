from langchain.prompts import PromptTemplate

# --- SPEAR PHISHING ---
SPEAR_PHISHING_PROMPT = """
You are an advanced phishing actor simulating a spear-phishing attack. 
Based on the following target information and tone from real-world samples, 
generate a highly personalized and deceptive email.

Target Name: {target_name}
Organization: {organization}
Target Role: {role}
Topic/Context: {context}
Tone/Urgency Style: {tone_style}

INSTRUCTIONS:
1. ADAPT TONE: 
   - If 'Low Urgency': Be helpful, casual, and non-threatening.
   - If 'High Urgency': Be direct, use time-sensitive language, and stress consequences.
   - If 'Passive-Aggressive': Use professional guilt, 'per my last email' style, and implied authority.
2. Refer to specific project or internal data mentioned in context.
3. Include a call-to-action with a link ({phishing_link}).
4. DO NOT make the phishing too obvious. Use subtle psychological cues.
5. Format:
Subject: [Subject Line]
Body: [Email Body]

Email:
"""

# --- BRAND IMPERSONATION ---
BRAND_IMPERSONATION_PROMPT = """
Simulate a brand impersonation attack targeting users of {brand}.
Mimic the formatting, tone, and common security triggers used by this brand.

Brand: {brand}
Trigger Issue: {trigger_issue} (e.g., Suspicious Login, Account Locked)
Urgency Level: {urgency}
Link: {phishing_link}

INSTRUCTIONS:
1. Use "Official" language style of the brand.
2. Use standardized footers or legal disclaimers often seen in their emails.
3. The goal is to induce immediate action/panic.
4. Format:
Subject: [Subject Line]
Body: [Email Body]

Email:
"""

# --- INTERNAL/HR NOTIFICATIONS ---
INTERNAL_HR_PROMPT = """
Simulate an internal organizational notification (HR, IT, or Payroll).
Ground this in the corporate environment.

Department: {department}
Update Topic: {topic} (e.g., Mandatory Security Training, New Benefits Policy)
Urgency Level: {urgency}
Link: {phishing_link}

INSTRUCTIONS:
1. Use internal corporate jargon.
2. Refer to official 'Employee Handbook' or 'System Migration' processes.
3. Leverage organizational hierarchy or compliance requirements.
4. Format:
Subject: [Subject Line]
Body: [Email Body]

Email:
"""

def get_template(attack_type):
    if attack_type == "spear_phishing":
        return PromptTemplate(
            input_variables=["target_name", "organization", "role", "context", "tone_style", "phishing_link"],
            template=SPEAR_PHISHING_PROMPT
        )
    elif attack_type == "brand_impersonation":
        return PromptTemplate(
            input_variables=["brand", "trigger_issue", "urgency", "phishing_link"],
            template=BRAND_IMPERSONATION_PROMPT
        )
    elif attack_type == "internal_hr":
        return PromptTemplate(
            input_variables=["department", "topic", "urgency", "phishing_link"],
            template=INTERNAL_HR_PROMPT
        )
    else:
        raise ValueError(f"Unknown attack type: {attack_type}")
