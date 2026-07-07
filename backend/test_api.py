import asyncio
import os
from analyzer import analyze_url
from gemini_client import generate_fallback_analysis, get_ai_explanation

async def test_analyzer():
    print("Testing URL analyzer...")
    test_urls = [
        "https://google.com",
        "https://paypal-secure-verify.login-check.xyz",
        "http://http-legacy-unsafe.net",
        "https://paypa1-update.xyz/login",
        "https://secure-login-check.top/banking",
        "https://netflix-account-verification.live/login",
        "https://checkout.cloudplaza.io/cz/f2aohaemf?affId=B27ACA03&c1=4",
        "https://flowcode.com/p/PVWkfzw5y?fc=0"
    ]
    
    for url in test_urls:
        print(f"\nScanning: {url}")
        res = await analyze_url(url)
        print(f"Domain: {res['domain']}")
        print(f"HTTPS Enforced: {res['https_enabled']}")
        print(f"Suspicious URL Signatures: {res['suspicious_patterns']}")
        print(f"Calculated Base Trust Score: {res['base_trust_score']}")
        print(f"Crawled Title: {res.get('crawled_page_content', {}).get('title')}")
        print(f"Has Password Field: {res.get('crawled_page_content', {}).get('has_password_field')}")
        print(f"Forms Count: {res.get('crawled_page_content', {}).get('forms_count')}")
        print(f"Inputs Found: {res.get('crawled_page_content', {}).get('input_fields')}")
        print(f"Subpages Scanned: {res.get('crawled_page_content', {}).get('subpages_scanned')}")
        print(f"Scorecard: {res.get('scorecard')}")
        
        # Test fallback response generator
        ai_data = generate_fallback_analysis(res)
        print(f"Calculated Risk Level: {ai_data['risk_level']}")
        print(f"Threat Assessment: {ai_data.get('threat_assessment')}")
        print(f"Ghost Summary: {ai_data['ghost_summary']}")
        print(f"Consequence Stepper (Steps Count): {len(ai_data['consequences'])}")
        
if __name__ == "__main__":
    # Ensure event loop runs properly
    asyncio.run(test_analyzer())
