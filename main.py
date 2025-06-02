import json
import os

from box_sdk_gen import (
    BoxClient,
    BoxJWTAuth,
    JWTConfig,
)
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Constants for file paths
EXCEL_PATHS_FILE = "likely_surveys.txt"
CHECKPOINT_FILE = "box_scan_checkpoint.json"

config = os.environ.get("BOX_CONFIGURATION")
jwt_config = JWTConfig.from_config_json_string(config)
auth = BoxJWTAuth(config=jwt_config)
client = BoxClient(auth=auth)
service_account = client.users.get_user_me()
print(
    f"Service Account: {service_account.name} ({service_account.id}), ({service_account.login})"
)


def append_to_file(file_path, content):
    """Append content to a file."""
    with open(file_path, "a") as f:
        f.write(f"{content}\n")


def load_checkpoint():
    """Load checkpoint data if exists."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Checkpoint file corrupted, starting fresh")
    return {"processed_folders": [], "processed_files": [], "found_excel_count": 0}


def save_checkpoint(checkpoint_data):
    """Save checkpoint data."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint_data, f)


def load_existing_excel_files():
    """Load existing Excel files from the output file."""
    existing_files = set()
    if os.path.exists(EXCEL_PATHS_FILE):
        with open(EXCEL_PATHS_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    existing_files.add(line)
    return existing_files


def search_box_recursively(
    folder_id,
    current_path="",
    found_files=None,
    progress_bar=None,
    is_root=False,
    checkpoint=None,
):
    """Recursively search through Box folders and return paths to all *.xls files.

    Args:
        folder_id: The Box folder ID to search
        current_path: Current path string for building full paths
        found_files: List to collect found XLS files
        progress_bar: tqdm progress bar instance
        is_root: Whether this is the root folder (for progress tracking)
        checkpoint: Checkpoint data for resuming

    Returns:
        List of paths to all *.xls files

    """
    if found_files is None:
        found_files = []

    if checkpoint is None:
        checkpoint = {
            "processed_folders": [],
            "processed_files": [],
            "found_excel_count": 0,
        }

    # Skip already processed folders
    if str(folder_id) in checkpoint["processed_folders"]:
        if progress_bar and is_root:
            progress_bar.write(
                f"Skipping already processed folder: {current_path or 'Root'}"
            )
            progress_bar.update(1)
        return found_files

    items = client.folders.get_folder_items(folder_id=folder_id)

    # Process items
    for item in items.entries:
        item_path = f"{current_path}/{item.name}" if current_path else item.name
        item_id = str(item.id)  # Convert to string for JSON compatibility

        # Skip already processed files
        if item_id in checkpoint["processed_files"]:
            if progress_bar:
                progress_bar.write(f"Skipping already processed: {item_path}")
            continue

        # Use tqdm.write for logging - doesn't interfere with progress bar
        if item.type == "folder":
            if progress_bar:
                progress_bar.write(f"Processing folder: {item_path}")
        else:
            if progress_bar:
                progress_bar.write(f"Processing file: {item_path}")

        if progress_bar and is_root:
            progress_bar.update(1)
            progress_bar.set_description(
                f"Current: {item.name[:30]}{'...' if len(item.name) > 30 else ''}"
            )

        if item.type == "folder":
            # Recursively process folders, pass progress bar for messages but not progress
            search_box_recursively(
                item.id, item_path, found_files, progress_bar, False, checkpoint
            )

            # Mark folder as processed after processing all its contents
            checkpoint["processed_folders"].append(item_id)
            save_checkpoint(checkpoint)

        elif item.type == "file":  # noqa: SIM102
            # Check if the file is an XLS file
            if item.name.lower().endswith((".xls", ".xlsx")):
                if progress_bar:
                    progress_bar.write(f"Found Excel file: {item_path}")

                # Add to results
                found_files.append(
                    {
                        "path": item_path,
                        "id": item_id,
                        "name": item.name,
                        "size": getattr(item, "size", "Unknown"),
                    }
                )

                # Save the path to file immediately
                append_to_file(EXCEL_PATHS_FILE, item_path)

                # Update checkpoint count
                checkpoint["found_excel_count"] += 1

            # Mark file as processed
            checkpoint["processed_files"].append(item_id)

            # Save checkpoint periodically (every 10 files)
            if len(checkpoint["processed_files"]) % 10 == 0:
                save_checkpoint(checkpoint)

    # Mark this folder as processed if it's the root folder and not already in the list
    if is_root and str(folder_id) not in checkpoint["processed_folders"]:
        checkpoint["processed_folders"].append(str(folder_id))
        save_checkpoint(checkpoint)

    return found_files


# Start the recursive search from the specified folder
folder_id = 251883083502  # AIT project  # 1509932719 # CP projects

# Load checkpoint data
checkpoint = load_checkpoint()
existing_excel_files = load_existing_excel_files()

# Initialize Excel paths file if it doesn't exist
if not os.path.exists(EXCEL_PATHS_FILE):
    with open(EXCEL_PATHS_FILE, "w") as f:
        f.write("# Box Excel file paths\n")
        f.write("# Format: path\n")

# Check if we're resuming from a previous scan
if checkpoint["processed_folders"] or checkpoint["processed_files"]:
    print(
        f"Resuming from checkpoint: {len(checkpoint['processed_folders'])} folders and {len(checkpoint['processed_files'])} files already processed"
    )
    print(f"Already found {checkpoint['found_excel_count']} Excel files")
else:
    print("Starting fresh scan")

# Get first-level items for progress tracking
print("Getting first-level items...")
root_items = client.folders.get_folder_items(folder_id=folder_id)
total_items = len(root_items.entries)
print(f"Found {total_items} items in root folder")

# Count how many root items we've already processed
root_item_ids = [str(item.id) for item in root_items.entries]
completed_root_items = sum(
    1
    for item_id in root_item_ids
    if item_id in checkpoint["processed_folders"]
    or item_id in checkpoint["processed_files"]
)
remaining_items = total_items - completed_root_items

print(f"Already processed {completed_root_items} of {total_items} root items")

# Create progress bar only for first-level items, initialize with already completed items
with tqdm(total=total_items, initial=completed_root_items, unit="items") as pbar:
    xls_files = search_box_recursively(
        folder_id, progress_bar=pbar, is_root=True, checkpoint=checkpoint
    )

# Print all found XLS files with their paths
print(f"\nFound {len(xls_files)} new Excel files in this scan")
print(
    f"Total Excel files found (including previous runs): {checkpoint['found_excel_count']}"
)
print(f"Excel file paths have been saved to: {EXCEL_PATHS_FILE}")
