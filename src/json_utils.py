import json, os, csv

def load_json_from_file(file_path)->dict:
    """Load JSON data from a file and return it as a dictionary."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load JSON data as a dictionary
            return data
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def json_print(json_dict):
    pretty_json = json.dumps(json_dict, indent=4)
    print(pretty_json)
    return 

def get_json_schema(json_dict):
    """
    Takes in a json dict.

    Args:
        json_dict (dict): The json data in a dict format.

    Returns:
        dict: A dictionary representing the schema of the JSON data.
    """
    def infer_schema(data):
        if isinstance(data, dict):
            return {key: infer_schema(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [infer_schema(item) for item in data] if data else []
        else:
            return type(data).__name__

    try:
        schema = infer_schema(json_dict)
        return schema
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def preview_json(json_file_path, num_samples=5):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        # Check if it's a list
        if isinstance(data, list):
            return data[:num_samples]  # Get first few items
        elif isinstance(data, dict):
            return {key: data[key] for key in list(data)[:num_samples]}  # Get first few keys
        else:
            return None

def save_dict_to_json(data_dict, file_path):
    """
    Saves a dictionary to a JSON file.

    Args:
        data_dict (dict): The dictionary to save.
        file_path (str): The file path where the JSON file will be saved.
    
    Raises:
        ValueError: If the input data is not a dictionary.
        IOError: If the file cannot be written.
    """
    # Check if data_dict is indeed a dictionary
    if not isinstance(data_dict, dict):
        raise ValueError("Input data must be a dictionary.")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the dictionary to the JSON file
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
    except IOError as e:
        raise IOError(f"Failed to write to file: {e}")

# print(data.keys() ) 
# videos1 = data["videos"][1]
# print(videos1) 
# save_dict_to_json(videos1, "../data/output/channel_data/videos1.json")
# print(get_json_schema(file) ) 
# print(preview_json(file) ) 
def flatten_json(nested_json, separator='_'):
    """
    Flattens a nested JSON object into a single-level dictionary.

    Args:
        nested_json (dict): The nested JSON object to flatten.
        separator (str): The separator to use when combining nested keys.

    Returns:
        dict: A flat dictionary with combined keys.
    """
    flat_dict = {}

    def flatten(item, parent_key=''):
        # If the item is a dictionary, recurse into each key-value pair
        if isinstance(item, dict):
            for key, value in item.items():
                full_key = f"{parent_key}{separator}{key}" if parent_key else key
                flatten(value, full_key)
        # If the item is a list, recurse into each element with an index
        elif isinstance(item, list):
            for index, value in enumerate(item):
                full_key = f"{parent_key}{separator}{index}"
                flatten(value, full_key)
        # If it's a leaf node, add it to the flat dictionary
        else:
            flat_dict[parent_key] = item

    flatten(nested_json)
    return flat_dict

def json_to_flat_csv(json_file_path, csv_file_path, separator='_'):
    """
    Converts a nested JSON file to a flat CSV file.
    
    Args:
        json_file_path (str): The path to the JSON file to convert.
        csv_file_path (str): The path where the CSV output file will be saved.
        separator (str): Separator used in flattening keys.
    """
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Flatten each record in the list (assuming JSON data is a list of dicts)
    flat_data = [flatten_json(record, separator=separator) for record in data]

    # Write to CSV
    if flat_data:
        fieldnames = flat_data[0].keys()  # Use the keys from the first item for CSV headers
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flat_data)
        print("Nested JSON data has been flattened and written to CSV.")

# Example usage
# json_to_flat_csv(file , "../data/output.csv")

def decode_unicode_json(data):
    """
    Decodes all Unicode escape sequences in a JSON-like dictionary efficiently by 
    serializing and deserializing the data with JSON functions.
    
    Parameters:
    data (dict): The JSON-like dictionary containing possible Unicode escape sequences.
    
    Returns:
    dict: A new dictionary with all Unicode escape sequences decoded in string values.
    """
    # Convert data to a JSON string and immediately parse it back
    return json.loads(json.dumps(data, ensure_ascii=False))
    
# file = "../data/output/channel_data/ΕΛΛΗΝΙΚΗ ΛΥΣΗ - ΚΥΡΙΑΚΟΣ ΒΕΛΟΠΟΥΛΟΣ.json"
# data = load_json_from_file(file) 
# decoded = decode_unicode_json(data)
# save_dict_to_json(decoded, "../data/output/elliniki_lysi_processed.json")

def find_key_globally(data, target_key):
    """
    Recursively searches for all occurrences of a specific key within a JSON-like dictionary.

    Parameters:
    ----------
    data : dict or list
        The JSON-like dictionary (or list) in which to search for the target key.
    target_key : str
        The key to search for within the dictionary.

    Returns:
    -------
    list
        A list of values associated with the specified key, found at any level of the input data.
        Returns an empty list if the key is not found.
    """
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                results.append(value)
            # Recursively search in nested dictionaries or lists
            if isinstance(value, (dict, list)):
                results.extend(find_key_globally(value, target_key))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                results.extend(find_key_globally(item, target_key))

    return results

