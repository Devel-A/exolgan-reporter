import requests
import logging
import base64
from typing import List, Dict, Any, Optional, Union
from datetime import datetime


def send_email_with_attachment(recipients: List[Dict[str, str]], excel_attachment: bytes, config: Dict[str, str]) -> bool:
    """
    Sends an email with Excel attachment using the ZeptoMail HTTP API.
    
    Args:
        recipients (List[Dict[str, str]]): A list of dictionaries containing recipient information.
            Each dictionary should have at least 'email' key.
            Example: [{'email': 'user1@example.com', 'name': 'User 1'}, {'email': 'user2@example.com'}]
        excel_attachment (bytes): The Excel file as bytes to be attached to the email.
        config (Dict[str, str]): Configuration parameters for ZeptoMail API.
            Required keys: 'api_url', 'api_key', 'from_email', 'from_name', 'subject'
    
    Returns:
        bool: True if email sent successfully, False otherwise.
    """
    try:
        # Check required configuration
        required_config = ['api_url', 'api_key', 'from_email', 'from_name', 'subject']
        for param in required_config:
            if param not in config:
                raise ValueError(f"Missing required configuration parameter: {param}")
        
        # Format current date for the filename
        current_date = datetime.now().strftime("%Y%m%d")
        
        # Prepare email recipients in BCC (so they don't see other recipients)
        bcc_list = []
        for recipient in recipients:
            if 'email' not in recipient:
                logging.warning(f"Skipping recipient without email address: {recipient}")
                continue
                
            recipient_data = {"email_address": {"address": recipient['email']}}
            if 'name' in recipient and recipient['name']:
                recipient_data["email_address"]["name"] = recipient['name']
            
            bcc_list.append(recipient_data)
        
        if not bcc_list:
            logging.error("No valid recipients provided")
            return False
        
        # Encode the Excel file as base64
        encoded_excel = base64.b64encode(excel_attachment).decode('utf-8')
        
        # Prepare the email payload
        payload = {
            "bounce_address": config.get('bounce_email', config['from_email']),
            "from": {
                "address": config['from_email'],
                "name": config['from_name']
            },
            "subject": config['subject'],
            "bcc": bcc_list,
            "htmlbody": """
                <div style='font-family: Arial, sans-serif; padding: 20px;'>
                    <h2>Report Generated</h2>
                    <p>Please find attached the Excel report.</p>
                    <p>This is an automated email, please do not reply.</p>
                    <p style='color: #555;'>
                        Best regards,<br>
                        The Reporter System
                    </p>
                </div>
            """,
            "attachments": [
                {
                    "name": f"Report_{current_date}.xlsx",
                    "content": encoded_excel
                }
            ]
        }
        
        # Set up headers with API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Zoho-enczapikey {config['api_key']}"
        }
        
        # Send the request to ZeptoMail API
        response = requests.post(
            config['api_url'],
            json=payload,
            headers=headers
        )
        
        # Check response
        if response.status_code == 200 or response.status_code == 202:
            logging.info(f"Email sent successfully to {len(bcc_list)} recipients")
            return True
        else:
            logging.error(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        logging.exception(f"Error sending email: {str(e)}")
        return False
