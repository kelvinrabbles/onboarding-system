from tracking.database import OnboardingDatabase
from documents.generator import DocumentGenerator

# Initialize
db = OnboardingDatabase()
gen = DocumentGenerator()

print("=" * 60)
print("TESTING ONBOARDING TRACKING SYSTEM")
print("=" * 60)

# Test 1: Add Roux to database
print("\n1. Adding Roux Anderson to system...")
roux_data = {
    'name': 'Roux Anderson',
    'email': 'roux.anderson@gmail.com',
    'position': 'Project Manager Consultant',
    'manager': 'Debbie Murray',
    'start_date': 'January 26, 2026',
    'end_date': 'April 3, 2026',
    'employment_type': 'Full-time',
    'pay_rate': '25'
}
roux = db.add_consultant(roux_data)
print(f"✓ Added: {roux.name} (ID: {roux.id})")

# Test 2: Generate documents
print("\n2. Generating documents...")
roux_full_data = {
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
offer_path = gen.generate_offer_letter(roux_full_data)
print(f"✓ Offer letter generated: {offer_path}")

# Test 3: Track documents in database
print("\n3. Adding documents to tracking...")
db.add_document(roux.id, 'Offer Letter', offer_path, status='Sent')
db.add_document(roux.id, 'Job Description', status='Pending')
db.add_document(roux.id, 'W-4', status='Pending')
db.add_document(roux.id, 'I-9', status='Pending')
db.add_document(roux.id, 'Direct Deposit Form', status='Pending')
print("✓ 5 documents added to tracking")

# Test 4: Update consultant status
print("\n4. Updating consultant status...")
db.update_consultant_status(roux.id, 'In Progress')
print(f"✓ Status updated to: In Progress")

# Test 5: Update document status
print("\n5. Simulating document received...")
docs = db.get_consultant_documents(roux.id)
db.update_document_status(docs[0].id, 'Completed')
print("✓ Offer Letter marked as Completed")

# Test 6: View progress
print("\n6. Checking Roux's progress...")
progress = db.get_consultant_progress(roux.id)
print(f"✓ Total documents: {progress['total_documents']}")
print(f"✓ Completed: {progress['completed_documents']}")
print(f"✓ Progress: {progress['completion_percentage']:.0f}%")

# Test 7: View all documents
print("\n7. Document Status:")
for doc in progress['documents']:
    print(f"   - {doc.document_type}: {doc.status}")

# Test 8: View activity log
print("\n8. Recent Activity:")
for activity in progress['activities'][:5]:
    print(f"   [{activity.timestamp.strftime('%Y-%m-%d %H:%M')}] {activity.activity_type}: {activity.description}")

# Test 9: Overall summary
print("\n9. Overall Onboarding Summary:")
summary = db.get_onboarding_summary()
print(f"✓ Total consultants: {summary['total']}")
print(f"✓ Pending: {summary['pending']}")
print(f"✓ In Progress: {summary['in_progress']}")
print(f"✓ Complete: {summary['complete']}")

print("\n" + "=" * 60)
print("✅ DATABASE TRACKING SYSTEM WORKING!")
print("=" * 60)

db.close()