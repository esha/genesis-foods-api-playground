import requests
import configparser
import json
import os
import uuid

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve the API settings
endpoint = config.get('api', 'endpoint')
api_key = config.get('api', 'api_key')

# Define the headers with API Key
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

# Define the GraphQL mutation for creating an ingredient
mutation = """
mutation($input : CreateFoodInput!){
    foods{
        create(input:$input)
        {
            food{
                id
                name
                definingAmount{
                    quantity{
                        value
                    }
                    unit{
                        id
                        name
                    }
                }
                conversions{
                    from{
                        quantity{
                            value
                        }
                        unit{
                            id
                            name
                        }
                    }
                    to{
                        quantity{
                            value
                        }
                        unit{
                            id
                            name
                        }
                    }
                }
            }
        }
    }
}
"""


def run_mutation(food, food_type):
    """Run the GraphQL mutation to create an ingredient."""
    input_data = {
        "input": {
            "name": food.get("name") + ' ' + food_type + ':' + str(uuid.uuid4()),
            "foodType": food_type,
            # "definingAmount": food.get("definingAmount"),
            # "conversions": food.get("conversions")
        }
    }

    response = requests.post(endpoint, json={"query": mutation, "variables": input_data}, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def bulk_import(food_type, file_path):
    """Load JSON data from a file and run the mutation for each ingredient."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    for food in data:
        print(f"Importing {food_type}: {food.get('name')}")
        result = run_mutation(food, food_type)

        if result and "errors" in result:
            print(f"Error while creating {food_type}: {food.get('name')}")
            print(result["errors"])
        elif result:
            created_food = result.get("data", {}).get("foods", {}).get("create", {}).get("food", {})
            print(f"Created {food_type}: {created_food.get('name')} (ID: {created_food.get('id')})")


def main():
    # Load the input file path from config
    input_file_path = config.get('files', 'input_file')

    # Ensure the file exists
    if not os.path.exists(input_file_path):
        print(f"Input file '{input_file_path}' does not exist.")
        return

    # Import ingredients
    bulk_import('Ingredient', input_file_path)

    # Import recipies
    bulk_import('Recipe', input_file_path)


if __name__ == "__main__":
    main()
