import json
from pathlib import Path

import together


def ai_summary(data: dict) -> str:  # HTML
	client = together.Client()
	html = Path("app/security/summarizer/html/test2.html")
	
	with html.open("r", encoding="utf-8") as f:
		html_content = f.read()
	
	prompt = f"""Summarize the following blacklist data from a honeypot firewall system:
{json.dumps(data, indent=2)}
Return overall insights, top targets, and any strange behavior."""
	response = client.chat.completions.create(
		model="meta-llama/Llama-Vision-Free",
		messages=[
			{
				"role":    "user",
				"content": prompt
			},
			{
				"role":    "system",
				"content": "You will be given blacklist information from a honeypot firewall system, the blacklisted "
				           "IPs were collected from a honeypot system using fake routes. You will summarize the data "
				           "and provide overall insights, top targets, and any strange behavior."
			},
			{
				"role":    "system",
				"content": "You will respond in html format, only include the html. Use the following template:"
				           f"\n\n\n{html_content}"
			}
		
		]
	)
	html_content = response.choices[0].message.content
	doctype_index = html_content.find("<!DOCTYPE html>")
	if doctype_index != -1:
		html_content = html_content[doctype_index:]
	return html_content
