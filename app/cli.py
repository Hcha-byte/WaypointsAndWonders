# app/search/cli.py (or wherever appropriate)

import click

from app.search.funtions import bulk_index_posts, search_posts


@click.command("index_all")
def index_all_command():
	try:
		response = bulk_index_posts()
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
