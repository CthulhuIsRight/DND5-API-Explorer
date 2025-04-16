#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# dndapicli.py - Command-line interface for the D&D 5e API.
# Copyright (C) 2025 CthulhuIsRight  # Optional copyright line
# SPDX-License-Identifier: MIT

"""
Navigate the D&D 5e API JSON data from the command line.

This module provides a command-line interface (CLI) to interact with the
data exposed by the Dungeons & Dragons 5th Edition API
(https://www.dnd5eapi.co/).

It serves as an exercise in creating interactive Python applications
with argument parsing. It may be useful for Dungeon Masters needing quick
lookups or anyone curious about the D&D 5e rules data available via the API.

Example usage:
    python dndapicli.py spells fireball
    python dndapicli.py monsters --search goblin
"""

import argparse
import requests
import json
import sys
import shlex

# Base URL for the target API, in this case D&D5
API_BASE_URL = "https://www.dnd5eapi.co/api"


def fetch_available_endpoints(base_url):
    """Fetches the list of available top-level endpoints."""
    print(f"[*] Attempting to connect to API index at: {base_url}")
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            endpoints = list(data.keys())
            print(f"[*] Successfully fetched {len(endpoints)} endpoints.")
            endpoints.sort()
            return endpoints
        else:
            print(
                f"[!] Error: API base response at {base_url} was not a JSON "
                "object (dictionary).", file=sys.stderr
            )
            return None
    except requests.exceptions.Timeout:
        print(f"[!] Error: Connection to API index {base_url} timed out.",
              file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Error: Could not connect to API index {base_url}.",
              file=sys.stderr)
        print(f"    Details: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(
            f"[!] Error: Could not decode JSON response from API index "
            f"{base_url}.", file=sys.stderr
        )
        return None


