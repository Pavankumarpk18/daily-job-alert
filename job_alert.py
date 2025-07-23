from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ✅ Load environment variables from .env
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

EMAIL_SUBJECT = "🚀 Daily Entry-Level AI/ML/DS Jobs at Top Startups & Job Boards"

# -------- JOB SCRAPER --------
def search_jobs():
    headers = {"User-Agent": "Mozilla/5.0"}

    job_boards = {
         "Google Jobs": "https://www.google.com/search?q=site:jobs.google.com+entry+level+AI+ML+data+science+startup",
         "Indeed": "https://www.indeed.com/jobs?q=entry+level+AI+ML+data+science&sort=date",
         "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords=entry%20level%20AI%20ML%20data%20science%20startup",
         "Glassdoor": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=entry%20level%20AI%20ML%20data%20science",
         "Foundit": "https://www.foundit.in/search/entry-level-ai-ml-data-science-jobs",
         "FreshersWorld": "https://www.freshersworld.com/jobs/jobsearch/entry-level-ai-ml-data-science-jobs",

    # Startup & Remote Friendly
         "Wellfound (AngelList)": "https://wellfound.com/jobs#find/f!f=entry-level&role=Data%20Science,AI,ML",
         "Y Combinator": "https://www.workatastartup.com/jobs?query=ai%20ml%20data%20science",
         "Levels.fyi": "https://www.levels.fyi/jobs/",
         "Toptal": "https://www.toptal.com/careers#positions",
         "X-Team": "https://x-team.com/remote-developer-jobs/",
         "Turing": "https://www.turing.com/jobs",
         "Gun.io": "https://www.gun.io/jobs",
         "Lemon.io": "https://lemon.io/for-developers/",
         "Flexiple": "https://flexiple.com/freelance-jobs/",
         "Dribbble": "https://dribbble.com/jobs?search=machine+learning",
         "TechCrunch": "https://jobs.techcrunch.com/jobs?q=AI+ML",

    # Freelance & Gig
         "Upwork": "https://www.upwork.com/freelance-jobs/ai-machine-learning/",
         "Freelancer": "https://www.freelancer.com/jobs/machine-learning/",
         "Outsourcely": "https://www.outsourcely.com/remote-jobs/developer",
         "Virtual Vocations": "https://www.virtualvocations.com/q-remote-ai-machine-learning-jobs.html",
         "Working Nomads": "https://www.workingnomads.com/jobs",
         "Jobspresso": "https://jobspresso.co/remote-machine-learning-jobs/",
         "FlexJobs": "https://www.flexjobs.com/search?search=AI+machine+learning",
         "We Work Remotely": "https://weworkremotely.com/remote-jobs/search?term=machine+learning",
         "Remote.com": "https://remote.com/remote-jobs/developer/",
         "RemoteOK": "https://remoteok.com/remote-ai+ml+data+science-jobs",

    # Niche Remote Sites
         "NoDesk": "https://nodesk.com/remote-jobs/machine-learning/",
         "Remoters": "https://remoters.net/remote-jobs/developer/",
         "RemoteHabits": "https://remotehabits.com/jobs/",
         "Remote4Me": "https://remote4me.com/ml",
         "Pangian": "https://pangian.com/job-travel-remote/remote-machine-learning-jobs/",
         "Remotees": "https://remotees.com/",
         "Remote of Asia": "https://remoteofasia.com/jobs",
         "SimplyHired": "https://www.simplyhired.com/search?q=entry+level+ai+ml+data+science",
         "Taptol": "https://www.taptol.com/jobs"
        
    }

    job_links = []

    for board, url in job_boards.items():
        try:
            print(f"🔎 Scraping {board}...")
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a")
            count = 0

            for link in links:
                href = link.get("href")
                if href:
                    if board == "Google Jobs" and "url?q=" in href:
                        actual_url = href.split("url?q=")[1].split("&")[0]
                        job_links.append(f"{board}: {actual_url}")
                        count += 1
                    elif board != "Google Jobs" and any(word in href.lower() for word in ["job", "jobs", "intern"]):
                        if href.startswith("/"):
                            domain = url.split("/")[2]
                            href = f"https://{domain}{href}"
                        elif not href.startswith("http"):
                            continue
                        job_links.append(f"{board}: {href}")
                        count += 1

                if count >= 3:
                    break

        except Exception as e:
            job_links.append(f"{board}: ❌ Error - {str(e)}")
            print(f"⚠️ Error scraping {board}: {e}")

    return job_links

# -------- EMAIL SENDER --------
def send_email(job_links):
    print("📧 Preparing to send email...")
    body = "Here are today's latest entry-level AI/ML/DS jobs:\n\n"
    body += "\n".join(job_links)
    body += f"\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    msg = MIMEText(body)
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print("❌ SMTP Authentication Error: Check your App Password.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# -------- DAILY TASK --------
def job_task():
    print(f"\n⏰ Running job search at {datetime.now().strftime('%H:%M:%S')}...")
    job_links = search_jobs()
    if job_links:
        send_email(job_links)
    else:
        print("❌ No job links found.")

# -------- SCHEDULER --------
schedule.every().day.at("11:00").do(job_task)
print("🕒 Job Alert Automation running daily at 11:00 AM...")

while True:
    schedule.run_pending()
    time.sleep(60)
