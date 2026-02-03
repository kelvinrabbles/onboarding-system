from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tracking.models import Base, Consultant, Document, Activity
from datetime import datetime
import os

class OnboardingDatabase:
    def __init__(self, db_path="data/onboarding.db"):
        """Initialize database connection"""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_consultant(self, consultant_data):
        """Add a new consultant to the system"""
        consultant = Consultant(
            name=consultant_data['name'],
            email=consultant_data['email'],
            position=consultant_data['position'],
            manager=consultant_data.get('manager'),
            start_date=consultant_data.get('start_date'),
            end_date=consultant_data.get('end_date'),
            employment_type=consultant_data.get('employment_type'),
            pay_rate=consultant_data.get('pay_rate'),
            status='Pending'
        )
        self.session.add(consultant)
        self.session.commit()
        
        self.log_activity(consultant.id, 'Consultant Added', f'Added {consultant.name} to onboarding system')
        
        return consultant
    
    def get_consultant(self, consultant_id):
        """Get consultant by ID"""
        return self.session.query(Consultant).filter_by(id=consultant_id).first()
    
    def get_all_consultants(self):
        """Get all consultants"""
        return self.session.query(Consultant).all()
    
    def update_consultant_status(self, consultant_id, new_status):
        """Update consultant onboarding status"""
        consultant = self.get_consultant(consultant_id)
        if consultant:
            old_status = consultant.status
            consultant.status = new_status
            consultant.updated_at = datetime.now()
            self.session.commit()
            self.log_activity(consultant_id, 'Status Changed', f'Status changed from {old_status} to {new_status}')
            return consultant
        return None
    
    def add_document(self, consultant_id, document_type, file_path=None, status='Pending'):
        """Add a document to consultant's onboarding"""
        document = Document(
            consultant_id=consultant_id,
            document_type=document_type,
            file_path=file_path,
            status=status
        )
        self.session.add(document)
        self.session.commit()
        
        self.log_activity(consultant_id, 'Document Added', f'{document_type} added')
        
        return document
    
    def update_document_status(self, document_id, new_status):
        """Update document status"""
        document = self.session.query(Document).filter_by(id=document_id).first()
        if document:
            old_status = document.status
            document.status = new_status
            document.updated_at = datetime.now()
            
            if new_status == 'Sent':
                document.sent_date = datetime.now()
            elif new_status == 'Received' or new_status == 'Completed':
                document.received_date = datetime.now()
            
            self.session.commit()
            self.log_activity(document.consultant_id, 'Document Updated', 
                            f'{document.document_type} status: {old_status} → {new_status}')
            return document
        return None
    
    def get_consultant_documents(self, consultant_id):
        """Get all documents for a consultant"""
        return self.session.query(Document).filter_by(consultant_id=consultant_id).all()
    
    def log_activity(self, consultant_id, activity_type, description):
        """Log an activity"""
        activity = Activity(
            consultant_id=consultant_id,
            activity_type=activity_type,
            description=description
        )
        self.session.add(activity)
        self.session.commit()
        return activity
    
    def get_consultant_activities(self, consultant_id, limit=20):
        """Get recent activities for a consultant"""
        return self.session.query(Activity)\
            .filter_by(consultant_id=consultant_id)\
            .order_by(Activity.timestamp.desc())\
            .limit(limit)\
            .all()
    
    def get_onboarding_summary(self):
        """Get summary of all onboarding statuses"""
        consultants = self.get_all_consultants()
        summary = {
            'total': len(consultants),
            'pending': len([c for c in consultants if c.status == 'Pending']),
            'in_progress': len([c for c in consultants if c.status == 'In Progress']),
            'complete': len([c for c in consultants if c.status == 'Complete']),
            'consultants': consultants
        }
        return summary
    
    def get_consultant_progress(self, consultant_id):
        """Get detailed progress for a consultant"""
        consultant = self.get_consultant(consultant_id)
        if not consultant:
            return None
        
        documents = self.get_consultant_documents(consultant_id)
        activities = self.get_consultant_activities(consultant_id)
        
        total_docs = len(documents)
        completed_docs = len([d for d in documents if d.status == 'Completed'])
        
        progress = {
            'consultant': consultant,
            'documents': documents,
            'activities': activities,
            'total_documents': total_docs,
            'completed_documents': completed_docs,
            'completion_percentage': (completed_docs / total_docs * 100) if total_docs > 0 else 0
        }
        
        return progress
    
    def close(self):
        """Close database connection"""
        self.session.close()