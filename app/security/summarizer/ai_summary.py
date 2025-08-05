import json

import together
from flask import send_from_directory


def ai_summary(data: dict) -> str:
	client = together.Client()
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
				"content": "You will respond in markdown format. Use the following template:"
				           f"\n\n\n{send_from_directory('html', 'test2.html')}"
			}
		
		]
	)
	return str(response.choices[0].message.content)
