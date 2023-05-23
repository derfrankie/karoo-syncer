#!/usr/bin/env /opt/homebrew/bin/python3
import requests
import json
import jwt
import os
import re
from datetime import datetime
import random
import time

BASE_URL = 'https://dashboard.hammerhead.io/v1'

# Produktion

CONFIG_FILE_PATH = "ksync-prod.json"

def random_wait():
    wait_time = random.uniform(1, 4)
    wait_time = int(wait_time)  # Convert wait_time to an integer

    print(f"Waiting for {wait_time} seconds... ", end='', flush=True)

    for seconds in reversed(range(1, wait_time + 1)):
        print(seconds, end=' ', flush=True)
        time.sleep(1)


def read_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def get_token(user, password):
    DebugLog("Authenticating...")
    payload = {
        'grant_type': 'password',
        'username': user,
        'password': password,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    r = requests.post(
        BASE_URL + '/auth/token',
        data=payload,
        headers=headers,
    )
    response = r.json()
    if 'access_token' in response:
        DebugLog("Authentication successful.")
        token = response['access_token']
        decoded_jwt = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
        user_id = decoded_jwt['sub']
        return token, user_id
    else:
        DebugLog(f"Authentication failed. Response: {response}")
        return None, None
    
def DebugLog(message, wait=False):
    print(f'{datetime.now()} - {message}')
    if wait:
        input("Press Enter to continue...")

def get_all_collections(user_id, access_token):
    DebugLog("Getting all collections...")
    # HTTP request to get all collections
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(f'https://dashboard.hammerhead.io/v1/users/{user_id}/collections', headers=headers)

    if response.status_code != 200:
        DebugLog("Failed to fetch collections")
        return None

    collections = json.loads(response.text)

    DebugLog(f" Collections: {collections}")
    return collections


def create_collection(user_id, access_token, collection_name, description=""):
    DebugLog(f"Creating collection: {collection_name}...")
    # HTTP request to create a collection
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'name': collection_name,
        'description': description
    }

    response = requests.post(f'https://dashboard.hammerhead.io/v1/users/{user_id}/collections', 
                             headers=headers, data=json.dumps(payload))

    # Handle the response
    if response.status_code == 201 or response.status_code == 200:
        DebugLog(f"Collection {collection_name} created successfully")
        created_collection = json.loads(response.text)
        random_wait
        return created_collection
    else:
        DebugLog(f"Failed to create collection - {response.text}")
        return None # Handle the failed import scenario
    

