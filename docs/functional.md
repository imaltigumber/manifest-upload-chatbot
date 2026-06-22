# Project Overview
The AI-powered SDLC Platform is a web application that provides a floating chat console over a full dashboard. It is designed to facilitate client onboarding by collecting essential identity details and generating manifest files in various formats (Excel, Word, Text).

# Architecture
The project is structured into several modules, each responsible for a specific functionality:
- `app.py`: The main application file that sets up the Streamlit app and imports necessary modules.
- `modules/client_registry.py`: Manages a cross-session client registry.
- `modules/file_parser.py`: Parses uploaded manifest files and extracts field values.
- `modules/intents.py`: Defines intent definitions and per-intent question sets.
- `modules/manifest_generator.py`: Generates manifest files in various formats.
- `modules/session_manager.py`: Handles session state initialization, reset, and convenience helpers.
- `modules/validation.py`: Provides validation helpers for manifest field values.

# Modules
### `app.py`
- **Purpose**: Sets up the Streamlit app and imports necessary modules.
- **Key Functions**: Initializes the session state, sets up the page configuration, and syncs the active session into the cross-tab client registry.
- **Inputs/Outputs**: None

### `modules/client_registry.py`
- **Purpose**: Manages a cross-session client registry.
- **Key Functions**: Registers a client, retrieves all clients, gets a client by company name, and removes a client.
- **Inputs/Outputs**:
  - `register_client`: Takes `company_name`, `intent`, `step`, `version`, and `answers` as inputs.
  - `all_clients`: Returns a dictionary of all clients.
  - `get_client`: Takes `company_name` as input and returns the corresponding client record.
  - `remove_client`: Takes `company_name` as input and removes the corresponding client record.

### `modules/file_parser.py`
- **Purpose**: Parses uploaded manifest files and extracts field values.
- **Key Functions**: Parses an uploaded file and returns a dictionary of field values.
- **Inputs/Outputs**:
  - `parse_uploaded_file`: Takes `uploaded_file` and `questions` as inputs and returns a dictionary of field values.

### `modules/intents.py`
- **Purpose**: Defines intent definitions and per-intent question sets.
- **Key Functions**: None
- **Inputs/Outputs**: None

### `modules/manifest_generator.py`
- **Purpose**: Generates manifest files in various formats.
- **Key Functions**: Generates Excel, Word, and Text manifest files.
- **Inputs/Outputs**:
  - `generate_excel`: Takes `answers`, `questions`, `intent_name`, and `version` as inputs and returns the generated Excel file as bytes.
  - `generate_docx`: Takes `answers`, `questions`, `intent_name`, and `version` as inputs and returns the generated Word file as bytes.
  - `generate_txt`: Takes `answers`, `questions`, `intent_name`, and `version` as inputs and returns the generated Text file as bytes.

### `modules/session_manager.py`
- **Purpose**: Handles session state initialization, reset, and convenience helpers.
- **Key Functions**: Initializes the session state, resets the session state, adds a message to the chat history, pushes a manifest version, and loads a client record into the session state.
- **Inputs/Outputs**:
  - `init_session`: Initializes the session state.
  - `reset_session`: Resets the session state.
  - `add_message`: Takes `role` and `content` as inputs and adds a message to the chat history.
  - `push_manifest_version`: Takes `answers` as input and pushes a manifest version.
  - `load_client`: Takes `company_name` and `record` as inputs and loads a client record into the session state.

### `modules/validation.py`
- **Purpose**: Provides validation helpers for manifest field values.
- **Key Functions**: Validates email addresses and answers against question definitions.
- **Inputs/Outputs**:
  - `validate_email`: Takes `value` as input and returns a boolean indicating whether the email address is valid.
  - `validate_answers`: Takes `answers` and `questions` as inputs and returns a dictionary of error messages for invalid fields.

# Data Flow
The data flow of the application is as follows:
1. The user interacts with the chat console, providing input and receiving output.
2. The input is processed by the `app.py` file, which initializes the session state and sets up the page configuration.
3. The session state is managed by the `modules/session_manager.py` file, which handles initialization, reset, and convenience helpers.
4. The user's input is validated by the `modules/validation.py` file, which checks for valid email addresses and answers against question definitions.
5. The validated input is then used to generate manifest files in various formats by the `modules/manifest_generator.py` file.
6. The generated manifest files are then returned to the user through the chat console.

# Key Dependencies
The application relies on the following external libraries:
- `streamlit`: A Python library for building web applications.
- `openpyxl`: A Python library for working with Excel files.
- `docx`: A Python library for working with Word files.
- `re`: A Python library for working with regular expressions.