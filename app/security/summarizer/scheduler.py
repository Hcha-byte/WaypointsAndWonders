import datetime
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import markdown
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app, Flask
from flask_mail import Message
from pytz import timezone

from app.security.ip_blocklist import get_recent_blacklist
from app.security.summarizer.ai_summary import ai_summary
from ..config import RECENT_BLACKLIST_FILE, get_data_path

path_latest = Path(get_data_path("summary_latest.md"))


def update_recent_blacklist_file():
	recent_data = get_recent_blacklist()
	with open(RECENT_BLACKLIST_FILE, "w") as f:
		json.dump(recent_data, f, indent=2)


def run_hourly_summary(app: Flask):
	with app.app_context():
		from app.extensions import mail
		update_recent_blacklist_file()
		try:
			current_app.logger.info("Starting hourly honeypot log summary job")
			
			data = get_recent_blacklist()
			if data == \
					{
						"blacklisted_ips": {}
					}:
				current_app.logger.warning("No recent data, skipping AI summary")
				return
			
			api_key = current_app.config.get("TOGETHER_API_KEY")
			if not api_key:
				current_app.logger.warning("TOGETHER_API_KEY not set, skipping AI summary")
				summary_text = "TOGETHER_API_KEY not set."
			else:
				summary_text = ai_summary(data)
			
			# Combine stats + AI summary
			full_summary = (f"# AI Summary\n{summary_text}\n\n*Data loaded at "
			                f"{datetime.now(ZoneInfo('America/Denver')).strftime('%Y-%m-%d %H:%M:%S %Z')}*\n")
			# Save to a file for now — you can extend to DB or email later
			with path_latest.open("w") as f:
				f.write(full_summary)
			if app.config["IS_ON_RAILWAY"]:
				# 4. Create and send email
				msg = Message(
					subject="Daily Honeypot Summary",
					recipients=["hcha.byte@gmail.com"]
				)
				
				msg.html = markdown.markdown(full_summary, output_format="html")
				mail.send(msg)
			
			current_app.logger.info("Hourly honeypot log summary job finished successfully")
		
		except Exception as e:
			current_app.logger.error(f"Error in hourly honeypot summary job: {e}", exc_info=True)


def init_scheduler(app: Flask):
	import logging
	import smtplib
	smtplib.SMTP.set_debuglevel = lambda self, level=0: None  # disable all debuglevel changes
	
	# Suppress smtplib debug logs by setting its logger to WARNING or higher
	logging.getLogger('smtplib').setLevel(logging.WARNING)
	
	# Start the scheduler
	mountain = timezone("America/Denver")
	scheduler = BackgroundScheduler(timezone=mountain)
	now = datetime.now(mountain)
	if app.config["IS_ON_RAILWAY"]:
		# Run at 12:55 every day
		scheduler.add_job(
			func=run_hourly_summary,
			args=[],
			kwargs={"app": app},
			trigger=CronTrigger(hour=7, minute=0, timezone=mountain),
			max_instances=1,
			id="daily_summary"
		)
	else:
		run_time = now + timedelta(minutes=1)
		run_minute = (now.minute + 1) % 60
		run_hour = now.hour if run_minute > now.minute else (now.hour + 1) % 24
		
		job = scheduler.add_job(
			func=run_hourly_summary,
			kwargs={"app": app},
			trigger=CronTrigger(
				hour=run_hour,
				minute=run_minute,
				timezone=mountain,
				jitter=10
			),
			id='test_daily',
			max_instances=1,
			misfire_grace_time=60,
			replace_existing=True
		)
	
	scheduler.start()
	
	# Shutdown scheduler when the app exits
	import atexit
	atexit.register(lambda: scheduler.shutdown())
	app.logger.info("APScheduler started for honeypot log summaries")
