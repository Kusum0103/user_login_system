import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_email(email, username, otp):
  
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_sender = os.getenv("SMTP_SENDER")
    smtp_password = os.getenv("SMTP_PASSWORD")


    if not smtp_sender or not smtp_password:
        print("\n" + "="*80)
        print(f"[DEV MODE] SMTP not configured in .env.")
        print(f"VERIFICATION OTP FOR {username} ({email}): {otp}")
        print("="*80 + "\n")
        return True

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Plus Jakarta Sans', Arial, sans-serif;
                background-color: #f3f4f6;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 500px;
                margin: 40px auto;
                background: #ffffff;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
                overflow: hidden;
                border: 1px solid #e5e7eb;
            }}
            .header-banner {{
                background: linear-gradient(135deg, #2563eb, #60a5fa);
                padding: 30px 20px;
                text-align: center;
                color: #ffffff;
            }}
            .header-banner h1 {{
                margin: 0;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            .content-body {{
                padding: 30px 25px;
                color: #1e3a8a;
                text-align: center;
            }}
            .content-body p {{
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 20px;
                text-align: left;
            }}
            .otp-box {{
                background: rgba(37, 99, 235, 0.06);
                border: 2px dashed #2563eb;
                border-radius: 16px;
                padding: 16px 20px;
                margin: 25px auto;
                display: inline-block;
                letter-spacing: 6px;
                font-size: 32px;
                font-weight: 700;
                color: #2563eb;
            }}
            .expiry-note {{
                font-size: 13px;
                color: #dc2626;
                font-weight: 500;
                margin-top: 10px;
            }}
            .footer {{
                background: #f9fafb;
                padding: 20px;
                text-align: center;
                border-top: 1px solid #f3f4f6;
                font-size: 12px;
                color: rgba(30, 58, 138, 0.5);
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header-banner">
                <h1>Verify Your Account</h1>
            </div>
            <div class="content-body">
                <p>Hello <strong>{username}</strong>,</p>
                <p>Thank you for registering at our Mock Placement Interview System. Use the following One-Time Password (OTP) to verify your email and complete your registration:</p>
                <div class="otp-box">{otp}</div>
                <div class="expiry-note">This OTP code is valid for 5 minutes only. Do not share this code with anyone.</div>
                <p style="text-align: left; margin-top: 25px;">Best regards,<br><strong>Mock Interview Team</strong></p>
            </div>
            <div class="footer">
                This is an automated message. Please do not reply directly to this email.
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = smtp_sender
    msg['To'] = email
    msg['Subject'] = f"{otp} is your verification code"
    msg.attach(MIMEText(html_content, 'html'))

    try:
     
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_sender, smtp_password)
        server.sendmail(smtp_sender, email, msg.as_string())
        server.quit()
        print(f"[MAIL-SUCCESS] Verification OTP email successfully sent to {email}")
        return True
    except Exception as e:
        print(f"[MAIL-ERROR] Failed to send email to {email}: {e}")
        print(f"[MAIL-BACKUP-OTP] Backup OTP code: {otp}")
        return False
