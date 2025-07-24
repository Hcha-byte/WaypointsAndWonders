# app/search/cli.py (or wherever appropriate)
import click
from flask import current_app
from rich.console import Console
from rich.markdown import Markdown

from .security.config import RECENT_BLACKLIST_FILE

console = Console()
from app.search.funtions import bulk_index_posts, search_posts
from app.security.summarizer.ai_summary import ai_summary
from app.security.summarizer.loader import load_blacklist
from app.security.summarizer.stats import summarize_stats


@click.command("index_all")
def index_all_command():
	try:
		bulk_index_posts()
		click.echo("Indexing complete.")
	except Exception as e:
		click.echo(f"Error during indexing: {e}")
		return 1
	
	return 0


@click.command("search")
@click.argument("query")
def search_command(query):
	try:
		posts = search_posts(query)
		click.echo("Search results:")
		for post in posts:
			click.echo(f"Title: {post.get('title', 'Untitled')}")
			click.echo(f"Date Posted: {post.get('date_posted', 'Unknown')}")
			click.echo(f"Location: {post.get('location_name', 'Unknown')}")
			click.echo(f"Content: {post.get('content', '')[:150]}...")
			click.echo("--------------------")
	
	except Exception as e:
		click.echo(f"Error during search: {e}")
		return 1
	
	return 0


@click.command("summarize-logs")
def summarize_logs():
	data = load_blacklist(RECENT_BLACKLIST_FILE)
	stats = summarize_stats(data)
	response = ""
	response += "\n# Honeypot Stats"
	for category, values in stats.items():
		response += f"\nTop {category.title()}:"
		for val, count in values:
			response += f"  - {val}: {count}"
	
	response += "\n# AI Summary"
	api_key = current_app.config.get("TOGETHER_API_KEY")
	if api_key:
		response += ai_summary(data)
	else:
		response += "No Together API key configured."
	md = Markdown(response)
	console.print(md)


def register_commands(app):
	app.cli.add_command(summarize_logs)
	app.cli.add_command(index_all_command)
	app.cli.add_command(search_command)
