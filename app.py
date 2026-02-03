"""
Solutions PM - Business Manager Dashboard
Streamlit web interface for the onboarding system

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your existing database and document generator
from tracking.database import OnboardingDatabase
from documents.generator import DocumentGenerator

# ============================================
# EMAIL CONFIGURATION
# ============================================
SENDGRID_API_KEY = "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"
FROM_EMAIL = "kelvinrabbles@gmail.com"  # Change this to your official email later

def send_email(to_email, subject, html_content, attachment_path=None):
    """Send email via SendGrid"""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            encoded_file = base64.b64encode(file_data).decode()
        
        attachment = Attachment(
            FileContent(encoded_file),
            FileName(os.path.basename(attachment_path)),
            FileType('application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            Disposition('attachment')
        )
        message.attachment = attachment
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True, response.status_code
    except Exception as e:
        return False, str(e)


def get_offer_email_html(consultant_name, position, start_date, manager):
    """Generate offer letter email HTML"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>Welcome to Solutions Project Management!</h2>
        
        <p>Dear {consultant_name.split()[0]},</p>
        
        <p>We are thrilled to offer you the position of <strong>{position}</strong> at Solutions Project Management, LLC.</p>
        
        <p><strong>Start Date:</strong> {start_date}<br>
        <strong>Reporting To:</strong> {manager}</p>
        
        <p>Please find your official offer letter attached to this email. Review it carefully and let us know if you have any questions.</p>
        
        <p>To accept this offer, please:</p>
        <ol>
            <li>Review the attached offer letter</li>
            <li>Sign and return a copy within 3 business days</li>
            <li>Complete the onboarding documents we'll send separately</li>
        </ol>
        
        <p>We're excited to have you join our team!</p>
        
        <p>Best regards,<br>
        <strong>Solutions Project Management, LLC</strong><br>
        Yarmouth, Maine</p>
    </body>
    </html>
    """


def get_reminder_email_html(consultant_name, pending_docs):
    """Generate reminder email HTML"""
    docs_list = "".join([f"<li>{doc}</li>" for doc in pending_docs])
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>Friendly Reminder: Onboarding Documents</h2>
        
        <p>Dear {consultant_name.split()[0]},</p>
        
        <p>This is a friendly reminder that we're still waiting on the following documents to complete your onboarding:</p>
        
        <ul>
            {docs_list}
        </ul>
        
        <p>Please complete these at your earliest convenience so we can finalize your onboarding process.</p>
        
        <p>If you have any questions, don't hesitate to reach out.</p>
        
        <p>Best regards,<br>
        <strong>Solutions Project Management, LLC</strong></p>
    </body>
    </html>
    """

