# ksync Route Sync for Hammerhead Karoo by GravelDeluxe

The `ksync` Python Route Sync Script is a versatile tool designed to synchronize route files from folders on your computer to the Hammerhead Dashboard. This script replicates folders as collections on the Dashboard, with various configuration options to customize the synchronization process according to your needs.

It does not use public APIs and it's possible that it breaks without notice - use at your own risk.

## Features

- Synchronize route folders from your computer to the Hammerhead Dashboard.
- Each folder is replicated as a collection on the Dashboard.
- Supports scanning subfolders for routes.
- Provides the option to clean a collection before uploading new routes.
- Allows synchronization with multiple Hammerhead accounts (you and your buddies for example).


## Prerequisites

- Python 3.6 or later
- Required Python packages (can be installed using `pip`):
  - `requests`
  - `jwt`
  - `json`

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/yourusername/ksync-python-route-sync.git
    ```

2. Navigate to the repository folder:

    ```bash
    cd ksync-python-route-sync
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Rename the provided `ksync.sample.json` file to `ksync.json`.

2. Edit the `ksync.json` file to include your Hammerhead Dashboard credentials and configure the synchronization settings:

    ```json
    {
        "users": [
            {
                "username": "yourusername@gmail.com",
                "password": "yourpassword"
            }
        ],
        "directory": "/path/to/your/route/files",
        "scan_subfolders": true,
        "clear_collections": true,
        "overwrite_tour": true,
        "clean_filenames": false
    }
    ```

## Usage

1. Run the script:

    ```bash
    python ksync.py
    ```

## License

This project is licensed under the [MIT License](LICENSE).

---

Please replace "yourusername" and "yourpassword" with the actual Hammerhead Dashboard credentials you intend to use. You can customize the README further to highlight the specific functionalities of your script and any other relevant information.

If you have any further instructions or sections you'd like to add, feel free to do so!
