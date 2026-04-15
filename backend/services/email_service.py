"""
Terra Pravah - Email Service
=============================
Email notifications and templates.
"""

from flask import current_app, render_template_string
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Send an email.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content
        text_content: Plain text content (optional)
    """
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT', 587)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@terrapravah.com')
    
    if not mail_server or not mail_username:
        current_app.logger.warning("Email not configured, skipping send")
        return
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = mail_sender
    msg['To'] = to_email
    
    if text_content:
        part1 = MIMEText(text_content, 'plain')
        msg.attach(part1)
    
    part2 = MIMEText(html_content, 'html')
    msg.attach(part2)
    
    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.sendmail(mail_sender, to_email, msg.as_string())
            
        current_app.logger.info(f"Email sent to {to_email}")
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        raise


def send_verification_email(user):
    """Send email verification link."""
    # Generate verification token (implement proper token generation)
    token = "placeholder_verification_token"
    
    verification_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; padding: 20px 0; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 8px; }}
            .button {{ display: inline-block; background: #4ade80; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Terra Pravah</div>
            </div>
            <div class="content">
                <h2>Verify Your Email</h2>
                <p>Hi {user.first_name or 'there'},</p>
                <p>Thank you for signing up for Terra Pravah! Please verify your email address by clicking the button below:</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{verification_url}</p>
                <p>This link will expire in 24 hours.</p>
            </div>
            <div class="footer">
                <p>© {datetime.now().year} Terra Pravah. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(
        to_email=user.email,
        subject="Verify your Terra Pravah account",
        html_content=html
    )


def send_password_reset_email(user):
    """Send password reset link."""
    # Generate reset token (implement proper token generation)
    token = "placeholder_reset_token"
    
    reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; padding: 20px 0; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 8px; }}
            .button {{ display: inline-block; background: #4ade80; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Terra Pravah</div>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>Hi {user.first_name or 'there'},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>© {datetime.now().year} Terra Pravah. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(
        to_email=user.email,
        subject="Reset your Terra Pravah password",
        html_content=html
    )


def send_analysis_complete_email(user, project, results):
    """Send notification when analysis is complete."""
    project_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/projects/{project.id}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; padding: 20px 0; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 8px; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat {{ text-align: center; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
            .stat-label {{ font-size: 12px; color: #666; }}
            .button {{ display: inline-block; background: #4ade80; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Terra Pravah</div>
            </div>
            <div class="content">
                <h2>✅ Analysis Complete</h2>
                <p>Hi {user.first_name or 'there'},</p>
                <p>Great news! The drainage analysis for <strong>{project.name}</strong> has been completed successfully.</p>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{results.get('total_channels', 0)}</div>
                        <div class="stat-label">Channels</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{results.get('total_length_km', 0):.1f} km</div>
                        <div class="stat-label">Network Length</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{results.get('total_outlets', 0)}</div>
                        <div class="stat-label">Outlets</div>
                    </div>
                </div>
                
                <p style="text-align: center;">
                    <a href="{project_url}" class="button">View Results</a>
                </p>
            </div>
            <div class="footer">
                <p>© {datetime.now().year} Terra Pravah. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(
        to_email=user.email,
        subject=f"Analysis Complete: {project.name}",
        html_content=html
    )


def send_project_shared_email(recipient_user, shared_by_user, project, permission):
    """Send notification when a project is shared."""
    project_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/projects/{project.id}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; padding: 20px 0; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 8px; }}
            .button {{ display: inline-block; background: #4ade80; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Terra Pravah</div>
            </div>
            <div class="content">
                <h2>Project Shared With You</h2>
                <p>Hi {recipient_user.first_name or 'there'},</p>
                <p><strong>{shared_by_user.full_name}</strong> has shared a project with you:</p>
                <div style="background: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="margin: 0 0 5px 0;">{project.name}</h3>
                    <p style="margin: 0; color: #666;">{project.description or 'No description'}</p>
                    <p style="margin: 10px 0 0 0;"><strong>Your access level:</strong> {permission.capitalize()}</p>
                </div>
                <p style="text-align: center;">
                    <a href="{project_url}" class="button">View Project</a>
                </p>
            </div>
            <div class="footer">
                <p>© {datetime.now().year} Terra Pravah. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(
        to_email=recipient_user.email,
        subject=f"{shared_by_user.full_name} shared a project with you",
        html_content=html
    )
