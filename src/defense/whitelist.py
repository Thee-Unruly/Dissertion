"""
Whitelist Manager Module
Manages trusted senders and domains to reduce false positives in phishing detection.
"""

from src.config.detection_config import DETECTION_CONFIG


class WhitelistManager:
    """
    Manages trusted senders and domains to reduce false positives.
    
    Usage:
        whitelist = WhitelistManager()
        if whitelist.is_trusted_sender("boss@enron.com"):
            skip_aggressive_checks = True
    """
    
    def __init__(self, config=None):
        """
        Initialize whitelist with configuration.
        
        Args:
            config: Optional config dict. If None, uses DETECTION_CONFIG
        """
        self.config = config or DETECTION_CONFIG.get("whitelist", {})
        self.trusted_domains = set(
            domain.lower() for domain in self.config.get("trusted_domains", [])
        )
        self.trusted_senders = set(
            sender.lower() for sender in self.config.get("trusted_senders", [])
        )
    
    def is_from_trusted_domain(self, email_address):
        """
        Check if email is from a trusted domain.
        
        Args:
            email_address: Email address string (e.g., "user@enron.com")
            
        Returns:
            True if email is from trusted domain, False otherwise
        """
        if not email_address or "@" not in email_address:
            return False
        
        domain = email_address.split("@")[-1].lower()
        return domain in self.trusted_domains
    
    def is_trusted_sender(self, email_address):
        """
        Check if the exact sender email is in trusted senders list.
        
        Args:
            email_address: Email address string
            
        Returns:
            True if sender is trusted, False otherwise
        """
        return email_address.lower() in self.trusted_senders
    
    def should_skip_aggressive_checks(self, sender):
        """
        Determine if email should skip aggressive heuristic checks.
        
        Emails from trusted senders are still analyzed, but with less aggressive scoring.
        
        Args:
            sender: Sender email address
            
        Returns:
            True if should skip aggressive checks, False otherwise
        """
        return self.is_from_trusted_domain(sender) or self.is_trusted_sender(sender)
    
    def apply_whitelist_reduction(self, risk_score, sender):
        """
        Apply a reduction to risk score if sender is from trusted domain.
        
        Args:
            risk_score: Original risk score (0-100)
            sender: Sender email address
            
        Returns:
            Adjusted risk score
        """
        if self.is_from_trusted_domain(sender):
            # Reduce score by 20% if from trusted domain
            return max(0, int(risk_score * 0.8))
        return risk_score
    
    def add_trusted_domain(self, domain):
        """
        Add a domain to the trusted domains list.
        
        Args:
            domain: Domain to add (e.g., "partner.com")
        """
        self.trusted_domains.add(domain.lower())
    
    def add_trusted_sender(self, email_address):
        """
        Add a sender to the trusted senders list.
        
        Args:
            email_address: Email address to add
        """
        self.trusted_senders.add(email_address.lower())
    
    def remove_trusted_domain(self, domain):
        """Remove a domain from the trusted domains list."""
        self.trusted_domains.discard(domain.lower())
    
    def remove_trusted_sender(self, email_address):
        """Remove a sender from the trusted senders list."""
        self.trusted_senders.discard(email_address.lower())
    
    def get_trusted_domains(self):
        """Return list of all trusted domains."""
        return sorted(list(self.trusted_domains))
    
    def get_trusted_senders(self):
        """Return list of all trusted senders."""
        return sorted(list(self.trusted_senders))
    
    def is_whitelisted(self, email_address):
        """
        Comprehensive check: is this email whitelisted in any way?
        
        Args:
            email_address: Email address to check
            
        Returns:
            True if whitelisted by domain or exact sender, False otherwise
        """
        return self.is_from_trusted_domain(email_address) or self.is_trusted_sender(email_address)


if __name__ == "__main__":
    # Test the whitelist manager
    whitelist = WhitelistManager()
    
    print("=== WHITELIST MANAGER TEST ===\n")
    
    test_emails = [
        "hr@enron.com",
        "user@enron.com",
        "admin@partner.com",
        "attacker@suspicious.com"
    ]
    
    for email in test_emails:
        is_trusted = whitelist.is_whitelisted(email)
        status = "✓ TRUSTED" if is_trusted else "✗ NOT TRUSTED"
        print(f"{email:<30} {status}")
    
    print(f"\nTrusted Domains: {whitelist.get_trusted_domains()}")
    print(f"Trusted Senders: {whitelist.get_trusted_senders()}")
