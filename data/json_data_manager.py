import json

from datetime import date

class JSONData:
    def __init__(self, filename) -> None:
        self.filename = filename
    
    def read_json(self, key):
        """
        Read data from the JSON file based on a specified key.

        This method reads the JSON file, retrieves the value associated with the provided key, and returns it.

        Parameters:
        - key (str): The key used to retrieve the data from the JSON file.

        Returns:
        The value associated with the specified key in the JSON file.

        Example:
        >>> json_data = JSONData("data.json")
        >>> result = json_data.read_json("my_key")
        >>> print(result)

        """
        try:
            with open(self.filename, 'r') as json_file:
                data = json.load(json_file)
                result = data[key]
                return result

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data from {self.filename}: {e}")
            return None

    def write_json(self, keys, value):
        """
        Write data to the JSON file using a specified set of keys.

        This method reads the JSON file, modifies the value associated with the specified set of keys, and updates the JSON file with the new data.

        Parameters:
        - keys (list): A list of keys to navigate through the JSON structure to locate the target value.
        - value: The new value to be written to the JSON file.

        Returns:
        A message indicating the successful update of the JSON file.

        Example:
        >>> json_data = JSONData("data.json")
        >>> result = json_data.write_json(["my", "nested", "key"], "new_value")
        >>> print(result)

        """
        try:
            with open(self.filename, 'r+') as json_file:
                data = json.load(json_file)
                nested_dict = data
                for key in keys[:-1]:
                    nested_dict = nested_dict.setdefault(key, {})
                nested_dict[keys[-1]] = value
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()
            return f"'{'/'.join(keys)}' updated in the JSON file"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading or writing data: {e}")
            return None
        
class DateEncoder(json.JSONEncoder):
    """
        Convert date objects to ISO format when encoding to JSON.

        This method is used as part of the JSON encoding process to handle date objects.

        Parameters:
        - obj: The object being encoded.

        Returns:
        If the object is a date, its ISO format representation; otherwise, the default JSON encoding.

        Example:
        >>> json_data = {"date": date(2023, 11, 8)}
        >>> json_string = json.dumps(json_data, cls=DateEncoder)
        >>> print(json_string)

        """
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)
