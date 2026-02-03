from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Consultant(Base):
    """Consultant being onboarded"""
    __tablename__ = 'consultants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    position = Column(String, nullable=False)
    manager = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    employment_type = Column(String)
    pay_rate = Column(String)
    status = Column(String, default='Pending')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    documents = relationship("Document", back_populates="consultant")
    
    def __repr__(self):
        return f"<Consultant(name='{self.name}', position='{self.position}', status='{self.status}')>"


class Document(Base):
    """Documents in the onboarding process"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    consultant_id = Column(Integer, ForeignKey('consultants.id'))
    document_type = Column(String, nullable=False)
    file_path = Column(String)
    status = Column(String, default='Pending')
    sent_date = Column(DateTime)
    received_date = Column(DateTime)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    consultant = relationship("Consultant", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(type='{self.document_type}', status='{self.status}')>"


class Activity(Base):
    """Activity log for tracking all onboarding events"""
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    consultant_id = Column(Integer, ForeignKey('consultants.id'))
    activity_type = Column(String, nullable=False)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Activity(type='{self.activity_type}', time='{self.timestamp}')>"