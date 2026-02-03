import os
from datetime import datetime
from pathlib import Path

class EmailSender:
    def __init__(self):
        """Initialize email sender"""
        self.from_email = "solutionsllc@me.com"
        self.from_name = "Solutions Project Management"
        
    def send_offer_letter(self, consultant_data, offer_letter_path):
        """Send offer letter email"""
        
        subject = f"Offer Letter - {consultant_data['position']} Position"
        
        message = f"""Dear {consultant_data['name'].split()[0]},

Congratulations! Please find attached your offer letter for the position of {consultant_data['position']} at Solutions Project Management, LLC.

Position: {consultant_data['position']}
Start Date: {consultant_data['start_date']}
Manager: {consultant_data.get('manager', 'Debbie Murray')}

Please review the attached offer letter and respond by signing and returning it at your earliest convenience.

If you have any questions, please don't hesitate to reach out.

We look forward to having you join our team!

Best regards,
{consultant_data.get('hiring_manager', 'Debbie Murray')}
{consultant_data.get('hiring_manager_title', 'President')}
Solutions Project Management, LLC
207-776-9259
solutionsllc@me.com"""

        email_log = {
            'to': consultant_data['email'],
            'from': self.from_email,
            'subject': subject,
            'body': message,
            'attachment': offer_letter_path,
            'sent_at': datetime.now(),
            'status': 'Ready to Send'
        }
        
        print(f"\n{'='*60}")
        print(f"EMAIL READY TO SEND")
        print(f"{'='*60}")
        print(f"To: {email_log['to']}")
        print(f"Subject: {email_log['subject']}")
        print(f"\n{email_log['body']}")
        print(f"\nAttachment: {email_log['attachment']}")
        print(f"{'='*60}\n")
        
        return email_log
    
    def send_next_steps_email(self, consultant_data, documents_needed):
        """Send email with next steps and required documents"""
        
        subject = "Next Steps - Onboarding Documents"
        
        docs_list = "\n".join([f"- {doc}" for doc in documents_needed])
        
        message = f"""Dear {consultant_data['name'].split()[0]},

Thank you for accepting our offer! We're excited to have you join Solutions Project Management, LLC.

To complete your onboarding, please submit the following documents by {consultant_data['start_date']}:

{docs_list}

Please reply to this email with the completed documents attached, or let me know if you have any questions.

Looking forward to your start date on {consultant_data['start_date']}!

Best regards,
{consultant_data.get('hiring_manager', 'Debbie Murray')}
{consultant_data.get('hiring_manager_title', 'President')}
Solutions Project Management, LLC
207-776-9259
solutionsllc@me.com"""

        email_log = {
            'to': consultant_data['email'],
            'from': self.from_email,
            'subject': subject,
            'body': message,
            'sent_at': datetime.now(),
            'status': 'Ready to Send'
        }
        
        print(f"\n{'='*60}")
        print(f"EMAIL READY TO SEND")
        print(f"{'='*60}")
        print(f"To: {email_log['to']}")
        print(f"Subject: {email_log['subject']}")
        print(f"\n{email_log['body']}")
        print(f"{'='*60}\n")
        
        return email_log
    
    def send_reminder_email(self, consultant_data, pending_documents):
        """Send reminder for pending documents"""
        
        subject = "Reminder: Onboarding Documents Still Needed"
        
        docs_list = "\n".join([f"- {doc}" for doc in pending_documents])
        
        message = f"""Dear {consultant_data['name'].split()[0]},

This is a friendly reminder that we're still waiting for the following documents to complete your onboarding:

{docs_list}

Your start date is {consultant_data['start_date']}, and we need these documents to ensure everything is ready for your first day.

Please submit these at your earliest convenience by replying to this email.

Thank you!

Best regards,
{consultant_data.get('hiring_manager', 'Debbie Murray')}
{consultant_data.get('hiring_manager_title', 'President')}
Solutions Project Management, LLC
207-776-9259
solutionsllc@me.com"""

        email_log = {
            'to': consultant_data['email'],
            'from': self.from_email,
            'subject': subject,
            'body': message,
            'sent_at': datetime.now(),
            'status': 'Ready to Send'
        }
        
        print(f"\n{'='*60}")
        print(f"EMAIL READY TO SEND")
        print(f"{'='*60}")
        print(f"To: {email_log['to']}")
        print(f"Subject: {email_log['subject']}")
        print(f"\n{email_log['body']}")
        print(f"{'='*60}\n")
        
        return email_log
    
    def send_welcome_email(self, consultant_data):
        """Send welcome email on first day"""
        
        subject = "Welcome to Solutions Project Management!"
        
        message = f"""Dear {consultant_data['name'].split()[0]},

Welcome to your first day at Solutions Project Management, LLC!

We're thrilled to have you join our team as {consultant_data['position']}.

Today's Schedule:
- 9:00 AM: Team introduction meeting
- 10:00 AM: HR orientation
- 11:00 AM: Systems setup
- 12:00 PM: Lunch with your team
- 2:00 PM: Meet with {consultant_data.get('manager', 'your manager')}

If you have any questions or need anything, please don't hesitate to reach out.

Welcome aboard!

Best regards,
{consultant_data.get('hiring_manager', 'Debbie Murray')}
{consultant_data.get('hiring_manager_title', 'President')}
Solutions Project Management, LLC"""

        email_log = {
            'to': consultant_data['email'],
            'from': self.from_email,
            'subject': subject,
            'body': message,
            'sent_at': datetime.now(),
            'status': 'Ready to Send'
        }
        
        print(f"\n{'='*60}")
        print(f"EMAIL READY TO SEND")
        print(f"{'='*60}")
        print(f"To: {email_log['to']}")
        print(f"Subject: {email_log['subject']}")
        print(f"\n{email_log['body']}")
        print(f"{'='*60}\n")
        
        return email_log