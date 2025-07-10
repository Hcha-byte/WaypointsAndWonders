# log_colorizer.py
import re
import sys

# ANSI color codes
COLORS = {
	'reset':       "\033[0m",
	'dim':         "\033[90m",
	'cyan':        "\033[1;96m",
	'blue':        "\033[1;94m",
	'white':       "\033[1;97m",
	'green':       "\033[1;92m",
	'yellow':      "\033[1;93m",
	'red':         "\033[1;91m",
	'bold_white':  "\033[1;97m",  # Bold and Bright White for routes
	'bold_yellow': "\033[1;93m",  # Bold and Bright Yellow for routes
}


# noinspection RegExpRedundantEscape
def color_line(line):
	original_line = line
	
	# Timestamp
	line = re.sub(
		r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+\-]\d{4})\]',
		lambda m: f"{COLORS['dim']}[{m.group(1)}]{COLORS['reset']}",
		line
	)
	
	# Log levels
	line = re.sub(r'\[(INFO)\]', lambda m: f"{COLORS['blue']}[{m.group(1)}]{COLORS['reset']}", line)
	line = re.sub(r'\[(DEBUG)\]', lambda m: f"{COLORS['cyan']}[{m.group(1)}]{COLORS['reset']}", line)
	line = re.sub(r'\[(WARNING|WARN)\]', lambda m: f"{COLORS['yellow']}[{m.group(1)}]{COLORS['reset']}", line)
	line = re.sub(r'\[(ERROR|CRITICAL)\]', lambda m: f"{COLORS['red']}[{m.group(1)}]{COLORS['reset']}", line)
	
	# Match and color HTTP method and path in the log
	line = re.sub(
		r'(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD) (/[^ ]+|/)',
		lambda m: f"{COLORS['cyan']}{m.group(1)}{COLORS['reset']} {COLORS['bold_yellow']}{m.group(2)}{COLORS['reset']}",
		line
	)
	
	# Status code coloring
	match = re.search(r'\s(\d{3})(?!\d)', line)
	if match:
		status = match.group(1)
		if status == "403":
			return f"{COLORS['dim']}{original_line}{COLORS['reset']}"
		elif status == "410":
			return f"{COLORS['dim']}{original_line}{COLORS['reset']}"
		elif status.startswith("2"):
			color = COLORS['green']
		elif status.startswith("3"):
			color = COLORS['blue']
		elif status.startswith("4"):
			color = COLORS['yellow']
		elif status.startswith("5"):
			color = COLORS['red']
		else:
			color = COLORS['reset']
		
		line = re.sub(
			r'(\s' + re.escape(status) + r')(?!\d)',
			lambda m: f"{color}{m.group(1)}{COLORS['reset']}",
			line
		)
	
	return line


# Read from stdin and process
try:
	for line in sys.stdin:
		print(color_line(line.rstrip()))
except KeyboardInterrupt:
	pass
