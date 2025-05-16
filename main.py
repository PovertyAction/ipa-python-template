import os

from box_sdk_gen import (
    BoxClient,
    BoxJWTAuth,
    JWTConfig,
)

config = os.environ.get("BOX_CONFIGURATION")
jwt_config = JWTConfig.from_config_json_string(config)
auth = BoxJWTAuth(config=jwt_config)
client = BoxClient(auth=auth)
service_account = client.users.get_user_me()
# print(f"Service Account: {service_account.name} ({service_account.id}), ({service_account.login})")


def search_box_recursively(folder_id, current_path="", found_files=None):
    """Recursively search through Box folders and return paths to all *.xls files.

    Args:
        folder_id: The Box folder ID to search
        current_path: Current path string for building full paths
        found_files: List to collect found XLS files

    Returns:
        List of paths to all *.xls files

    """
    if found_files is None:
        found_files = []

    items = client.folders.get_folder_items(folder_id=folder_id)
    for item in items.entries:
        item_path = f"{current_path}/{item.name}" if current_path else item.name

        if item.type == "folder":
            # Recursively process folders
            search_box_recursively(item.id, item_path, found_files)
        elif item.type == "file":  # noqa: SIM102
            # Check if the file is an XLS file
            if item.name.lower().endswith((".xls", ".xlsx")):
                found_files.append(
                    {
                        "path": item_path,
                        "id": item.id,
                        "name": item.name,
                        "size": getattr(item, "size", "Unknown"),
                    }
                )

    return found_files


# Start the recursive search from the specified folder
folder_id = 1509932719
xls_files = search_box_recursively(folder_id)

# Print all found XLS files with their paths
print(f"Found {len(xls_files)} Excel files:")
for file in xls_files:
    print(f"Path: {file['path']}, ID: {file['id']}, Size: {file['size']} bytes")