def fetch_entity_list(base_url, entity_type):
    """Fetches the list of all entities of a given type."""
    url = f"{base_url}/{entity_type}"
    print(f"[*] Fetching list from: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        list_key = 'results'
        if list_key in data and isinstance(data[list_key], list):
            return data[list_key]
        else:
            if isinstance(data, list):
                print(
                    f"[*] Warning: Fetched list directly from {url} "
                    f"(no '{list_key}' key found).", file=sys.stderr
                )
                return data
            print(f"[!] Unexpected API response format for list at {url}",
                  file=sys.stderr)
            print(f"    Expected a JSON object with a '{list_key}' list.",
                  file=sys.stderr)
            return None
    except requests.exceptions.Timeout:
        print(f"[!] Request timed out while fetching list from {url}",
              file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching list: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"[!] Error decoding JSON response from {url}", file=sys.stderr)
        return None


def fetch_entity_data(base_url, entity_type, entity_name_or_index):
    """Fetches data for a specific entity from the API."""
    # Use the provided name directly, converting to lowercase slug for URL
    slug = str(entity_name_or_index).lower().replace(' ', '-')
    url = f"{base_url}/{entity_type}/{slug}"
    print(f"[*] Fetching details from: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"[!] Request timed out while fetching details from {url}",
              file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching details: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 404:
                # Use original name in error message for clarity
                print(
                    f"[!] Could not find {entity_type}: "
                    f"'{entity_name_or_index}' (tried slug: '{slug}').",
                    file=sys.stderr
                )
                print(
                    f"    You can list all {entity_type} by running: "
                    f"{entity_type}", file=sys.stderr
                )
            else:
                print(f"    Status Code: {e.response.status_code}",
                      file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"[!] Error decoding JSON response from {url}", file=sys.stderr)
        return None


def display_entity_list(entity_list, entity_type):
    """Displays a list of entity names/indices. Attempts common keys."""
    if not entity_list:
        print(f"No {entity_type} found or error fetching list.")
        return
    print(f"\n--- Available {entity_type.capitalize()} ---")
    name_key = 'name'
    index_key = 'index'
    url_key = 'url'
    items_displayed = 0
    for item in entity_list:
        if isinstance(item, dict):
            display_name = item.get(name_key, item.get(index_key))
            if not display_name and url_key in item:
                try:
                    parts = item[url_key].strip('/').split('/')
                    if len(parts) > 1 and parts[-1].isdigit():
                        display_name = f"ID: {parts[-1]}"
                    elif len(parts) > 0:
                        display_name = parts[-1]
                except Exception:
                    pass  # Ignore parsing errors for URL fallback
            if display_name:
                print(f"- {display_name}")
                items_displayed += 1
            else:
                # Fallback if no suitable key found
                print(f"- {item}")
                items_displayed += 1
        else:
            # Handle cases where the list contains non-dict items
            print(f"- {item}")
            items_displayed += 1
    if items_displayed == 0:
        print(
            f"Could not extract displayable names/indices from the "
            f"{entity_type} list."
        )
    print("-------------------------------\n")  # Removed f-string F541
    print(f"Use '{entity_type} <name_or_index>' to get details (JSON format).")


def display_help(available_endpoints):
    """Displays help information using the dynamically fetched endpoints."""
    print("\n--- Help ---")
    print(f"API Base URL: {API_BASE_URL}")
    print("Usage: <endpoint> [name_or_index ...]")  # Updated usage string
    print("\nAvailable Endpoints (fetched from API):")
    col_width = max(len(ep) for ep in available_endpoints) + 2
    cols = 3
    for i, ep in enumerate(available_endpoints):
        print(f"{ep:<{col_width}}", end="")
        if (i + 1) % cols == 0:
            print()
    if len(available_endpoints) % cols != 0:
        print()
    print("\nCommands:")
    print("  <endpoint>             : List all available items for that "
          "endpoint (e.g., 'monsters')")
    print("  <endpoint> <name ...>  : Show details for a specific item "
          "(output is raw JSON)")
    print("                         : Name can be multiple words "
          "(e.g., 'spells Acid Arrow')")
    print("  help                   : Show this help message.")
    print("  exit / quit / q        : Exit the application.")
    print("\nNote: Names/indices often match the list output "
          "(case-insensitive lookup attempted).")
    print("--- End Help ---\n")


# --- Main Execution ---

if __name__ == "__main__":
    # 1. Fetch available endpoints on startup
    available_endpoints = fetch_available_endpoints(API_BASE_URL)
    if available_endpoints is None:
        print(
            "\n[!] Critical Error: Could not initialize API endpoints. "
            "Exiting.", file=sys.stderr
        )
        sys.exit(1)

    # 3. Build the Parser
    parser = argparse.ArgumentParser(
        description='Interactive API JSON Navigator.',
        prog="",
        add_help=False
        )
    parser.add_argument(
        'entity_type',
        choices=available_endpoints,
        metavar='ENDPOINT',
        help='The API endpoint to query.'
    )
    parser.add_argument(
        'entity_name_parts',
        nargs=argparse.REMAINDER,  # Consume ALL remaining arguments
        metavar='NAME_OR_INDEX ...',  # Indicate multiple words possible
        help=('Optional: Specific item name/index (can be multiple words). '
              'If omitted, lists items.')
    )

    # --- Start Interactive Loop ---
    print("\n--- Interactive API Navigator ---")
    print("Type 'help' for instructions, 'exit' to quit.")

    while True:
        try:
            # Get user input
            user_input = input("> ").strip()
            if not user_input:
                continue

            # Check for custom commands
            cmd_lower = user_input.lower()
            if cmd_lower in ['exit', 'quit', 'q']:
                break
            if cmd_lower == 'help':
                display_help(available_endpoints)
                continue

            # Split input
            try:
                command_parts = shlex.split(user_input)
            except ValueError:
                print(f"[!] Error: Unmatched quotes in input: {user_input}",
                      file=sys.stderr)
                continue

            # Parse the input parts
            try:
                args = parser.parse_args(command_parts)
            except SystemExit:
                # Prevent argparse default SystemExit on --help or error
                continue
            except Exception as parse_err:
                print(f"[!] Error parsing command: {parse_err}",
                      file=sys.stderr)
                continue

            # Execute based on parsed arguments
            selected_endpoint = args.entity_type
            # Check if the list of name parts is empty or not
            # `args.entity_name_parts` will be [] if no name was given,
            # or ['Acid', 'Arrow'] etc.
            if not args.entity_name_parts:
                # List items for the endpoint (No name parts provided)
                entity_list = fetch_entity_list(API_BASE_URL,
                                                selected_endpoint)
                if entity_list is not None:
                    display_entity_list(entity_list, selected_endpoint)
            else:
                # Join the parts back into a single name string
                item_name = ' '.join(args.entity_name_parts)
                # Get specific item details using the joined name
                entity_data = fetch_entity_data(API_BASE_URL,
                                                selected_endpoint, item_name)
                if entity_data is not None:
                    # Use the reconstructed item_name in the header
                    print(f"\n--- Details for: {selected_endpoint}/{item_name}"
                          " (JSON) ---")
                    print(json.dumps(entity_data, indent=2))
                    print("-------------------------------------------\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break
        except Exception as loop_err:
            print(f"\n[!!!] An unexpected error occurred in the main loop: "
                  f"{loop_err}", file=sys.stderr)
            continue
