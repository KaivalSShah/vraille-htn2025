# Tool declarations for function calling
# These define the function signatures that the AI can call

describe_image_declaration = {
    "name": "describe_infront_of_me",
    "description": (
        "Use this function whenever the user asks about their surroundings, "
        "what is visible, or what is in front of the camera. "
        "Return a detailed description of everything in view."
    ),
}

recognize_face_declaration = {
    "name": "recognize_face",
    "description": (
        "Use this function whenever the user asks 'who is this person', "
        "'who am I looking at', or to identify/recognize a face in the camera. "
        "Return the person's identity if known, otherwise say unknown."
    ),
}

read_text_declaration = {
    "name": "read_text",
    "description": (
        "Use this function whenever the user asks to read, transcribe, or interpret "
        "any visible text in the camera view (signs, menus, documents, labels, books, screens, etc.)."
    ),
}

braille_mode_on_declaration = {
    "name": "braille_mode_on",
    "description": "Turn on braille mode for accessibility features. Returns True if braille mode is ON.",
}

braille_mode_off_declaration = {
    "name": "braille_mode_off",
    "description": "Turn off braille mode for accessibility features. Returns True if braille mode is OFF.",
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
    read_text_declaration,
    describe_image_declaration,
    recognize_face_declaration,
    braille_mode_on_declaration,
    braille_mode_off_declaration
    # Add new declarations to this list as you create them
]
