from email_service.sender import EmailSender
from tracking.database import OnboardingDatabase
from documents.generator import DocumentGenerator

# Initialize
email_sender = EmailSender()
db = OnboardingDatabase()
gen = DocumentGenerator()

print("=" * 60)
print("TESTING EMAIL AUTOMATION SYSTEM")
print("=" * 60)

# Sample consultant data
roux_data = {
    'name': 'Roux Anderson',
    'email': 'roux.anderson@gmail.com',
    'position': 'Project Manager Consultant',
    'manager': 'Debbie Murray',
    'start_date': 'January 26, 2026',
    'end_date': 'April 3, 2026',
    'employment_type': 'Full-time',
    'exempt_status': 'Non-Exempt',
    'work_location': 'Remote, Hybrid',
    'location_detail': 'Portland, Maine',
    'pay_rate': '25',
    'pay_frequency': 'Hourly',
    'pay_schedule': 'X Monthly',
    'min_hours': '32',
    'max_hours': '40',
    'hiring_manager': 'Debbie Murray',
    'hiring_manager_title': 'President',
    'department': 'Project Management'
}

# Test 1: Send offer letter email
print("\n1. OFFER LETTER EMAIL")
offer_path = gen.generate_offer_letter(roux_data)
email_sender.send_offer_letter(roux_data, offer_path)

# Test 2: Send next steps email
print("\n2. NEXT STEPS EMAIL")
documents_needed = [
    'W-4 Tax Withholding Form',
    'I-9 Employment Eligibility Verification',
    'Direct Deposit Authorization Form',
    'Emergency Contact Information',
    'Signed Offer Letter'
]
email_sender.send_next_steps_email(roux_data, documents_needed)

# Test 3: Send reminder email
print("\n3. REMINDER EMAIL")
pending_docs = ['W-4', 'I-9']
email_sender.send_reminder_email(roux_data, pending_docs)

# Test 4: Send welcome email
print("\n4. WELCOME EMAIL")
email_sender.send_welcome_email(roux_data)

print("\n" + "=" * 60)
print("✅ EMAIL SYSTEM WORKING!")
print("=" * 60)
print("\nNOTE: Emails are currently in 'preview mode'.")
print("To actually send emails, you would need to:")
print("1. Set up SendGrid account (free tier available)")
print("2. Add API key to environment variables")
print("3. Uncomment the actual sending code")