# Page config
st.set_page_config(
    page_title="Solutions PM - Business Manager",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Headers */
    h1 {
        color: #1e293b !important;
        font-weight: 700 !important;
        margin-bottom: 0.25rem !important;
    }
    
    h2, h3 {
        color: #334155 !important;
        font-weight: 600 !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        padding: 0.5rem 1.25rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #14b8a6, #10b981);
        color: white;
    }
    
    /* Cards / Containers */
    .consultant-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s;
    }
    
    .consultant-card:hover {
        border-color: #14b8a6;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.1);
    }
    
    /* Status badges */
    .badge {
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-pending {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .badge-progress {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .badge-complete {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e2e8f0;
    }
    
    /* Forms */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 0.625rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #14b8a6;
        box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #14b8a6, #10b981);
        border-radius: 9999px;
    }
    
    /* Dividers */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Activity items */
    .activity-item {
        padding: 0.75rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================
# DATABASE CONNECTION
# ============================================
@st.cache_resource
def get_db():
    """Get database connection (cached)"""
    return OnboardingDatabase()


def get_status_badge(status):
    """Return HTML badge for status"""
    if not status:
        status = "Pending"
    
    status_lower = status.lower()
    if "complete" in status_lower:
        return f'<span class="badge badge-complete">{status}</span>'
    elif "progress" in status_lower:
        return f'<span class="badge badge-progress">{status}</span>'
    else:
        return f'<span class="badge badge-pending">{status}</span>'


def format_date(date_val):
    """Format date for display"""
    if not date_val:
        return "—"
    if isinstance(date_val, str):
        return date_val
    return date_val.strftime("%b %d, %Y")


def format_currency(amount):
    """Format as currency"""
    if not amount:
        return "—"
    if isinstance(amount, str):
        amount = amount.replace("$", "").replace(",", "")
        try:
            amount = float(amount)
        except:
            return amount
    return f"${amount:,.0f}"


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 📋 Solutions PM")
    st.markdown("*Business Manager*")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "👥 Consultants", "📧 Emails", "📊 Reports"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    db = get_db()
    summary = db.get_onboarding_summary()
    
    st.markdown("**Quick Stats**")
    st.markdown(f"📊 Total: **{summary['total']}**")
    st.markdown(f"⏳ Pending: **{summary['pending']}**")
    st.markdown(f"🔄 In Progress: **{summary['in_progress']}**")
    st.markdown(f"✅ Complete: **{summary['complete']}**")
    
    st.markdown("---")
    st.markdown("**Kelvin**")
    st.caption("Administrator")


# ============================================
# INITIALIZE SESSION STATE
# ============================================
if "selected_consultant" not in st.session_state:
    st.session_state.selected_consultant = None
if "show_new_form" not in st.session_state:
    st.session_state.show_new_form = False


# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "🏠 Dashboard":
    
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Dashboard")
        st.caption("Welcome back, Kelvin")
    with col2:
        if st.button("➕ New Onboarding", type="primary", use_container_width=True):
            st.session_state.show_new_form = True
            st.session_state.selected_consultant = None
    
    st.markdown("")
    
    # Stats cards
    db = get_db()
    summary = db.get_onboarding_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Consultants", summary['total'])
    with col2:
        st.metric("Pending", summary['pending'])
    with col3:
        st.metric("In Progress", summary['in_progress'])
    with col4:
        st.metric("Complete", summary['complete'])
    
    st.markdown("---")
    
    # Two columns: Recent consultants + Activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Recent Consultants")
        
        consultants = db.get_all_consultants()
        
        if consultants:
            for consultant in consultants[:5]:
                with st.container():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    
                    with c1:
                        st.markdown(f"**{consultant.name}**")
                        st.caption(f"{consultant.position}")
                    
                    with c2:
                        docs = db.get_consultant_documents(consultant.id)
                        if docs:
                            completed = len([d for d in docs if d.status == "Completed"])
                            total = len(docs)
                            progress = completed / total if total > 0 else 0
                            st.progress(progress)
                            st.caption(f"{completed}/{total} documents")
                        else:
                            st.caption("No documents")
                    
                    with c3:
                        st.markdown(get_status_badge(consultant.status), unsafe_allow_html=True)
                        if st.button("View", key=f"dash_view_{consultant.id}", use_container_width=True):
                            st.session_state.selected_consultant = consultant.id
                            st.session_state.show_new_form = False
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No consultants yet. Click **New Onboarding** to add your first consultant!")
    
    with col2:
        st.subheader("Recent Activity")
        
        # Get activities from all consultants
        all_activities = []
        for consultant in consultants[:10]:
            activities = db.get_consultant_activities(consultant.id, limit=3)
            for activity in activities:
                activity.consultant_name = consultant.name
                all_activities.append(activity)
        
        # Sort by timestamp and take top 8
        all_activities.sort(key=lambda x: x.timestamp if x.timestamp else datetime.min, reverse=True)
        
        if all_activities:
            for activity in all_activities[:8]:
                icon = "📧" if "email" in activity.activity_type.lower() else \
                       "📄" if "document" in activity.activity_type.lower() else \
                       "✅" if "complete" in activity.activity_type.lower() else "👤"
                
                st.markdown(f"{icon} **{activity.activity_type}**")
                st.caption(activity.description)
                if activity.timestamp:
                    st.caption(f"_{activity.timestamp.strftime('%b %d, %H:%M')}_")
                st.markdown("")
        else:
            st.info("No activity yet")


# ============================================
# PAGE: CONSULTANTS
# ============================================
elif page == "👥 Consultants":
    db = get_db()
    
    # Check if viewing specific consultant
    if st.session_state.selected_consultant and not st.session_state.show_new_form:
        consultant_id = st.session_state.selected_consultant
        progress = db.get_consultant_progress(consultant_id)
        
        if progress:
            consultant = progress['consultant']
            
            # Back button
            if st.button("← Back to Consultants"):
                st.session_state.selected_consultant = None
                st.rerun()
            
            st.markdown("")
            
            # Header
            col1, col2 = st.columns([4, 1])
            with col1:
                st.title(consultant.name)
                st.caption(f"{consultant.position} • {consultant.email}")
            with col2:
                st.markdown(get_status_badge(consultant.status), unsafe_allow_html=True)
            
            st.markdown("")
            
            # Info cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Salary", format_currency(consultant.pay_rate))
            with col2:
                st.metric("Start Date", format_date(consultant.start_date))
            with col3:
                st.metric("Documents", f"{progress['completed_documents']}/{progress['total_documents']}")
            with col4:
                st.metric("Progress", f"{progress['completion_percentage']:.0f}%")
            
            st.markdown("---")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📄 Generate Docs", type="primary", use_container_width=True):
                    try:
                        # Prepare consultant data for generator
                        generator = DocumentGenerator()
                        consultant_data = {
                            'name': consultant.name,
                            'email': consultant.email,
                            'position': consultant.position,
                            'manager': consultant.manager or 'Debbie Murray',
                            'start_date': consultant.start_date or '',
                            'end_date': consultant.end_date or 'N/A',
                            'employment_type': consultant.employment_type or 'Full-time',
                            'pay_rate': consultant.pay_rate or '',
                        }
                        
                        # Generate offer letter
                        offer_path = generator.generate_offer_letter(consultant_data)
                        
                        # Generate checklist
                        checklist_path = generator.generate_onboarding_checklist(consultant_data)
                        
                        # Update document records in database with file paths
                        docs = db.get_consultant_documents(consultant.id)
                        for doc in docs:
                            if doc.document_type == "Offer Letter":
                                doc.file_path = offer_path
                                doc.status = "Generated"
                                db.session.commit()
                        
                        # Log activity
                        db.log_activity(consultant.id, "Documents Generated", f"Offer letter and checklist created")
                        
                        st.success(f"✅ Documents generated!\n- {offer_path}\n- {checklist_path}")
                        st.rerun()
                    except FileNotFoundError:
                        st.error("❌ Template not found! Make sure offer_letter_template.docx is in documents/templates/")
                    except Exception as e:
                        st.error(f"❌ Error generating documents: {str(e)}")
            with col2:
                if st.button("📧 Send Offer", use_container_width=True):
                    # Check if offer letter exists
                    docs = db.get_consultant_documents(consultant.id)
                    offer_doc = next((d for d in docs if d.document_type == "Offer Letter"), None)
                    
                    if offer_doc and offer_doc.file_path and os.path.exists(offer_doc.file_path):
                        # Send email with attachment
                        html_content = get_offer_email_html(
                            consultant.name,
                            consultant.position,
                            consultant.start_date or "TBD",
                            consultant.manager or "Debbie Murray"
                        )
                        
                        success, result = send_email(
                            to_email=consultant.email,
                            subject=f"Offer Letter - {consultant.position} at Solutions PM",
                            html_content=html_content,
                            attachment_path=offer_doc.file_path
                        )
                        
                        if success:
                            db.update_document_status(offer_doc.id, "Sent")
                            db.log_activity(consultant.id, "Email Sent", f"Offer letter sent to {consultant.email}")
                            st.success(f"✅ Offer letter sent to {consultant.email}!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to send: {result}")
                    else:
                        st.warning("⚠️ Generate documents first before sending!")
            with col3:
                if st.button("⏰ Send Reminder", use_container_width=True):
                    # Get pending documents
                    docs = db.get_consultant_documents(consultant.id)
                    pending_docs = [d.document_type for d in docs if d.status not in ["Completed", "Received"]]
                    
                    if pending_docs:
                        html_content = get_reminder_email_html(consultant.name, pending_docs)
                        
                        success, result = send_email(
                            to_email=consultant.email,
                            subject=f"Reminder: Onboarding Documents Needed - Solutions PM",
                            html_content=html_content
                        )
                        
                        if success:
                            db.log_activity(consultant.id, "Reminder Sent", f"Document reminder sent to {consultant.email}")
                            st.success(f"✅ Reminder sent to {consultant.email}!")
                        else:
                            st.error(f"❌ Failed to send: {result}")
                    else:
                        st.info("No pending documents - nothing to remind about!")
            with col4:
                # Status update dropdown
                new_status = st.selectbox(
                    "Update Status",
                    ["Pending", "In Progress", "Complete"],
                    index=["Pending", "In Progress", "Complete"].index(consultant.status) if consultant.status in ["Pending", "In Progress", "Complete"] else 0,
                    label_visibility="collapsed"
                )
                if new_status != consultant.status:
                    db.update_consultant_status(consultant.id, new_status)
                    st.success(f"Status updated to {new_status}")
                    st.rerun()
            
            st.markdown("---")
            
            # Document checklist
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📋 Document Checklist")
                
                documents = progress['documents']
                
                if documents:
                    for doc in documents:
                        c1, c2, c3 = st.columns([4, 2, 2])
                        
                        with c1:
                            icon = "✅" if doc.status == "Completed" else "⬜"
                            st.markdown(f"{icon} **{doc.document_type}**")
                            if doc.file_path:
                                st.caption(f"📁 {doc.file_path}")
                        
                        with c2:
                            st.markdown(get_status_badge(doc.status), unsafe_allow_html=True)
                        
                        with c3:
                            if doc.status != "Completed":
                                if st.button("Mark Complete", key=f"complete_{doc.id}"):
                                    db.update_document_status(doc.id, "Completed")
                                    st.rerun()
                        
                        st.markdown("")
                else:
                    st.info("No documents tracked yet")
                    
                    # Add standard documents button
                    if st.button("➕ Add Standard Documents"):
                        standard_docs = ["Offer Letter", "Job Description", "W-4", "I-9", "Direct Deposit Form"]
                        for doc_type in standard_docs:
                            db.add_document(consultant.id, doc_type)
                        st.success("Standard documents added!")
                        st.rerun()
            
            with col2:
                st.subheader("📝 Activity Log")
                
                activities = progress['activities']
                
                if activities:
                    for activity in activities[:10]:
                        st.markdown(f"**{activity.activity_type}**")
                        st.caption(activity.description)
                        if activity.timestamp:
                            st.caption(f"_{activity.timestamp.strftime('%b %d, %H:%M')}_")
                        st.markdown("")
                else:
                    st.info("No activity logged")
        
        else:
            st.error("Consultant not found")
            st.session_state.selected_consultant = None
    
    # Show new consultant form
    elif st.session_state.show_new_form:
        if st.button("← Cancel"):
            st.session_state.show_new_form = False
            st.rerun()
        
        st.title("New Consultant Onboarding")
        st.markdown("Enter the consultant's information to start the onboarding process.")
        
        st.markdown("---")
        
        with st.form("new_consultant"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="John Smith")
                email = st.text_input("Email Address *", placeholder="john@example.com")
                position = st.text_input("Position / Role *", placeholder="Senior Consultant")
                manager = st.text_input("Reporting Manager", placeholder="Debbie Smith")
            
            with col2:
                pay_rate = st.text_input("Annual Salary", placeholder="75000")
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date (if contract)", value=None)
                employment_type = st.selectbox(
                    "Employment Type",
                    ["Full-Time Consultant", "Part-Time Consultant", "Contract", "1099 Contractor"]
                )
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                submitted = st.form_submit_button("✅ Start Onboarding", type="primary")
            with col2:
                add_docs = st.form_submit_button("📄 Start + Add Docs")
            
            if submitted or add_docs:
                if name and email and position:
                    consultant_data = {
                        'name': name,
                        'email': email,
                        'position': position,
                        'manager': manager,
                        'pay_rate': pay_rate,
                        'start_date': str(start_date) if start_date else None,
                        'end_date': str(end_date) if end_date else None,
                        'employment_type': employment_type
                    }
                    
                    consultant = db.add_consultant(consultant_data)
                    
                    # Add standard documents if requested
                    if add_docs:
                        standard_docs = ["Offer Letter", "Job Description", "W-4", "I-9", "Direct Deposit Form"]
                        for doc_type in standard_docs:
                            db.add_document(consultant.id, doc_type)
                    
                    st.success(f"✅ {name} added successfully!")
                    st.session_state.show_new_form = False
                    st.session_state.selected_consultant = consultant.id
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (Name, Email, Position)")
    
    # Default: Show consultant list
    else:
        # Header
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("Consultants")
            st.caption("Manage all consultant onboarding")
        with col2:
            if st.button("➕ New", type="primary", use_container_width=True):
                st.session_state.show_new_form = True
                st.rerun()
        
        st.markdown("")
        
        # Filters
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Search by name or position...", label_visibility="collapsed")
        with col2:
            status_filter = st.selectbox("Filter", ["All", "Pending", "In Progress", "Complete"], label_visibility="collapsed")
        
        st.markdown("---")
        
        # Get consultants
        consultants = db.get_all_consultants()
        
        # Apply filters
        if search:
            search_lower = search.lower()
            consultants = [c for c in consultants if search_lower in c.name.lower() or search_lower in (c.position or "").lower()]
        
        if status_filter != "All":
            consultants = [c for c in consultants if c.status == status_filter]
        
        # Display consultants
        if consultants:
            for consultant in consultants:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{consultant.name}**")
                        st.caption(consultant.email)
                    
                    with col2:
                        st.caption("Role")
                        st.markdown(consultant.position or "—")
                    
                    with col3:
                        st.caption("Start Date")
                        st.markdown(format_date(consultant.start_date))
                    
                    with col4:
                        docs = db.get_consultant_documents(consultant.id)
                        if docs:
                            completed = len([d for d in docs if d.status == "Completed"])
                            total = len(docs)
                            st.caption("Documents")
                            st.progress(completed / total if total > 0 else 0)
                            st.caption(f"{completed}/{total}")
                        else:
                            st.caption("Documents")
                            st.markdown("—")
                    
                    with col5:
                        st.markdown(get_status_badge(consultant.status), unsafe_allow_html=True)
                        if st.button("View", key=f"list_view_{consultant.id}", use_container_width=True):
                            st.session_state.selected_consultant = consultant.id
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No consultants found. Add your first consultant to get started!")


# ============================================
# PAGE: EMAILS
# ============================================
elif page == "📧 Emails":
    st.title("Email Management")
    st.caption("Send emails and manage templates")
    
    st.markdown("---")
    
    # Email templates
    st.subheader("Email Templates")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📨 Offer Letter")
        st.markdown("Send the official offer letter with compensation details")
        if st.button("Preview", key="preview_offer", use_container_width=True):
            st.info("Template preview would appear here")
    
    with col2:
        st.markdown("### 📋 Document Request")
        st.markdown("Request completion of onboarding documents")
        if st.button("Preview", key="preview_docs", use_container_width=True):
            st.info("Template preview would appear here")
    
    with col3:
        st.markdown("### ⏰ Reminder")
        st.markdown("Friendly reminder for pending items")
        if st.button("Preview", key="preview_reminder", use_container_width=True):
            st.info("Template preview would appear here")
    
    st.markdown("---")
    
    # Send to specific consultant
    st.subheader("Send Email")
    
    db = get_db()
    consultants = db.get_all_consultants()
    
    if consultants:
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            consultant_names = {c.id: c.name for c in consultants}
            selected_id = st.selectbox(
                "Select Consultant",
                options=list(consultant_names.keys()),
                format_func=lambda x: consultant_names[x]
            )
        
        with col2:
            email_type = st.selectbox(
                "Email Type",
                ["Offer Letter", "Document Request", "Reminder", "Welcome Message"]
            )
        
        with col3:
            st.markdown("")
            st.markdown("")
            if st.button("📤 Send", type="primary", use_container_width=True):
                st.success(f"Email sent to {consultant_names[selected_id]}!")
    else:
        st.info("Add consultants first to send emails")
    
    st.markdown("---")
    
    # Bulk actions
    st.subheader("Bulk Actions")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        bulk_action = st.selectbox(
            "Select action",
            [
                "Send reminder to all with pending documents",
                "Send reminder to all pending > 7 days",
                "Send welcome to all starting this week"
            ],
            label_visibility="collapsed"
        )
    with col2:
        if st.button("📤 Send All", use_container_width=True):
            st.success("Bulk emails sent!")


# ============================================
# PAGE: REPORTS
# ============================================
elif page == "📊 Reports":
    st.title("Reports")
    st.caption("Onboarding analytics and exports")
    
    st.markdown("---")
    
    db = get_db()
    summary = db.get_onboarding_summary()
    consultants = summary['consultants']
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Consultants", summary['total'])
    with col2:
        st.metric("Pending", summary['pending'])
    with col3:
        st.metric("In Progress", summary['in_progress'])
    with col4:
        st.metric("Complete", summary['complete'])
    
    st.markdown("---")
    
    # Status breakdown chart
    st.subheader("Status Breakdown")
    
    if consultants:
        status_data = {
            'Status': ['Pending', 'In Progress', 'Complete'],
            'Count': [summary['pending'], summary['in_progress'], summary['complete']]
        }
        df = pd.DataFrame(status_data)
        st.bar_chart(df.set_index('Status'))
    else:
        st.info("No data to display yet")
    
    st.markdown("---")
    
    # Export section
    st.subheader("Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Consultants (CSV)", use_container_width=True):
            if consultants:
                data = [{
                    'Name': c.name,
                    'Email': c.email,
                    'Position': c.position,
                    'Status': c.status,
                    'Start Date': c.start_date,
                    'Manager': c.manager
                } for c in consultants]
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download CSV",
                    csv,
                    "consultants.csv",
                    "text/csv"
                )
            else:
                st.warning("No consultants to export")
    
    with col2:
        if st.button("📥 Export Documents (CSV)", use_container_width=True):
            all_docs = []
            for c in consultants:
                docs = db.get_consultant_documents(c.id)
                for d in docs:
                    all_docs.append({
                        'Consultant': c.name,
                        'Document': d.document_type,
                        'Status': d.status,
                        'File Path': d.file_path
                    })
            if all_docs:
                df = pd.DataFrame(all_docs)
                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download CSV",
                    csv,
                    "documents.csv",
                    "text/csv"
                )
            else:
                st.warning("No documents to export")
    
    with col3:
        if st.button("📥 Export Activity Log (CSV)", use_container_width=True):
            all_activities = []
            for c in consultants:
                activities = db.get_consultant_activities(c.id, limit=100)
                for a in activities:
                    all_activities.append({
                        'Consultant': c.name,
                        'Activity': a.activity_type,
                        'Description': a.description,
                        'Timestamp': a.timestamp
                    })
            if all_activities:
                df = pd.DataFrame(all_activities)
                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download CSV",
                    csv,
                    "activity_log.csv",
                    "text/csv"
                )
            else:
                st.warning("No activities to export")


