import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, timezone
from dotenv import load_dotenv
load_dotenv()

def send_daily_mudge(rows, recipient_email):
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).date().isoformat()

    today_tasks = [r for r in rows if r['date'] == today]
    if not today_tasks:
        future_dates = sorted(set(r['date'] for r in rows if r['date'] >= today))
        if future_dates:
            today_tasks = [r for r in rows if r['date'] == future_dates[0]]

    print(f"📅 Today is: {today}")
    print(f"📋 Tasks found for today: {len(today_tasks)}")
    print(f"📋 All dates in timetable: {set(r['date'] for r in rows)}")

    if not today_tasks:
        print("⚠️ No tasks for today! Email will be empty.")
        return  # ← stops here if no tasks, no point sending empty email

    sender_email = os.getenv("GMAIL_ID")
    app_password = os.getenv("GMAIL_PASSWORD")

    print(f"📧 Sender: {sender_email}")
    print(f"📧 Receiver: {recipient_email}")

    table_rows = ''.join(
        f"<tr>"
        f"<td>{r['subject']}</td>"
        f"<td>{r['topic']}</td>"
        f"<td>{r['minutes']} min</td>"
        f"<td><i>{r['notes']}</i></td>"
        f"</tr>"
        for r in today_tasks
    )

    total_mins = sum(r['minutes'] for r in today_tasks)

    html = f"""
        <h2>StudyPilot - {today}</h2>
        <table border='1' cellpadding='6'>
        <tr><th>Subject</th><th>Topics</th><th>Time</th><th>Notes</th></tr>
        {table_rows}
        </table>
        <p><strong>Total today: {total_mins} minutes</strong></p>
        <p>Stay consistent. See you tomorrow.</p>
        """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'StudyPilot - Your plan for {today}'
    msg['From']    = f"StudyPilot <{sender_email}>"   # ← change this line
    msg['Reply-To'] = sender_email                     # ← add this
    msg['X-Priority'] = '1'                            # ← add this
    msg['To']      = recipient_email
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f'✅ Nudge sent to {recipient_email}')
    except Exception as e:
        print(f'❌ Email failed: {e}')
        raise