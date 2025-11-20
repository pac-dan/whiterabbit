#!/usr/bin/env python3
"""
Environment Variables Validation Script
Run this before deployment to verify all required secrets are configured
"""
import os
import re
from dotenv import load_dotenv

# Load .env file
load_dotenv()


def validate_env():
    """Validate environment variables for production deployment"""
    
    print("=" * 70)
    print("ENVIRONMENT VARIABLES AUDIT")
    print("=" * 70)
    print()
    
    issues = []
    warnings = []
    
    # Required variables
    required_vars = {
        'SECRET_KEY': {
            'description': 'Flask secret key for session security',
            'min_length': 32,
            'example': 'Use: python -c "import secrets; print(secrets.token_hex(32))"'
        },
        'DATABASE_URL': {
            'description': 'Database connection string',
            'pattern': r'^(sqlite:///|mysql\+pymysql://|postgresql://)',
            'example': 'mysql+pymysql://user:pass@localhost:3306/dbname'
        },
        'ANTHROPIC_API_KEY': {
            'description': 'Claude AI API key',
            'pattern': r'^sk-ant-',
            'example': 'Get from https://console.anthropic.com/'
        },
        'MAIL_USERNAME': {
            'description': 'Email address for sending notifications',
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'example': 'support@momentumclips.com'
        },
        'MAIL_PASSWORD': {
            'description': 'Email password or app-specific password',
            'min_length': 8,
            'example': 'Use app-specific password for Gmail'
        },
    }
    
    # Optional but recommended variables
    optional_vars = {
        'RETELL_API_KEY': {
            'description': 'Retell AI voice assistant API key',
            'pattern': r'^key_',
            'example': 'Get from https://beta.retellai.com/'
        },
        'RETELL_AGENT_ID': {
            'description': 'Retell AI agent ID',
            'pattern': r'^agent_',
            'example': 'Get from Retell AI dashboard'
        },
        'RETELL_PUBLIC_KEY': {
            'description': 'Retell AI public key for browser widget',
            'example': 'Public key from Retell AI dashboard'
        },
        'STRIPE_SECRET_KEY': {
            'description': 'Stripe secret key for payments',
            'pattern': r'^(sk_test_|sk_live_)',
            'example': 'Get from https://dashboard.stripe.com/'
        },
        'STRIPE_PUBLISHABLE_KEY': {
            'description': 'Stripe publishable key',
            'pattern': r'^(pk_test_|pk_live_)',
            'example': 'Get from Stripe dashboard'
        },
        'AYRSHARE_API_KEY': {
            'description': 'Ayrshare API key for social media posting',
            'example': 'Get from https://www.ayrshare.com/'
        },
    }
    
    # Placeholders that should not be in production
    dangerous_placeholders = [
        'PLACEHOLDER',
        'CHANGE_THIS',
        'your-email',
        'your-secret-key',
        'dev-secret-key',
        'your_anthropic_api_key_here',
        'your_retell_api_key_here',
        'your-email@gmail.com',
        'your-app-specific-password',
    ]
    
    print("REQUIRED VARIABLES:")
    print("-" * 70)
    
    for var, config in required_vars.items():
        value = os.getenv(var)
        
        if not value:
            issues.append(f"[X] {var}: MISSING - {config['description']}")
            if 'example' in config:
                issues.append(f"   Example: {config['example']}")
        else:
            # Check for placeholders
            if any(placeholder.lower() in value.lower() for placeholder in dangerous_placeholders):
                issues.append(f"[X] {var}: Contains placeholder value")
            # Check minimum length
            elif 'min_length' in config and len(value) < config['min_length']:
                issues.append(f"[X] {var}: Too short (min {config['min_length']} chars)")
            # Check pattern
            elif 'pattern' in config and not re.match(config['pattern'], value):
                issues.append(f"[X] {var}: Invalid format")
                issues.append(f"   Expected: {config.get('example', 'See documentation')}")
            else:
                print(f"[OK] {var}: Configured ({len(value)} chars)")
    
    print()
    print("OPTIONAL VARIABLES:")
    print("-" * 70)
    
    for var, config in optional_vars.items():
        value = os.getenv(var)
        
        if not value:
            warnings.append(f"[!] {var}: Not configured - {config['description']}")
        else:
            # Check for placeholders
            if any(placeholder.lower() in value.lower() for placeholder in dangerous_placeholders):
                warnings.append(f"[!] {var}: Contains placeholder value")
            # Check pattern
            elif 'pattern' in config and not re.match(config['pattern'], value):
                warnings.append(f"[!] {var}: Possibly invalid format")
            else:
                print(f"[OK] {var}: Configured")
    
    print()
    print("OTHER IMPORTANT SETTINGS:")
    print("-" * 70)
    
    # Check Flask environment
    flask_env = os.getenv('FLASK_ENV', 'development')
    if flask_env == 'production':
        print(f"[OK] FLASK_ENV: {flask_env}")
    else:
        warnings.append(f"[!] FLASK_ENV: Set to '{flask_env}' (should be 'production' for deployment)")
    
    # Check Redis URL
    redis_url = os.getenv('REDIS_URL')
    if redis_url and 'localhost' not in redis_url:
        print(f"[OK] REDIS_URL: Configured for production")
    elif redis_url:
        warnings.append(f"[!] REDIS_URL: Contains 'localhost' - update for production")
    else:
        warnings.append(f"[!] REDIS_URL: Not configured")
    
    # Check CORS origins
    cors_origins = os.getenv('CORS_ORIGINS', '')
    if cors_origins and 'localhost' not in cors_origins:
        print(f"[OK] CORS_ORIGINS: Configured for production")
    else:
        warnings.append(f"[!] CORS_ORIGINS: Update with production domain")
    
    # Print summary
    print()
    print("=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    
    if issues:
        print()
        print("CRITICAL ISSUES (must fix before deployment):")
        print()
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print()
        print("WARNINGS (review before deployment):")
        print()
        for warning in warnings:
            print(f"  {warning}")
    
    if not issues and not warnings:
        print()
        print("[OK] ALL CHECKS PASSED!")
        print()
        print("Your environment variables are properly configured for deployment.")
    elif not issues:
        print()
        print("[OK] No critical issues found.")
        print()
        print("Review warnings above and configure optional features as needed.")
    else:
        print()
        print("[ERROR] DEPLOYMENT BLOCKED")
        print()
        print("Fix critical issues above before deploying to production.")
        print()
        return False
    
    print()
    print("=" * 70)
    print()
    
    return len(issues) == 0


if __name__ == '__main__':
    import sys
    success = validate_env()
    sys.exit(0 if success else 1)

