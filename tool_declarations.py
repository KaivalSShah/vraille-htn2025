# Tool declarations for function calling
# These define the function signatures that the AI can call

describe_image_declaration = {
    "name": "describe_image",
    "description": "Describe what you are seeing from the camera, and return a detailed description of it",
}

recognize_face_declaration = {
    "name": "recognize_face",
    "description": "Recognize the face of the person in the camera view",
}

read_text_declaration = {
    "name": "read_text",
    "description": "Read any text visible in the camera view - signs, menus, documents, labels, books, etc.",
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
    recognize_face_declaration,
    # Add new declarations to this list as you create them
]
