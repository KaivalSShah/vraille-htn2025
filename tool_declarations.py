# Tool declarations for function calling
# These define the function signatures that the AI can call

describe_image_declaration = {
    "name": "describe_image",
    "description": "Describe the image and return a detailed description of it",
    "parameters": {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "The path to the image file to describe"
            }
        },
        "required": ["image_path"],
    },
}

# Add more tool declarations here as you expand functionality
# Example for future tools:

# read_text_from_camera_declaration = {
#     "name": "read_text_from_camera",
#     "description": "Use camera to read text from books, signs, menus, etc.",
#     "parameters": {
#         "type": "object",
#         "properties": {},
#         "required": [],
#     },
# }

# identify_objects_declaration = {
#     "name": "identify_objects", 
#     "description": "Identify and locate objects in the camera view",
#     "parameters": {
#         "type": "object",
#         "properties": {},
#         "required": [],
#     },
# }

# get_current_location_declaration = {
#     "name": "get_current_location",
#     "description": "Get the user's current GPS coordinates and address",
#     "parameters": {
#         "type": "object",
#         "properties": {},
#         "required": [],
#     },
# }

# List of all available tool declarations
ALL_TOOL_DECLARATIONS = [
    describe_image_declaration,
    # Add new declarations to this list as you create them
]
