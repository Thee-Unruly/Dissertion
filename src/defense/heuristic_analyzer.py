import re
from urllib.parse import urlparse

class HeuristicAnalyzer:
    """
    Analyzes email content for common heuristic phishing indicators.
    """
    
    URGENCY_KEYWORDS = [
        r"urgent", r"immediate", r"action required", r"suspension", r"expired",
        r"unauthorized", r"security alert", r"critical", r"verify your account",
        r"compromised", r"attention", r"failure to comply"
    ]
    
    AUTHORITY_KEYWORDS = [
        r"compliance", r"policy", r"human resources", r"it department",
        r"management", r"strictly prohibited", r"mandatory", r"legal action"
    ]

    def __init__(self, target_domain="enron.com"):
        self.target_domain = target_domain.lower()
        self.brand_name = target_domain.split('.')[0].lower()

    def analyze(self, subject, body):
        """
        Runs multiple heuristic checks and returns a combined score and findings.
        """
        findings = []
        score = 0
        
        # 1. Urgency Detection
        urgency_hits = self._check_keywords(subject + " " + body, self.URGENCY_KEYWORDS)
        if urgency_hits:
            findings.append(f"Urgency/Pressure detected: {', '.join(urgency_hits)}")
            score += min(len(urgency_hits) * 10, 30)
            
        # 2. Authority/Policy Language
        auth_hits = self._check_keywords(body, self.AUTHORITY_KEYWORDS)
        if auth_hits:
            findings.append(f"Authority-based language detected: {', '.join(auth_hits)}")
            score += min(len(auth_hits) * 5, 20)
            
        # 3. Link Analysis
        links = self._extract_links(body)
        for link in links:
            link_score, link_finding = self._analyze_link(link)
            if link_score > 0:
                score += link_score
                findings.append(link_finding)

        # Normalize score (Cap at 100)
        final_score = min(score, 100)
        
        return {
            "score": final_score,
            "risk_level": "High" if final_score >= 70 else "Medium" if final_score >= 30 else "Low",
            "findings": findings
        }

    def _check_keywords(self, text, keywords):
        text = text.lower()
        found = []
        for kw in keywords:
            if re.search(r'\b' + kw + r'\b', text):
                found.append(kw)
        return found

    def _extract_links(self, text):
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

    def _analyze_link(self, link):
        try:
            parsed = urlparse(link)
            domain = parsed.netloc.lower()
            
            # Case 1: Domain is the exact target domain (Likely Safe)
            if domain == self.target_domain or domain.endswith("." + self.target_domain):
                return 0, ""

            # Case 2: Domain contains the brand name but isn't the official domain (SSO/Portal spoofing)
            if self.brand_name in domain:
                return 40, f"Suspicious Link: Domain '{domain}' contains '{self.brand_name}' but is not '{self.target_domain}'"
            
            # Case 3: IP Address as domain
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
                return 50, f"Critical Link: Uses IP address instead of domain: {domain}"
                
            return 10, f"Untrusted Link: External domain detected: {domain}"
        except Exception:
            return 5, "Malformed Link detected"

if __name__ == "__main__":
    # Test
    analyzer = HeuristicAnalyzer(target_domain="enron.com")
    test_body = "URGENT: Your enron account is compromised. Please login at http://enron-security-verify.net/login"
    results = analyzer.analyze("Security Alert", test_body)
    print(f"Score: {results['score']} | Risk: {results['risk_level']}")
    for f in results['findings']:
        print(f" - {f}")
