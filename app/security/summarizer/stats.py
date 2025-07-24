from collections import Counter


def summarize_stats(data):
	reasons = Counter()
	countries = Counter()
	paths = Counter()
	
	for entry in data.values():
		reasons[entry.get("reason", "unknown")] += 1
		countries[entry.get("country", "unknown")] += 1
		paths[entry.get("location", "unknown")] += 1
	
	return {
		"reasons":   reasons.most_common(5),
		"countries": countries.most_common(5),
		"paths":     paths.most_common(5),
	}
