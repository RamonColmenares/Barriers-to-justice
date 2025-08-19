"""
Email service for sending contact form messages via AWS SES
"""
import boto3
import os
from datetime import datetime
from typing import Dict, Optional
from email_validator import validate_email, EmailNotValidError

# Try to import AWS SES, fall back to mock if not available
try:
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    print("⚠️  AWS boto3 not available, falling back to mock mode")
    AWS_AVAILABLE = False
    
    # Mock ClientError for compatibility
    class ClientError(Exception):
        def __init__(self, error_response, operation_name):
            self.response = error_response


class EmailService:
    def __init__(self):
        """Initialize the email service with AWS SES client"""
        try:
            # Initialize SES client
            self.ses_client = boto3.client('ses', region_name='us-east-1')
            
            # Get configuration from environment variables
            self.from_email = os.getenv('CONTACT_EMAIL', 'your-email@example.com')
            # Fixed destination email for all contact form submissions
            self.to_email = 'ramon.colmenaresblanco@gmail.com'
            
            # Verify the email identity exists
            self._verify_email_identity()
            
        except Exception as e:
            print(f"Error initializing email service: {str(e)}")
            self.ses_client = None
    
    def _verify_email_identity(self):
        """Verify that the email identity is configured in SES"""
        try:
            response = self.ses_client.list_identities()
            if self.from_email not in response['Identities']:
                print(f"Warning: Email identity {self.from_email} not verified in SES")
        except Exception as e:
            print(f"Error verifying email identity: {str(e)}")
    
    def validate_contact_data(self, data: Dict) -> tuple[bool, str]:
        """
        Validate contact form data
        
        Args:
            data: Dictionary containing form data
            
        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ['firstName', 'lastName', 'email', 'message']
        
        # Check required fields
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                return False, f"Field '{field}' is required"
        
        # Validate email format
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            return False, "Invalid email address format"
        
        # Validate message length
        if len(data['message'].strip()) < 10:
            return False, "Message must be at least 10 characters long"
        
        if len(data['message'].strip()) > 5000:
            return False, "Message must be less than 5000 characters"
        
        return True, ""

    def send_contact_email(self, form_data: Dict) -> tuple[bool, str]:
        """
        Send contact form email via AWS SES
        
        Args:
            form_data: Dictionary containing contact form data
            
        Returns:
            tuple: (success, message)
        """
        if not self.ses_client:
            return False, "Email service not available"
        
        # Validate form data
        is_valid, error_message = self.validate_contact_data(form_data)
        if not is_valid:
            return False, error_message
        
        try:
            # Prepare email content
            subject = self._create_email_subject(form_data)
            body = self._create_email_body(form_data)
            
            # Send email
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={
                    'ToAddresses': [self.to_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': self._create_html_body(form_data),
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            print(f"Email sent successfully. Message ID: {response['MessageId']}")
            return True, "Message sent successfully"
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"SES Error [{error_code}]: {error_message}")
            
            if error_code == 'MessageRejected':
                return False, "Email could not be sent. Please verify your email address."
            elif error_code == 'SendingPausedException':
                return False, "Email sending is temporarily disabled."
            else:
                return False, "Failed to send email. Please try again later."
        
        except Exception as e:
            print(f"Unexpected error sending email: {str(e)}")
            return False, "An unexpected error occurred. Please try again later."
    
    def _create_email_subject(self, form_data: Dict) -> str:
        """Create email subject line"""
        subject_prefix = form_data.get('subject', 'general')
        name = f"{form_data['firstName']} {form_data['lastName']}"
        
        subject_map = {
            'research': 'Research Collaboration Inquiry',
            'data': 'Data Access Request',
            'media': 'Media Inquiry',
            'policy': 'Policy Discussion',
            'general': 'General Question',
            'other': 'Other Inquiry'
        }
        
        subject_type = subject_map.get(subject_prefix, 'Contact Form Submission')
        return f"[Juvenile Immigration Study] {subject_type} - {name}"
    
    def _create_email_body(self, form_data: Dict) -> str:
        """Create plain text email body"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        body = f"""
Contact Form Submission
{'-' * 30}

Submitted: {timestamp}

Contact Information:
- Name: {form_data['firstName']} {form_data['lastName']}
- Email: {form_data['email']}
- Organization: {form_data.get('organization', 'Not provided')}

Subject Category: {form_data.get('subject', 'Not specified')}

Message:
{form_data['message']}

Newsletter Signup: {'Yes' if form_data.get('newsletter') else 'No'}

---
This message was sent through the Juvenile Immigration Study contact form.
        """.strip()
        
        return body
    
    def _create_html_body(self, form_data: Dict) -> str:
        """Create HTML email body"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Format message to handle line breaks
        formatted_message = form_data['message'].replace('\n', '<br>')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contact Form Submission</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9fafb; padding: 20px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #374151; }}
                .value {{ margin-top: 5px; }}
                .message {{ background-color: white; padding: 15px; border-left: 4px solid #2563eb; margin-top: 10px; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Contact Form Submission</h1>
                    <p>Juvenile Immigration Study</p>
                </div>
                
                <div class="content">
                    <p><strong>Submitted:</strong> {timestamp}</p>
                    
                    <div class="field">
                        <div class="label">Name:</div>
                        <div class="value">{form_data['firstName']} {form_data['lastName']}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value"><a href="mailto:{form_data['email']}">{form_data['email']}</a></div>
                    </div>
                    
                    <div class="field">
                        <div class="label">Organization:</div>
                        <div class="value">{form_data.get('organization', 'Not provided')}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">Subject Category:</div>
                        <div class="value">{form_data.get('subject', 'Not specified')}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">Newsletter Signup:</div>
                        <div class="value">{'Yes' if form_data.get('newsletter') else 'No'}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">Message:</div>
                        <div class="message">{formatted_message}</div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This message was sent through the Juvenile Immigration Study contact form.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Global instance
email_service = EmailService()
