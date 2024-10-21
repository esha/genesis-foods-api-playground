import requests
import configparser
import json
import os

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve the API settings
endpoint = config.get('api', 'endpoint')
api_key = config.get('api', 'api_key')

# Retrieve the output file path from the configuration
output_file = config.get('files', 'output_file')

# Ensure the file is written to the local directory
file_path = os.path.join(os.getcwd(), output_file)

# Delete the file if it already exists
if os.path.exists(file_path):
    os.remove(file_path)
    print(f"Existing file '{file_path}' has been deleted.")

# Define the headers
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

# Define the GraphQL query
query = """
query($input: FoodSearchInput!){
    foods{
        search(input: $input) {
            foodSearchResults{
                id
                name
                modified
                created
                versionName
                eshaCode
                foodType
                product
                supplier
                versionHistoryId
            }
            totalCount
            pageInfo{
                cursor
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
}
"""


def run_query(graphql_query, variables):
    """Run a GraphQL query against the Genesis API with variables."""
    response = requests.post(
        endpoint,
        json={'query': graphql_query, 'variables': variables},
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None


def export(graphql_query, food_type):
    first_entry = True
    """Iterate through each character in the corpus and update the searchText."""
    with open(file_path, "a") as file:

        file.write("[\n")  # Write the opening bracket for the JSON array

        variables = {
            "input": {
                "searchText": '*',
                "foodTypes": [food_type],
                "itemSourceFilter": "Customer",
                "versionFilter": "All",
                "first": 10000,
                "after": 0
            }
        }

        print(f"Running query...")
        result = run_query(graphql_query, variables)
        if result:
            total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
            print(f"Found {total_count} results")
            if total_count > 0:
                if not first_entry:
                    file.write(",\n")  # Add a comma before each entry - except the first
                json.dump(result, file, indent=4)  # Append the JSON response to the file
                first_entry = False
            else:
                print(f"No results found. Skipping write.")

        file.write("\n]")  # Write the closing bracket for the JSON array


# Run the playground script
if __name__ == "__main__":
    export(query, 'Ingredient')  # Ingredient or Recipe
    print(f"Complete. Exported results to {file_path}")
