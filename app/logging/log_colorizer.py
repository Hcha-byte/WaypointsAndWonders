# app/logging/log_colorizer.py
import logging
import os
import re
import sys

# ... (rest of your ColorFormatter and LOGGING_CONFIG)

print(f"DEBUG: PYTHONPATH in log_colorizer.py: {os.environ.get('PYTHONPATH')}", file=sys.stderr)
print(f"DEBUG: sys.path in log_colorizer.py: {sys.path}", file=sys.stderr)

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


class ColorFormatter(logging.Formatter):
	# noinspection RegExpRedundantEscape
	def format(self, record):
		original_line = super().format(record)
		line = original_line
		
		line = re.sub(
			r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Z]{2,4})\]',
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
			lambda
				m: f"{COLORS['cyan']}{m.group(1)}{COLORS['reset']} {COLORS['bold_yellow']}{m.group(2)}{COLORS['reset']}",
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


import sys

LOGGING_CONFIG = {
	'version':                  1,
	'disable_existing_loggers': False,
	'formatters':               {
		'colored_formatter': {
			'()':      'app.logging.log_colorizer.ColorFormatter',
			'format':  "[%(asctime)s] [%(levelname)s] %(message)s",
			'datefmt': "%Y-%m-%d %H:%M:%S %Z",
		},
	},
	'handlers':                 {
		'console': {
			'class':     'logging.StreamHandler',
			'formatter': 'colored_formatter',
			'level':     'DEBUG',
			'stream':    sys.stdout,
		},
	},
	'loggers':                  {
		'hypercorn.access': {
			'handlers':  ['console'],
			'level':     'DEBUG',
			'propagate': False,
		},
		'hypercorn.error':  {
			'handlers':  ['console'],
			'level':     'DEBUG',
			'propagate': False,
		},
		'werkzeug':         {
			'handlers':  ['console'],
			'level':     'DEBUG',
			'propagate': False,
		},
		'':                 {  # Root logger
			'handlers':  ['console'],
			'level':     'INFO',
			'propagate': False,
		},
	},
}

### For testing only ###
if __name__ == "__main__":
	import sys
	
	logger = logging.getLogger("test")
	handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(ColorFormatter(
		"[%(asctime)s] [%(levelname)s] %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S %Z"
	))
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG)
	
	logger.debug("GET /test/path 200 OK")
	logger.warning("POST /login 403 Forbidden")
	logger.error("DELETE /item/5 500 Internal Server Error")
