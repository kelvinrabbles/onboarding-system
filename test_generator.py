from documents.generator import DocumentGenerator

# Sample consultant data - Roux Anderson
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

# Initialize generator - ADD THIS LINE
gen = DocumentGenerator()

# Generate all documents
print("Generating offer letter...")
offer_path = gen.generate_offer_letter(roux_data)
print(f"✓ Offer letter created: {offer_path}")