# ============================================
# NEW ONBOARDING MODAL (from Dashboard)
# ============================================
if st.session_state.show_new_form and page == "🏠 Dashboard":
    st.markdown("---")
    st.subheader("➕ New Consultant Onboarding")
    
    db = get_db()
    
    with st.form("dashboard_new_consultant"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Smith")
            email = st.text_input("Email *", placeholder="john@example.com")
            position = st.text_input("Position *", placeholder="Senior Consultant")
        
        with col2:
            manager = st.text_input("Manager", placeholder="Debbie Smith")
            pay_rate = st.text_input("Salary", placeholder="75000")
            start_date = st.date_input("Start Date")
        
        employment_type = st.selectbox("Type", ["Full-Time Consultant", "Part-Time Consultant", "Contract"])
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submitted = st.form_submit_button("Start Onboarding", type="primary")
        with col2:
            cancelled = st.form_submit_button("Cancel")
        
        if submitted:
            if name and email and position:
                consultant_data = {
                    'name': name,
                    'email': email,
                    'position': position,
                    'manager': manager,
                    'pay_rate': pay_rate,
                    'start_date': str(start_date),
                    'employment_type': employment_type
                }
                consultant = db.add_consultant(consultant_data)
                
                # Add standard docs
                for doc_type in ["Offer Letter", "Job Description", "W-4", "I-9", "Direct Deposit Form"]:
                    db.add_document(consultant.id, doc_type)
                
                st.success(f"✅ {name} added!")
                st.session_state.show_new_form = False
                st.rerun()
            else:
                st.error("Fill in required fields")
        
        if cancelled:
            st.session_state.show_new_form = False
            st.rerun()
