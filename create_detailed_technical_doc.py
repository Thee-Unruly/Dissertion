from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def set_cell_border(cell, **kwargs):
    """
    Set cell border
    Usage:
    set_cell_border(
        cell,
        top={"sz": 12, "val": "single", "color": "#FF0000", "space": "0"},
        bottom={"sz": 12, "color": "#00FF00", "val": "single"},
        start={"sz": 24, "val": "dashed", "shadow": "true"},
        end={"sz": 12, "val": "none"},
    )
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # check for tag existnace, if not create
    tcBorders = tcPr.find(qn('w:tcBorders'))
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    # list over all available tags
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)

            # check for tag existnace, if not create
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)

            # looks for each of the attributes
            for key in ["sz", "val", "color", "space", "shadow"]:
                if key in edge_data:
                    element.set(qn('w:{}'.format(key)), str(edge_data[key]))

def create_detailed_technical_report():
    doc = Document()
    
    # Custom Styles
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    # Title Page
    title = doc.add_heading('Technical Implementation Specification', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = doc.add_paragraph('PhishDefense AI Hub: A Modular Framework for Adversarial AI Phishing Research')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # Table of Contents (Placeholder)
    doc.add_heading('Table of Contents', level=1)
    doc.add_paragraph('1. System Architecture Overview')
    doc.add_paragraph('2. Offensive Module: Generative Adversarial Engine')
    doc.add_paragraph('3. Defensive Module: Multi-Layered Inspection Pipeline')
    doc.add_paragraph('4. Network Simulation & Gateway Integration')
    doc.add_paragraph('5. Data Ingestion & Persona Modeling')
    doc.add_paragraph('6. User Interface & API Specification')
    doc.add_paragraph('7. Evaluation Framework & Scoring Algorithms')
    doc.add_page_break()

    # Section 1: Architecture
    doc.add_heading('1. System Architecture Overview', level=1)
    doc.add_paragraph(
        "The PhishDefense AI Hub is engineered as a decoupled, modular system implementing the 'Modularized Adversarial "
        "Simulation' (MAS) pattern. The architecture is divided into three primary functional domains: The Offense Domain, "
        "The Defense Domain, and the Orchestration Layer."
    )
    
    doc.add_heading('1.1 Execution Flow', level=2)
    doc.add_paragraph(
        "The system lifecycle follows a 'Sync-Attack-Defend' sequence:\n"
        "1. Ingestion: Historical corporate communication (Enron dataset) is parsed to create behavioral baselines.\n"
        "2. Generation: The Red Team module synthesizes payloads based on extracted personas.\n"
        "3. Transmission: Payloads are physically transmitted via SMTP protocols to a simulated internet gateway (Mailtrap).\n"
        "4. Retrieval: The Blue Team module triggers a network handshake to fetch delivered messages via POP3.\n"
        "5. Detection: Each message is scrutinized through a three-stage pipeline (Heuristic -> Behavioral -> Semantic).\n"
        "6. Evaluation: Metrics are computed by comparing original adversarial intent against detection outcomes."
    )

    # Section 2: Offensive Module
    doc.add_heading('2. Offensive Module: Generative Adversarial Engine', level=1)
    doc.add_paragraph(
        "The Offensive Module (src/generation/) is designed to eliminate the 'uncanny valley' of phishing emails through "
        "context-aware LLM reasoning."
    )

    doc.add_heading('2.1 PhishingGenerator Class Specification', level=2)
    doc.add_paragraph("The primary generator utilizes Llama-3-70B-Versatile via a hardware-accelerated Groq inference engine.")
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Method'
    hdr_cells[1].text = 'Technical Description'
    
    row = table.add_row().cells
    row[0].text = 'generate(type, params)'
    row[1].text = 'Uses LangChain Expression Language (LCEL) to pipe prompts into the LLM. Implements specific tone modifiers (Low/High/PA) to influence the psychological vector of the output.'
    
    doc.add_heading('2.2 URL Obfuscation Algorithms', level=2)
    doc.add_paragraph("The 'url_obfuscator.py' implements a stochastic selection model for link generation:")
    doc.add_paragraph("• Typosquatting Algorithm: Performs character doubling on brand strings (e.g., 'enron' -> 'ennron').", style='List Bullet')
    doc.add_paragraph("• Subdomain Masquerading: Injecting 'compliance-check' or 'sso-auth' as prefixes to legitimate domains.", style='List Bullet')
    doc.add_paragraph("• TLD Hijacking: Randomly selecting from .net, .biz, and .org to mimic corporate infrastructure updates.", style='List Bullet')

    # Section 3: Defensive Module
    doc.add_heading('3. Defensive Module: Multi-Layered Inspection Pipeline', level=1)
    doc.add_paragraph(
        "The Defense Domain (src/defense/) implements a 'Swiss Cheese' security model where multiple weak filters "
        "combine to create a strong detection barrier."
    )

    doc.add_heading('3.1 HeuristicAnalyzer (The Perimeter Layer)', level=2)
    doc.add_paragraph(
        "This component performs regex-based scanning for 30+ indicators of urgency (suspension, action required) "
        "and authority (compliance, policy). It extracts URLs and performs domain-diff analysis between the "
        "sender's claimed brand and the actual resolved link domain."
    )

    doc.add_heading('3.2 BehavioralBaseline (The Context Layer)', level=2)
    doc.add_paragraph(
        "Utilizes a JSON-persisted set of unique (Sender, Recipient) tuples derived from the total Enron dataset. "
        "Any communication between entities without prior history triggers an 'Anomaly Flag', significantly "
        "increasing the risk score of the message."
    )

    doc.add_heading('3.3 LLMClassifier (The Cognitive Layer)', level=2)
    doc.add_paragraph(
        "Performs Deep Semantic Analysis (DSA). The LLM is prompted to identify specific social engineering tactics "
        "like 'Pretexting', 'Quid Pro Quo', and 'Fear-based Manipulation'. It outputs a structured JSON analysis "
        "including a 'Risk Score' (0-100) and specific evidence found in the text."
    )

    # Section 4: Network Gateway
    doc.add_heading('4. Network Simulation & Gateway Integration', level=1)
    doc.add_paragraph(
        "Unlike standard datasets, this system uses physical network bridges. The MailtrapBridge utility implements "
        "the Python smtplib and poplib libraries."
    )
    doc.add_paragraph("• Protocol Fidelity: Emails are transmitted with full MIME headers, including proper From/To/Date fields.", style='List Bullet')
    doc.add_paragraph("• SSL/TLS Handling: Implements secure handshakes on Port 2525 (SMTP) and Port 1100 (POP3) for gateway communication.", style='List Bullet')

    # Section 5: Evaluation Framework
    doc.add_heading('5. Evaluation Framework & Scoring Algorithms', level=1)
    doc.add_paragraph("The system uses an ensemble scoring algorithm to reduce False Positives:")
    
    doc.add_paragraph(
        "Mathematical Model:\n"
        "S_total = (H_score * 0.3) + (B_score * 0.3) + (L_score * 0.4)\n\n"
        "Where:\n"
        "H = Heuristics (Keyword + Link Analysis)\n"
        "B = Behavioral (Communication History)\n"
        "L = LLM reasoning (Semantic Intent)"
    )

    doc.add_paragraph(
        "Status Classification:\n"
        "• ALERT: S_total > 50\n"
        "• QUARANTINE: 30 < S_total < 50\n"
        "• PASS: S_total < 30"
    )

    doc.add_page_break()

    # Save
    report_path = "PhishDefense_Detailed_Technical_Implementation.docx"
    doc.save(report_path)
    print(f"Detailed Report created: {report_path}")

if __name__ == "__main__":
    create_detailed_technical_report()
