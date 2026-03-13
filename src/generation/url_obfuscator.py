import random

def generate_obfuscated_url(original_domain, target_brand=None):
    """
    Generates realistic-looking malicious URLs for research purposes.
    Example: enron.com -> enron-security-portal.net
    """
    tlds = [".net", ".com", ".org", ".info", ".biz", ".co"]
    suffixes = [
        "security-verify",
        "verify-access",
        "login-portal",
        "update-now",
        "compliance-check",
        "internal-support",
        "sso-auth"
    ]
    separators = ["-", ""]
    
    brand = target_brand if target_brand else original_domain.split('.')[0]
    
    style = random.choice(["typo", "subdomain", "suffix"])
    
    if style == "typo":
        # Simple character swap or addition
        chars = list(brand)
        if len(chars) > 3:
            idx = random.randint(0, len(chars)-1)
            chars.insert(idx, chars[idx]) # character doubling
        malicious_domain = "".join(chars)
    elif style == "subdomain":
        malicious_domain = f"{random.choice(suffixes)}.{brand}"
    else: # suffix
        malicious_domain = f"{brand}{random.choice(separators)}{random.choice(suffixes)}"
        
    tld = random.choice(tlds)
    return f"http://{malicious_domain}{tld}/login?id={random.randint(1000, 9999)}"

if __name__ == "__main__":
    # Test
    print(f"Original: enron.com -> Obfuscated: {generate_obfuscated_url('enron.com')}")
    print(f"Original: microsoft.com -> Obfuscated: {generate_obfuscated_url('microsoft.com')}")
