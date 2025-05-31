import json


def ensure_endline_in_json(input_path, output_path=None):
    # Load the JSON content
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Define the output file (overwrite or new)
    if output_path is None:
        output_path = input_path

    # Dump JSON with an explicit newline at the end
    with open(output_path, 'w', encoding='utf-8') as f:
        # noinspection PyTypeChecker
        json.dump(data, f, indent=2)
  
        f.write('\n')  # Add final newline

    print(f"Saved properly formatted JSON to '{output_path}'.")

# Example usage:
# ensure_endline_in_json('washington_trip.json')
