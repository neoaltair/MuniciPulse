"""
Email notification service for CivicFix
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Email configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Send an email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        text_content: Plain text email body (optional)
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    # If SMTP not configured, just log and return True (for development)
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"[EMAIL SIMULATION] To: {to_email}")
        print(f"[EMAIL SIMULATION] Subject: {subject}")
        print(f"[EMAIL SIMULATION] Content: {text_content or html_content[:100]}...")
        return True
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # Add plain text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[EMAIL] Sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {str(e)}")
        return False


def send_report_resolved_notification(
    citizen_email: str,
    citizen_name: str,
    report_title: str,
    report_id: str,
    officer_name: str,
    comment: Optional[str] = None
) -> bool:
    """
    Send notification to citizen when their report is resolved
    
    Args:
        citizen_email: Citizen's email address
        citizen_name: Citizen's full name
        report_title: Title of the resolved report
        report_id: Report ID
        officer_name: Name of the officer who resolved it
        comment: Optional comment from the officer
        
    Returns:
        bool: True if sent successfully
    """
    subject = f"✅ Your Report Has Been Resolved: {report_title}"
    
    # Plain text version
    text_content = f"""
Hello {citizen_name},

Great news! Your report "{report_title}" has been marked as RESOLVED by {officer_name}.

{f"Officer's Comment: {comment}" if comment else ""}

You can view the resolved report and the 'after' photo at:
{FRONTEND_URL}/my-reports

Thank you for helping improve our community!

Best regards,
CivicFix Team
    """.strip()
    
    # HTML version
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                color: white;
                padding: 30px;
                border-radius: 8px 8px 0 0;
                text-align: center;
            }}
            .content {{
                background: #f7fafc;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .badge {{
                display: inline-block;
                background: #c6f6d5;
                color: #22543d;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .comment-box {{
                background: white;
                border-left: 4px solid #48bb78;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                color: #718096;
                padding: 20px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Report Resolved!</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{citizen_name}</strong>,</p>
                
                <p>We have great news! Your report has been resolved:</p>
                
                <div class="badge">✅ RESOLVED</div>
                
                <h3>"{report_title}"</h3>
                
                <p><strong>Resolved by:</strong> {officer_name}</p>
                
                {f'''
                <div class="comment-box">
                    <strong>Officer's Comment:</strong>
                    <p>{comment}</p>
                </div>
                ''' if comment else ''}
                
                <p>You can view the resolved report and see the 'after' photo by visiting your dashboard:</p>
                
                <a href="{FRONTEND_URL}/my-reports" class="btn">View My Reports</a>
                
                <p style="margin-top: 30px;">Thank you for helping improve our community! Your civic engagement makes a difference.</p>
            </div>
            <div class="footer">
                <p>CivicFix - Making Communities Better Together</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(citizen_email, subject, html_content, text_content)


def send_report_status_changed_notification(
    citizen_email: str,
    citizen_name: str,
    report_title: str,
    new_status: str,
    officer_name: str,
    comment: Optional[str] = None
) -> bool:
    """
    Send notification to citizen when report status changes (non-resolved statuses)
    
    Args:
        citizen_email: Citizen's email address
        citizen_name: Citizen's full name
        report_title: Title of the report
        new_status: New status of the report
        officer_name: Name of the officer who changed the status
        comment: Optional comment from the officer
        
    Returns:
        bool: True if sent successfully
    """
    status_emoji = {
        "pending": "⏳",
        "in_progress": "🔧",
        "rejected": "❌"
    }
    
    emoji = status_emoji.get(new_status.lower(), "📋")
    subject = f"{emoji} Status Update: {report_title}"
    
    text_content = f"""
Hello {citizen_name},

Your report "{report_title}" status has been updated to: {new_status.upper()}

Updated by: {officer_name}
{f"Comment: {comment}" if comment else ""}

View your report at:
{FRONTEND_URL}/my-reports

Best regards,
CivicFix Team
    """.strip()
    
    # For non-resolved statuses, send a simpler notification
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;

                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .content {{
                background: #f7fafc;
                padding: 30px;
                border-radius: 8px;
            }}
            .badge {{
                display: inline-block;
                background: #bee3f8;
                color: #2c5282;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h2>{emoji} Status Update</h2>
                <p>Hello <strong>{citizen_name}</strong>,</p>
                <p>Your report status has been updated:</p>
                <h3>"{report_title}"</h3>
                <div class="badge">{new_status.upper()}</div>
                <p><strong>Updated by:</strong> {officer_name}</p>
                {f'<p><strong>Comment:</strong> {comment}</p>' if comment else ''}
                <p><a href="{FRONTEND_URL}/my-reports">View My Reports</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(citizen_email, subject, html_content, text_content)
