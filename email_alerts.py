import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import datetime
import os

# ✅ Your email config — update these!
SENDER_EMAIL    = "derindevis79@gmail.com"      # your Gmail
SENDER_PASSWORD = "aaoe myap acea dtni"       # 16 char app password
RECEIVER_EMAIL  = "derindevis79@gmail.com"  # who gets the alert

def send_defect_alert(image_name, defect_type, confidence, 
                      severity, region, recommendation):
    """Send email alert for HIGH severity defects"""
    
    try:
        # Create email
        msg = MIMEMultipart()
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = RECEIVER_EMAIL
        msg["Subject"] = f"🚨 HIGH SEVERITY DEFECT DETECTED — {defect_type}"

        # Email body
        now = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        
        body = f"""
========================================
   🚨 DEFECT ALERT — IMMEDIATE ACTION REQUIRED
========================================

Date & Time      : {now}
Image            : {image_name}
Defect Type      : {defect_type}
Confidence       : {confidence*100:.1f}%
Severity         : {severity}
Region           : {region}
Recommendation   : {recommendation}

========================================
   ⚠️ Please take immediate action!
========================================

This is an automated alert from:
AI Visual Quality Inspector
Powered by AI
        """

        msg.attach(MIMEText(body, "plain"))

        # Send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        print(f"✅ Alert email sent to {RECEIVER_EMAIL}!")
        return True

    except Exception as e:
        print(f"⚠️ Email failed: {e}")
        return False


def send_daily_summary(total, passed, failed, pass_rate):
    """Send daily inspection summary email"""
    
    try:
        msg = MIMEMultipart()
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = RECEIVER_EMAIL
        msg["Subject"] = f"📊 Daily Inspection Summary — {datetime.date.today()}"

        now = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        body = f"""
========================================
   📊 DAILY INSPECTION SUMMARY REPORT
========================================

Date & Time       : {now}

Total Inspected   : {total}
✅ Passed         : {passed}
❌ Failed         : {failed}
📊 Pass Rate      : {pass_rate:.1f}%

========================================
   View full details on your dashboard:
   http://localhost:8501
========================================

AI Visual Quality Inspector
Powered by YOLOv8 + Edufyi Tech Solutions
        """

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        print(f"✅ Daily summary sent to {RECEIVER_EMAIL}!")
        return True

    except Exception as e:
        print(f"⚠️ Email failed: {e}")
        return False