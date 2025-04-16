# DND5-API-Explorer
An interactive command-line interface (CLI) to navigate and explore the D&D JSON API dynamically.

## Features
*   Dynamically discovers API endpoints on startup.
*   Interactive shell (REPL) for querying endpoints.
*   Lists items available at a specified endpoint.
*   Displays full JSON details for a specific item.
*   Supports multi-word item names/indices.
*   Basic error handling for API requests.

## Installation
1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <repo-name>
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
3.  **Install dependencies within virtual enviroment:**
    ```bash
    pip install -r requirements.txt
    ```
## Usage
1.  **Activate the virtual environment** (if not already active).
2.  **Run the script:**
    ```bash
    python dndapicli.py
    ```
3.  Follow the prompts. Type `help` for commands. Examples:
    ```
    > monsters
    > spells Acid Arrow
    > help
    > exit
    ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
*   Uses the [requests](https://requests.readthedocs.io/en/latest/) library.
*   Example usage often demonstrated with the [D&D 5e API](https://www.dnd5eapi.co/).
*   Linting and PEP 8 regulation done via flake8