def delete_collection(user_id, access_token, collection_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.delete(f'{BASE_URL}/users/{user_id}/collections/{collection_id}', headers=headers)

    if response.status_code != 200:
        DebugLog(f"Failed to delete collection {collection_id}")
        return False

    DebugLog(f"Successfully deleted collection {collection_id}")
    random_wait
    return True

def get_routes_in_collection(user_id, access_token, collection_id):
    DebugLog(f"Getting routes in collection: {collection_id}")
    
    # Prepare the request headers
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    # Prepare the request parameters
    params = {
        'per_page': 50,
        'page': 1,
        'search': '',
        'order_by': 'NEWEST',
        'ascending': 'true',
        'include': collection_id,
        'exclude': 'archive'
    }
    
    # Send the GET request
    response = requests.get(BASE_URL + '/users/' + user_id + '/routes', headers=headers, params=params)
    
    # Handle the response
    if response.status_code == 200:
        routes_data = response.json()
        routes = routes_data['data']
        DebugLog(f"Successfully fetched {len(routes)} routes in collection {collection_id}")
        return routes
    else:
        DebugLog(f"Failed to fetch routes in collection {collection_id}: {response.status_code}")
        return []

def delete_route(user_id, access_token, route_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.delete(f'{BASE_URL}/users/{user_id}/routes/{route_id}', headers=headers)

    if response.status_code != 200:
        DebugLog(f"Failed to delete route {route_id}")
        return False

    DebugLog(f"Successfully deleted route {route_id}")
    random_wait
    return True


def import_route(user_id, access_token, collection_id, file_path):
    DebugLog(f"Importing route: {file_path}")
    DebugLog(f"Collection_id: {collection_id}")

    config = read_config(CONFIG_FILE_PATH)

    # Prepare the request headers
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Prepare the files data
    files = {'file': open(file_path, 'rb')}

    # Send the POST request with multipart/form-data
    url = f"{BASE_URL}/users/{user_id}/routes/import/file?collectionId={collection_id}"
    response = requests.post(url, headers=headers, files=files)

    # Handle the response
    if response.status_code == 201:
        DebugLog("Route import successful")
        route_data = response.json()
        # for item in route_data:
        # DebugLog(str(item))
        random_wait()
    else:
        DebugLog(f"Route import failed with status code: {response.status_code}")
        random_wait()
        # Handle the failed import scenario



def fix_filenames(directory, recursive=False):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.gpx'):
                safe_filename = re.sub(r'[\\/:*?"<>|]', '-', file)
                safe_filename = re.sub(r'\s{2,}', ' ', safe_filename).strip()
                new_path = os.path.join(root, safe_filename)
                if new_path != os.path.join(root, file):
                    os.rename(os.path.join(root, file), new_path)
                    DebugLog(f"Renamed file {file} to {safe_filename}")
        
        if not recursive:
            break

        
        if not recursive:
            break

def find_gpx_files(directory, recursive=False):
    gpx_files = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.gpx'):
                if root not in gpx_files:
                    gpx_files[root] = []

                gpx_files[root].append(file)

                DebugLog(f"Found GPX file {file} in directory {root}")

        if not recursive:
            break

    return gpx_files

def match_routes_and_files(collections, gpx_files, base_directory):
    matched = {}
    new_collections = {}

    for folder, files in gpx_files.items():
        collection_name = os.path.basename(folder)

        if folder == base_directory:
            DebugLog(f"Skipping files in base folder: {base_directory}")
            continue

        matched_collection = None
        for collection in collections:
            if collection['name'].lower() == collection_name.lower():
                matched_collection = collection
                break

        if matched_collection:
            if matched_collection['name'] not in matched:
                matched[matched_collection['name']] = []
            matched[matched_collection['name']].extend(files)
            DebugLog(f"Matched Collection: {matched_collection['name']}")
        else:
            if collection_name not in new_collections:
                new_collections[collection_name] = []
            new_collections[collection_name].extend(files)
            DebugLog(f"New Collection: {collection_name}")

    DebugLog(f"Matched {len(matched)} collections with GPX files - {matched}")
    DebugLog(f"Found {len(new_collections)} new collections - {new_collections}")

    return matched, new_collections



def main():
    DebugLog("Starting script...")
    
    config = read_config(CONFIG_FILE_PATH)
    if config['clean_filenames']: fix_filenames(config['directory'], config['scan_subfolders'])
    for user in config['users']:
        access_token, user_id = get_token(user['username'], user['password'])
        if access_token is None:
            DebugLog(f"Skipping user {user['username']} due to authentication failure.")
            continue
        
        collections = get_all_collections(user_id, access_token)
        file_collections = find_gpx_files(config['directory'], config['scan_subfolders'])
        matched_collections, new_collections = match_routes_and_files(collections, file_collections, config['directory'])
        
        for collection_name, file_paths in matched_collections.items():
            DebugLog(f"Matching collection name: {collection_name}")
            collection_id = next((coll['id'] for coll in collections if coll['name'] == collection_name), None)
            DebugLog(f"Matched collection ID: {collection_id}")
            if collection_id:
                if config['clear_collections']:
                    DebugLog('Clearing Collection of all Routes')
                    routes = get_routes_in_collection(user_id, access_token, collection_id)
                    for route in routes:
                        delete_route(user_id, access_token, route['id'])

                collection_folder = os.path.join(config['directory'], collection_name)
                files_in_folder = os.listdir(collection_folder)
                for file in files_in_folder:
                    full_file_path = os.path.join(collection_folder, file)
                    import_route(user_id, access_token, collection_id, full_file_path)
   
        for new_collection_name in new_collections:
            collection_folder = os.path.join(config['directory'], new_collection_name)
            collection_id = create_collection(user_id, access_token, new_collection_name)
            file_paths = new_collections.get(new_collection_name, [])
            for file_path in file_paths:
                full_file_path = os.path.abspath(os.path.join(collection_folder, file_path))
                import_route(user_id, access_token, collection_id, full_file_path)

    DebugLog("Script finished.")




if __name__ == "__main__":
    main()
