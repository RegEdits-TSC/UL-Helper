# Standard Library Imports
import json  # For handling JSON data
import os  # For operating system interactions
import sys  # For system-specific parameters and functions
import re  # For regular expressions
import platform  # For platform-specific information
import time  # For time-related functions
import random  # For generating random numbers
import logging  # For logging messages
import shutil  # For high-level file operations
import glob  # For filename pattern matching
import subprocess  # For spawning new processes
import traceback  # For extracting, formatting, and printing stack traces
import asyncio  # For asynchronous programming
import multiprocessing  # For process-based parallelism
from pathlib import Path  # For filesystem paths
from urllib.parse import urlparse, parse_qs  # For URL parsing
from difflib import SequenceMatcher  # For comparing sequences

# Third-Party Imports
import requests  # For making HTTP requests
from packaging.version import Version  # For comparing versions
import bencodepy as bencode  # For Bencode encoding/decoding
from rich.markdown import Markdown  # For rendering Markdown
from rich.style import Style  # For styling Rich text
from rich.prompt import Prompt, Confirm  # For user prompts
from rich.text import Text  # For Rich text handling
from rich.panel import Panel  # For creating panels
from rich.table import Table  # For creating tables
from rich.align import Align  # For text alignment
from rich.rule import Rule  # For creating rules
from rich.console import Group  # For grouping Rich elements
from rich.progress import Progress, TimeRemainingColumn  # For progress bars and timers

# Custom Imports
from src.args import Args  # Custom module, likely for argument parsing
from src.clients import Clients  # Custom module, likely for client handling
from src.prep import Prep  # Custom module, likely for preparation steps
from src.trackers.COMMON import COMMON  # Custom module, common tracker functionalities
from src.console import console  # Custom module, likely for console operations
import importlib  # For dynamic imports

####################################
#######  Tracker List Here   #######
### Add below + api or http list ###
####################################

# List of tracker names used in the project
tracker_list = [
    'ACM', 'AITHER', 'ANT', 'BHD', 'BHDTV', 'BLU', 'FL', 'FNP', 'HDB', 'HDT', 'HUNO', 'JPTV', 
    'LCD', 'LDU', 'LST', 'LT', 'MB', 'MTV', 'NBL', 'OE', 'OINK', 'OTW', 'PTER', 'PTT', 'R4E', 
    'RF', 'RTF', 'SN', 'STC', 'TDC', 'TL', 'TTG', 'TTR', 'ULCX', 'UTP', 'VHD'
]

# Creates a dictionary mapping each tracker name to its class from src.trackers module
# Assumes each tracker has a corresponding module in src.trackers and the module's name is the same as the tracker
tracker_class_map = {
    tracker: getattr(importlib.import_module(f"src.trackers.{tracker}"), tracker) 
    for tracker in tracker_list
}

# Trackers using API-based interaction
api_trackers = [
    'ACM', 'AITHER', 'ANT', 'BHD', 'BHDTV', 'BLU', 'FNP', 'HUNO', 'JPTV', 'LCD', 'LDU', 'LST', 
    'LT', 'MB', 'NBL', 'OE', 'OINK', 'OTW', 'PTT', 'RF', 'R4E', 'RTF', 'SN', 'STC', 'TDC', 
    'TTR', 'ULCX', 'UTP', 'VHD'
]

# Trackers using HTTP-based interaction
http_trackers = [
    'FL', 'HDB', 'HDT', 'MTV', 'PTER', 'TTG'
]

############# EDITING BELOW THIS LINE MAY RESULT IN SCRIPT BREAKING #############

# Determine the path to the Python 3 executable
python3_path = shutil.which("python3")
python_cmd = python3_path if python3_path else "python" 

# Set up directory paths
base_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(base_dir, 'data')
config_path = os.path.abspath(os.path.join(data_dir, 'config.py'))
old_config_path = os.path.abspath(os.path.join(data_dir, 'backup', 'old_config.py'))
minimum_version = Version('1.0.0')

def get_backup_name(path, suffix='_bu'):
    """
    Generate a unique backup file name by appending a suffix and a counter.
    
    :param path: The base path for the backup file.
    :param suffix: The suffix to append before the counter.
    :return: A unique backup file name.
    """
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{base}{suffix}{counter}{ext}"
        counter += 1
    return path

# Check if the configuration file exists
if not os.path.exists(config_path):  
    console.print("[bold red] It appears you have no config file, please ensure to configure and place `/data/config.py`")
    exit()

try:
    # Attempt to import the configuration
    from data.config import config 
except ImportError as e:
    # Handle import errors and exit
    console.print(f"[bold red]Error importing config: {str(e)}[/bold red]")
    exit()

def reconfigure():
    """
    Reconfigure the application by backing up the old configuration, 
    running a reconfiguration script, and checking the outcome.
    """
    console.print("[bold red]WARN[/bold red]: Version out of date, automatic upgrade in progress")
    
    try:
        # Backup old configuration if it exists
        if os.path.exists(old_config_path):
            backup_name = get_backup_name(old_config_path)
            shutil.move(old_config_path, backup_name)
        # Move current config to old config path
        shutil.move(config_path, old_config_path)
    except Exception as e:
        console.print("[bold red]ERROR[/bold red]: Unable to proceed with automatic upgrade. Please rename `config.py` to `old_config.py`, move it to 'data/backup`, and run `python3 data/reconfig.py`")
        console.print(f"Error: {str(e)}")
        exit()

    # Run the reconfiguration script
    result = subprocess.run(
        [python_cmd, os.path.join(data_dir, "reconfig.py"), "--output-dir", data_dir],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        console.print(f"[bold red]Error during reconfiguration: {result.stderr}[/bold red]")
        exit()

    # Check if the new config file was created successfully
    if os.path.exists(config_path):
        console.print("[bold green]Congratulations! config.py was successfully updated.[/bold green]")
    else:
        console.print("[bold][red]ERROR[/red]: config.py not found in the expected directory after reconfiguration.[/bold]")
        exit()

    # Final messages to the user
    console.print("Please double-check new config and ensure client settings were appropriately set.")
    console.print("[bold yellow]WARN[/bold yellow]: After verification of config, rerun command.")
    console.print("[dim green]Thanks for using Uploadrr :)")
    exit()
    
# Check if 'version' key is in config and if it's less than the minimum required version
if 'version' not in config or Version(config.get('version')) < minimum_version:
    reconfigure()  # Function to handle reconfiguration if version is outdated

try:
    # Attempt to import example_config and check if its version is newer than the current config's version
    from data.backup import example_config
    if 'version' in example_config.config and Version(example_config.config.get('version')) > Version(config.get('version')):
        console.print("[bold yellow]WARN[/bold yellow]: Config version out of date, updating is recommended.")
        console.print("[bold yellow]WARN[/bold yellow]: Simply pass --reconfig")
except Exception as e:
    # Handle errors during import or version checking
    console.print(f"[bold red]Error: {str(e)}[/bold red]")

# Initialize Clients and Args with the current configuration
client = Clients(config=config)
parser = Args(config)

async def do_the_thing(base_dir):
    # Print a banner (assumed to be a function that displays some introductory text)
    print_banner()
    
    # Initialize metadata dictionary and add the base directory to it
    meta = {'base_dir': base_dir}
    
    # Collect paths from command-line arguments, ensuring they exist
    paths = []
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            paths.append(os.path.abspath(arg))
        else:
            # Stop processing further if any path does not exist
            break
    
    # Reconfigure settings if 'reconfig' is set in meta
    if meta.get("reconfig", False):
        reconfigure()
    
    # Parse command-line arguments and update meta dictionary
    meta, help_text, before_args = parser.parse(
        tuple(' '.join(sys.argv[1:]).split(' ')), meta
    )
    
    # Cleanup temporary directory if 'cleanup' is true and directory exists
    tmp_dir = os.path.join(base_dir, 'tmp')
    if meta.get('cleanup', False) and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
        # Notify user of successful cleanup
        console.print("[bold green]Successfully emptied the tmp directory...")
        
    # Check if auto-queuing is enabled
    if meta.get('auto_queue'):
        directory = meta['auto_queue']
        if os.path.isdir(directory):
            queue = list_directory(directory)  # Function to list files in the directory
            if meta.get('show_queue') or meta.get('debug'):
                md_text = "\n - ".join(queue)
                console.print("\n[bold green]Automatically queuing these files:[/bold green]", end='')
                console.print(Markdown(f"- {md_text.rstrip()}\n\n", style=Style(color='cyan')))
            console.print(f"\nUnique uploads queued: [bold cyan]{len(queue)}[/bold cyan]")
        else:
            console.print(f"[red]Directory: [bold red]{directory}[/bold red] does not exist")
            exit(1)
    else:
        # Handle manual queuing
        if not meta.get('path'):
            exit(0)
        
        path = os.path.abspath(meta['path'])
        
        # Remove trailing quote if present
        if path.endswith('"'):
            path = path[:-1]
        
        if os.path.exists(path):
            meta, help_text, before_args = parser.parse(
                tuple(' '.join(sys.argv[1:]).split(' ')), meta
            )
            queue = [path]
        else:
            # Handle pattern matching if path does not exist
            directory_exists = os.path.exists(os.path.dirname(path))
            if directory_exists and len(paths) <= 1:
                escaped_path = path.replace('[', '[[]')
                queue = glob.glob(escaped_path)
                if queue:
                    if meta.get('show_queue') or meta.get('debug'):
                        md_text = "\n - ".join(queue)
                        console.print("\n[bold green]Queuing these files:[/bold green]", end='')
                        console.print(Markdown(f"- {md_text.rstrip()}\n\n", style=Style(color='cyan')))
                    console.print(f"\nUnique Uploads Queued: [bold cyan]{len(queue)}[/bold cyan]\n")
                else:
                    console.print(f"[red]Path: [bold red]{path}[/bold red] does not exist")
            elif directory_exists and len(paths) != 1:
                queue = paths
                if meta.get('show_queue') or meta.get('debug'):
                    md_text = "\n - ".join(queue)
                    console.print("\n[bold green]Queuing these files:[/bold green]", end='')
                    console.print(Markdown(f"- {md_text.rstrip()}\n\n", style=Style(color='cyan')))
                console.print(f"\nUnique uploads queued: [bold cyan]{len(queue)}[/bold cyan]\n")
            else:
                # Handle cases where the directory doesn't exist and path needs splitting
                split_path = path.split()
                queue = []
                p1 = split_path[0]
                for i, each in enumerate(split_path):
                    try:
                        next_path = f"{p1} {split_path[i+1]}"
                        if os.path.exists(p1) and not os.path.exists(next_path):
                            queue.append(p1)
                            p1 = split_path[i+1]
                        else:
                            p1 += f" {split_path[i+1]}"
                    except IndexError:
                        if os.path.exists(p1):
                            queue.append(p1)
                        else:
                            console.print(f"[red]Path: [bold red]{p1}[/bold red] does not exist")
                
                if queue:
                    if meta.get('show_queue') or meta.get('debug'):
                        md_text = "\n - ".join(queue)
                        console.print("\n[bold green]Queuing these files:[/bold green]", end='')
                        console.print(Markdown(f"- {md_text.rstrip()}\n\n", style=Style(color='cyan')))
                    console.print(f"\nTotal items queued: [bold cyan]{len(queue)}[/bold cyan]\n")
                else:
                    console.print("[red]No valid files were queued. Please check your path and try again.[/red]")
                    exit(1) 

    # Retrieve delay settings, defaulting to 0 if not specified
    delay = meta.get('delay', 0) or config['AUTO'].get('delay', 0)

    # Create a copy of meta for use in processing
    base_meta = dict(meta)  # Simplified copy creation

    # Initialize counters and lists for tracking progress
    total_files = len(queue)  # Total number of files in the queue
    successful_uploads = 0  # Counter for successful uploads
    skipped_files = 0  # Counter for skipped files
    skipped_details = []  # List to store details of skipped files
    skipped_tmdb_files = []  # List to store details of skipped TMDB files
    current_file = 1  # Counter to track the current file being processed

    # Sort or shuffle the queue based on user preferences
    if meta.get('random'):
        # Shuffle queue randomly if 'random' key is set in meta
        random.shuffle(queue)
    elif meta.get('auto_queue'):
        # Sort queue in case-insensitive order if 'auto_queue' key is set in meta
        queue = sorted(queue, key=str.lower)
        
    # Iterate over each path in the queue
    for path in queue:
        # Create a copy of the base_meta dictionary and update with the current path
        meta = dict(base_meta)
        meta['path'] = path
        meta['uuid'] = None

        # Define a list of keys to be overwritten if present in saved_meta
        overwrite_keys = [
            'path', 'trackers', 'dupe', 'debug', 'anon', 'category', 'type', 'screens', 
            'nohash', 'manual_edition', 'imdb', 'tmdb_manual', 'mal', 'manual', 'hdb', 
            'ptp', 'blu', 'no_season', 'no_aka', 'no_year', 'no_dub', 'no_tag', 'no_seed', 
            'client', 'desclink', 'descfile', 'desc', 'draft', 'region', 'freeleech', 
            'personalrelease', 'unattended', 'season', 'episode', 'torrent_creation', 
            'qbit_tag', 'qbit_cat', 'skip_imghost_upload', 'imghost', 'manual_source', 
            'webdv', 'hardcoded-subs'
        ]

        # Attempt to load existing metadata from a file
        meta_file_path = f"{base_dir}/tmp/{os.path.basename(path)}/meta.json"
        try:
            with open(meta_file_path, 'r') as f:
                saved_meta = json.load(f)
                # Update saved_meta with values from meta if they differ and are in the overwrite list
                for key in overwrite_keys:
                    if key in saved_meta and meta.get(key) != saved_meta[key]:
                        saved_meta[key] = meta[key]
                meta = saved_meta
        except FileNotFoundError:
            # If the file does not exist, continue without updating meta
            pass

        # Print the current processing status
        console.print(Align.center(f"\n\n————————— Upload Helper is processing # [bold bright_cyan]{current_file}[/bold bright_cyan] of [bold bright_magenta]{total_files}[/bold bright_magenta] —————————"))

        # Handle delay if specified
        if delay > 0:
            with Progress("[progress.description]{task.description}", TimeRemainingColumn(), transient=True) as progress:
                task = progress.add_task("[cyan]Auto delay...", total=delay)
                for i in range(delay):
                    await asyncio.sleep(1)
                    progress.update(task, advance=1)

        # Print information gathering status
        console.print(f"[green]Gathering info for {os.path.basename(path)}")

        # Set default image host if not provided
        if meta['imghost'] is None:
            meta['imghost'] = config['DEFAULT']['img_host_1']

        # Notify if running in auto mode
        if meta['unattended']:
            console.print("[yellow]Running in Auto Mode")

        # Increment the current file counter
        current_file += 1

        # Initialize the Prep object and gather preparation data
        prep = Prep(screens=meta.get('screens', 3), img_host=meta.get('imghost', 'imgbox'), config=config)
        meta = await prep.gather_prep(meta=meta, mode='cli')

        # Gather TMDb ID
        if meta.get('tmdb_not_found'):
            skipped_files += 1
            skipped_tmdb_files.append(path)
            continue

        try:
            # Retrieve name details
            meta['name_notag'], meta['name'], meta['clean_name'], meta['potential_missing'] = await prep.get_name(meta)
            
            # Ensure all name values are present
            if any(val is None for val in (meta['name_notag'], meta['name'], meta['clean_name'], meta['potential_missing'])):
                raise ValueError("Name values are None")
        except Exception as e:
            # Handle errors during name retrieval
            skipped_files += 1
            skipped_details.append((path, f'Error getting name: {str(e)}'))
            continue

        # Handle image list and upload
        if meta.get('image_list', False) in (False, []) and meta.get('skip_imghost_upload', False) == False:
            return_dict = {}
            meta['image_list'], dummy_var = prep.upload_screens(meta, meta['screens'], 1, 0, meta['screens'], [], return_dict)
            
            # Print image list if debugging
            if meta['debug']:
                console.print(meta['image_list'])
            # meta['uploaded_screens'] = True
        elif meta.get('skip_imghost_upload', False) and not meta.get('image_list', False):
            meta['image_list'] = []
            
        # Check if the base torrent file exists
        if not os.path.exists(os.path.abspath(f"{meta['base_dir']}/tmp/{meta['uuid']}/BASE.torrent")):
            reuse_torrent = None
            
            # If 'rehash' is not set, try to find an existing torrent to reuse
            if not meta.get('rehash', False):
                reuse_torrent = await client.find_existing_torrent(meta)
                
                # If an existing torrent is found, create a base from it
                if reuse_torrent is not None:
                    prep.create_base_from_existing_torrent(reuse_torrent, meta['base_dir'], meta['uuid'])
            
            # If no hash is required and no existing torrent was found, create a new torrent
            if not meta['nohash'] and reuse_torrent is None:
                prep.create_torrent(meta, Path(meta['path']), "BASE", meta.get('piece_size_max', 0))
            
            # If hashing is not required, set the client to "none"
            if meta['nohash']:
                meta['client'] = "none"
        
        # If the base torrent file exists and rehash is enabled, create a new torrent
        elif os.path.exists(os.path.abspath(f"{meta['base_dir']}/tmp/{meta['uuid']}/BASE.torrent")) and meta.get('rehash', False) is True and meta['nohash'] is False:
            prep.create_torrent(meta, Path(meta['path']), "BASE", meta.get('piece_size_max', 0))
        
        # If randomization is enabled, create random torrents
        if int(meta.get('randomized', 0)) >= 1:
            prep.create_random_torrents(meta['base_dir'], meta['uuid'], meta['randomized'], meta['path'])

        # Determine the list of trackers to use, defaulting to configuration if not provided
        if meta.get('trackers', None) is not None:
            trackers = meta['trackers']
        else:
            trackers = config['TRACKERS']['default_trackers']
        
        # Split trackers into a list if they are comma-separated
        if "," in trackers:
            trackers = trackers.split(',')
        
        # Save the updated meta information to a JSON file
        with open(f"{meta['base_dir']}/tmp/{meta['uuid']}/meta.json", 'w') as f:
            json.dump(meta, f, indent=4)
        
        # Get user confirmation for the current meta information
        confirm = get_confirmation(meta)
        
        # Loop until valid confirmation is received or user decides to skip
        while not confirm:
            # Display instructions for editing meta information
            console.print("Input args that need correction e.g.(--tag NTb --category tv --tmdb 12345)")
            console.print("Enter 'skip' if no correction needed", style="dim")
            
            # Prompt user for input
            editargs = Prompt.ask("")
            
            # If user chooses to skip, exit the loop
            if editargs.lower() == 'skip':
                break
            
            # Validate user input
            elif editargs == '':
                console.print("Invalid input. Please try again or type 'skip' to pass.", style="dim")
            else:
                # Prepare arguments for parsing
                editargs = (meta['path'],) + tuple(editargs.split())
                if meta['debug']:
                    editargs = editargs + ("--debug",)
                
                # Parse the new arguments and update meta information
                meta, help, before_args = parser.parse(editargs, meta)
                meta['edit'] = True
                meta = await prep.gather_prep(meta=meta, mode='cli')
                meta['name_notag'], meta['name'], meta['clean_name'], meta['potential_missing'] = await prep.get_name(meta)
                
                # Recheck confirmation with updated meta information
                confirm = get_confirmation(meta)
                
                # Exit loop if confirmation is received
                if confirm:
                    break

        # Ensure trackers is a list, even if a single string was provided
        if not isinstance(trackers, list):
            trackers = [trackers]
        
        # Strip whitespace and convert all tracker names to uppercase
        trackers = [s.strip().upper() for s in trackers]
        
        # If 'manual' flag is set in meta, add "MANUAL" to the beginning of the trackers list
        if meta.get('manual', False):
            trackers.insert(0, "MANUAL")
        
        # Print a message indicating the path currently being processed
        console.print(f"Processing: [bold cyan]{path}[/bold cyan]")
        
        # Initialize a COMMON object with the provided configuration
        common = COMMON(config=config)

        
        
        
        
        
        
        
        





        # Iterate through each tracker in the list
        for tracker in trackers:
            # Remove 'DUPE?' from the end of the meta name if present
            if meta['name'].endswith('DUPE?'):
                meta['name'] = meta['name'].replace(' DUPE?', '')
            
            # Clean and format the tracker name
            tracker = tracker.replace(" ", "").upper().strip()
            
            # Set debug flag for logging purposes
            debug = "(DEBUG)" if meta['debug'] else ""

            # Check if the tracker is in the list of API-supported trackers
            if tracker in api_trackers:
                # Initialize the tracker class using the tracker_class_map
                tracker_class = tracker_class_map[tracker](config=config)
                
                # Determine if upload should proceed based on the unattended flag
                if meta['unattended']:
                    upload_to_tracker = True
                else:
                    upload_to_tracker = Confirm.ask(f"Upload to {tracker_class.tracker}? {debug}")
                
                # If upload is confirmed, print the upload message; otherwise, log the skip and continue
                if upload_to_tracker:
                    console.print(f"Uploading to {tracker_class.tracker}")
                else:
                    upload_to_tracker = False
                    skipped_files += 1
                    skipped_details.append((path, f"User skipped Upload on {tracker_class.tracker}"))
                    continue
                
                # Check if the tracker is banned or has banned groups
                if check_banned_group(tracker_class.tracker, tracker_class.banned_groups, meta, skipped_details, path):
                    skipped_files += 1
                    skipped_details.append((path, f"Banned Group on {tracker_class.tracker}"))
                    continue
                
                # Search for existing items on the tracker and filter duplicates
                dupes = await tracker_class.search_existing(meta)
                dupes = await common.filter_dupes(dupes, meta)
                meta, skipped = dupe_check(dupes, meta, config, skipped_details, path)
                
                # If duplicate check indicates a skip, log it and continue
                if skipped:
                    skipped_files += 1
                    skipped_details.append((path, f"Potential duplicate on {tracker_class.tracker}"))
                    continue
                
                # If upload is confirmed, perform the upload
                if meta['upload']:
                    # Perform the upload and handle success or failure
                    upload_success = await tracker_class.upload(meta)
                    if upload_success:
                        if tracker == 'SN':
                            await asyncio.sleep(16)  # Delay specific to 'SN' tracker
                        await client.add_to_client(meta, tracker_class.tracker)
                        successful_uploads += 1
                    else:
                        skipped_files += 1
                        skipped_details.append((path, f"{tracker_class.tracker} Rejected Upload"))


                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
            
            if tracker in http_trackers:
                tracker_class = tracker_class_map[tracker](config=config)
                if meta['unattended']:
                    upload_to_tracker = True
                else:
                    upload_to_tracker = Confirm.ask(f"Upload to {tracker_class.tracker}? {debug}", choices=["y", "N"])
                if upload_to_tracker:
                    console.print(f"Uploading to {tracker}")
                    if check_banned_group(tracker_class.tracker, tracker_class.banned_groups, meta, skipped_details, path):
                        skipped_files += 1
                        skipped_details.append((path, f"Banned group on {tracker_class.tracker}"))                        
                        continue
                    if await tracker_class.validate_credentials(meta):
                        dupes = await tracker_class.search_existing(meta)
                        dupes = await common.filter_dupes(dupes, meta)
                        meta, skipped = dupe_check(dupes, meta)
                        if skipped:
                            skipped_files += 1
                            skipped_details.append((path, tracker))
                            continue
                        if meta['upload']:
                            await tracker_class.upload(meta)
                            await client.add_to_client(meta, tracker_class.tracker)
                            successful_uploads += 1

            if tracker == "MANUAL":
                if meta['unattended']:
                    do_manual = True
                else:
                    do_manual = Confirm.ask("Get files for manual upload?", default=True)
                if do_manual:
                    for manual_tracker in trackers:
                        if manual_tracker != 'MANUAL':
                            manual_tracker = manual_tracker.replace(" ", "").upper().strip()
                            tracker_class = tracker_class_map[manual_tracker](config=config)
                            if manual_tracker in api_trackers:
                                await common.unit3d_edit_desc(meta, tracker_class.tracker, tracker_class.signature)
                            else:
                                await tracker_class.edit_desc(meta)
                    url = await prep.package(meta)
                    if not url:
                        console.print(f"[yellow]Unable to upload prep files, they can be found at `tmp/{meta['uuid']}")
                    else:
                        console.print(f"[green]{meta['name']}")
                        console.print(f"[green]Files can be found at: [yellow]{url}[/yellow]")  

            if tracker == "BHD":
                bhd = BHD(config=config)
                draft_int = await bhd.get_live(meta)
                draft = "Draft" if draft_int == 0 else "Live"
                if meta['unattended']:
                    upload_to_bhd = True
                else:
                    upload_to_bhd = Confirm.ask(f"Upload to BHD? ({draft}) {debug}")
                if upload_to_bhd:
                    console.print("Uploading to BHD")
                    if check_banned_group("BHD", bhd.banned_groups, meta, skipped_details, path):
                        skipped_files += 1
                        skipped_details.append((path, f"Banned group on {tracker_class.tracker}")) 
                        continue
                    dupes = await bhd.search_existing(meta)
                    dupes = await common.filter_dupes(dupes, meta)
                    meta, skipped = dupe_check(dupes, meta)
                    if skipped:
                        skipped_files += 1
                        skipped_details.append((path, tracker))
                        continue
                    if meta['upload']:
                        await bhd.upload(meta)
                        await client.add_to_client(meta, "BHD")
                        successful_uploads += 1
            
            if tracker == "THR":
                if meta['unattended']:
                    upload_to_thr = True
                else:
                    upload_to_thr = Confirm.ask(f"Upload to THR? {debug}")
                if upload_to_thr:
                    console.print("Uploading to THR")
                    def is_valid_imdb_id(imdb_id):
                        return re.match(r'tt\d{7}', imdb_id) is not None
                    if meta.get('imdb_id', '0') == '0':
                        while True:
                            imdb_id = Prompt.ask("Please enter a valid IMDB id (e.g., tt1234567)")
                            if is_valid_imdb_id(imdb_id):
                                meta['imdb_id'] = imdb_id.replace('tt', '').zfill(7)
                                break
                            else:
                                print("Invalid IMDB id. Please try again.")
                    def get_youtube_id(url):
                        parsed_url = urlparse(url)
                        if "youtube.com" in parsed_url.netloc:
                            if "watch" in parsed_url.path:
                                video_id = parse_qs(parsed_url.query).get('v', None)
                                if video_id:
                                    return video_id[0]
                        return None

                    if meta.get('youtube', None) is None:
                        while True:
                            youtube = Prompt.ask("Unable to find youtube trailer, please link one\n[dim] e.g.(https://www.youtube.com/watch?v=dQw4w9WgXcQ or dQw4w9WgXcQ)[/dim]")
                            video_id = get_youtube_id(youtube)
                            if video_id is not None:
                                meta['youtube'] = video_id
                                break
                            else:
                                print("Invalid YouTube URL or ID. Please enter a valid full URL.")
                    thr = THR(config=config)
                    try:
                        with requests.Session() as session:
                            console.print("[yellow]Logging in to THR")
                            session = thr.login(session)
                            console.print("[yellow]Searching for Dupes")
                            dupes = thr.search_existing(session, meta.get('imdb_id'))
                            dupes = await common.filter_dupes(dupes, meta)
                            meta, skipped = dupe_check(dupes, meta)
                            if skipped:
                                skipped_files += 1
                                skipped_details.append((path, tracker))
                                continue
                            if meta['upload']:
                                await thr.upload(session, meta)
                                await client.add_to_client(meta, "THR")
                                successful_uploads += 1
                    except:
                        console.print(traceback.print_exc())

            if tracker == "PTP":
                if meta['unattended']:
                    upload_to_ptp = True
                else:
                    upload_to_ptp = Confirm.ask(f"Upload to {tracker}? {debug}")
                if upload_to_ptp:
                    console.print(f"Uploading to {tracker}")
                    def is_valid_imdb_id(imdb_id):
                        # Check if the imdb_id matches the pattern tt followed by 7 digits
                        return re.match(r'tt\d{7}', imdb_id) is not None

                    if meta.get('imdb_id', '0') == '0':
                        while True:
                            imdb_id = Prompt.ask("Please enter a valid IMDB id (e.g., tt1234567)")
                            if is_valid_imdb_id(imdb_id):
                                meta['imdb_id'] = imdb_id.replace('tt', '').zfill(7)
                                break
                            else:
                                print("Invalid IMDB id. Please try again.")
                    ptp = PTP(config=config)
                    if check_banned_group(tracker_class.tracker, tracker_class.banned_groups, meta, skipped_details, path):
                        skipped_files += 1
                        skipped_details.append((path, f"Banned group on {tracker_class.tracker}"))                                          
                        continue
                    try:
                        console.print("[yellow]Searching for Group ID")
                        groupID = await ptp.get_group_by_imdb(meta['imdb_id'])
                        if groupID is None:
                            console.print("[yellow]No Existing Group found")
                            def get_youtube_id(url):
                                parsed_url = urlparse(url)
                                if "youtube.com" in parsed_url.netloc:
                                    if "watch" in parsed_url.path:
                                        video_id = parse_qs(parsed_url.query).get('v', None)
                                        if video_id:
                                            return video_id[0]
                                return None

                            if meta.get('youtube', None) is None:
                                while True:
                                    youtube = Prompt.ask("Unable to find youtube trailer, please link one\n[dim] e.g.(https://www.youtube.com/watch?v=dQw4w9WgXcQ or dQw4w9WgXcQ)[/dim]")
                                    video_id = get_youtube_id(youtube)
                                    if video_id is not None:
                                        meta['youtube'] = video_id
                                        break
                                    else:
                                        print("Invalid YouTube URL or ID. Please enter a valid full URL.")
                            meta['upload'] = True
                        else:
                            console.print("[yellow]Searching for Existing Releases")
                            dupes = await ptp.search_existing(groupID, meta)
                            dupes = await common.filter_dupes(dupes, meta)
                            meta, skipped = dupe_check(dupes, meta)
                            if skipped:
                                skipped_files += 1
                                skipped_details.append((path, tracker))
                                continue
                        if meta.get('imdb_info', {}) == {}:
                            meta['imdb_info'] = await prep.get_imdb_info(meta['imdb_id'], meta)
                        if meta['upload']:
                            ptpUrl, ptpData = await ptp.fill_upload_form(groupID, meta)
                            await ptp.upload(meta, ptpUrl, ptpData)
                            await asyncio.sleep(5)
                            await client.add_to_client(meta, "PTP")
                            successful_uploads += 1
                    except:
                        console.print(traceback.print_exc())

            if tracker == "TL":
                tracker_class = tracker_class_map[tracker](config=config)
                if meta['unattended']:
                    upload_to_tracker = True
                else:
                    upload_to_tracker = Confirm.ask(f"Upload to {tracker_class.tracker}? {debug}")
                if upload_to_tracker:
                    console.print(f"Uploading to {tracker_class.tracker}")
                    if check_banned_group(tracker_class.tracker, tracker_class.banned_groups, meta, skipped_details, path):
                        skipped_files += 1
                        skipped_details.append((path, f"Banned group on {tracker_class.tracker}"))  
                        continue
                    await tracker_class.upload(meta)
                    await client.add_to_client(meta, tracker_class.tracker)
                    successful_uploads += 1 
          















    ### FEEDBACK ###

    def format_path_with_files(path, files):
        formatted_text = Text()
        formatted_text.append("Path: ")
        formatted_text.append(f"{path}", style="bold")  # Removed the newline here
        for i, file in enumerate(files):
            file_name = os.path.basename(file)
            # Add a newline before each file, but not before the first one
            #if i != 0:
            formatted_text.append("\n")
            formatted_text.append(f"• {file_name}") 
        return formatted_text

    if total_files > 0:
        console.print()
        console.print(Panel(
            f"Processed [bold bright_magenta]{total_files}[/bold bright_magenta] Unique Uploads\n"
            f"Successful Uploads: [bold green]{successful_uploads}[/bold green]\n"
            f"Failed Uploads: [bold red]{skipped_files}[/bold red]",
            title="Upload Summary",
            border_style="bold cyan"
        ))

    # Handle skipped files
    if skipped_files > 0:
        tracker_skip_map = {}
        for detail in skipped_details:
            if len(detail) == 2:
                file, reason = detail
                tracker = "Unknown Tracker"
            else:
                file, reason, tracker = detail
            if reason not in tracker_skip_map:
                tracker_skip_map[reason] = []
            tracker_skip_map[reason].append((file, tracker))

        for reason, files in tracker_skip_map.items():
            reason_text = f"{reason}"
            reason_style = "bold red" if "banned" in reason.lower() or "rejected" in reason.lower() else "bold yellow"
            
            path_file_map = {}
            for file, _ in files:
                path = os.path.dirname(file) + os.sep  
                if path not in path_file_map:
                    path_file_map[path] = []
                path_file_map[path].append(file)

            combined_renderable = []
            for i, (path, files) in enumerate(path_file_map.items()):
                if i != 0:
                    combined_renderable.append(Text())
                formatted_text = format_path_with_files(path, files)
                combined_renderable.append(formatted_text)


            if 'duplicate' in reason.lower():
                combined_renderable.append(Text("\nTip: If 100% sure not a dupe pass with --skip-dupe-check", style="dim"))

            reason_panel = Panel(
                renderable=Group(*combined_renderable),
                title=reason_text,
                border_style=reason_style
            )

            console.print(reason_panel)

    # Handle skipped TMDB files
    if skipped_tmdb_files:
        path_file_map = {}
        for file in skipped_tmdb_files:
            path = os.path.dirname(file) + os.sep
            if path not in path_file_map:
                path_file_map[path] = []
            path_file_map[path].append(file)
        
        combined_renderable = []
        for i, (path, files) in enumerate(path_file_map.items()):
            if i != 0:
                combined_renderable.append(Text())
            formatted_text = format_path_with_files(path, files)
            combined_renderable.append(formatted_text)

        combined_renderable.append(Text("\nTip: Pass individually with --tmdb #####", style="dim"))

        reason_panel = Panel(
            renderable=Group(*combined_renderable),
            title="TMDb ID not found",
            border_style="bold red"
        )

        console.print(reason_panel)
        
def get_confirmation(meta):
    if meta['debug']:
        console.print("[bold red]DEBUG: True")
    console.print(f"Prep material saved to {meta['base_dir']}/tmp/{meta['uuid']}")
    console.print()

    db_info = [
        f"[bold]Title[/bold]: {meta['title']} ({meta['year']})\n",
        f"[bold]Overview[/bold]: {meta['overview']}\n",
        f"[bold]Category[/bold]: {meta['category']}\n",
    ]

    if int(meta.get('tmdb', 0)) != 0:
        db_info.append(f"TMDB: https://www.themoviedb.org/{meta['category'].lower()}/{meta['tmdb']}")
    if int(meta.get('imdb_id', '0')) != 0:
        db_info.append(f"IMDB: https://www.imdb.com/title/tt{meta['imdb_id']}")
    if int(meta.get('tvdb_id', '0')) != 0:
        db_info.append(f"TVDB: https://www.thetvdb.com/?id={meta['tvdb_id']}&tab=series")
    if int(meta.get('mal_id', 0)) != 0:
        db_info.append(f"MAL : https://myanimelist.net/anime/{meta['mal_id']}")

    console.print(Panel("\n".join(db_info), title="Database Info", border_style="bold yellow"))
    console.print()
    if int(meta.get('freeleech', '0')) != 0:
        console.print(f"[bold]Freeleech[/bold]: {meta['freeleech']}")
    if meta['tag'] == "":
            tag = ""
    else:
        tag = f" / {meta['tag'][1:]}"
    if meta['is_disc'] == "DVD":
        res = meta['source']
    else:
        res = meta['resolution']

    console.print(Text(f" {res} / {meta['type']}{tag}", style="bold"))
    if meta.get('personalrelease', False):
        console.print("[bright_magenta]Personal Release!")
    console.print()
    if not meta.get('unattended', False):
        get_missing(meta)
        ring_the_bell = "\a" if config['DEFAULT'].get("sfx_on_prompt", True) is True else "" # \a rings the bell
        console.print(f"[bold yellow]Is this correct?{ring_the_bell}") 
        console.print(f"[bold]Name[/bold]: {meta['name']}")
        confirm = Confirm.ask(" Correct?")
    else:
        console.print(f"[bold]Name[/bold]: {meta['name']}")
        confirm = True
    return confirm

def dupe_check(dupes, meta, config, skipped_details, path):
    if not dupes:
        console.print("[green]No dupes found")
        meta['upload'] = True   
        return meta, False  # False indicates not skipped

    table = Table(
        title="Are these dupes?",
        title_justify="center",
        show_header=True,
        header_style="bold underline",
        expand=True,
        show_lines=False,
        box=None
    )

    table.add_column("Name")
    table.add_column("Size", justify="center")

    for name, size in dupes.items():
        try:
            if "GB" in str(size).upper():
                size_gb = str(size).upper()
            else:
                size = int(size)
                if size > 0:
                    size_gb = str(round(size / (1024 ** 3), 2)) + " GB"  # Convert size to GB
                else:
                    size_gb = "N/A"
        except ValueError:
            size_gb = "N/A"
        table.add_row(name, f"[magenta]{size_gb}[/magenta]")

    console.print()
    console.print(table)
    console.print()

    def preprocess_string(text):
        text = re.sub(r'\[[a-z]{3}\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[^\w\s]', '', text)
        text = text.lower()
        return text

    def handle_similarity(similarity, meta):
        if similarity == 1.0:
            console.print(f"[red]Found exact match dupe.[dim](byte-for-byte)[/dim] Aborting..")
            meta['upload'] = False
            return meta, True  # True indicates skipped
        elif meta['unattended']:
            console.print(f"[red]Found potential dupe with {similarity * 100:.2f}% similarity. Aborting.")
            meta['upload'] = False
            return meta, True  # True indicates skipped
        else:
            upload = Confirm.ask(" Upload Anyways?")
            if not upload:
                meta['upload'] = False
                return meta, True  # True indicates skipped
        return meta, False  # False indicates not skipped

    similarity_threshold = max(config['AUTO'].get('dupe_similarity', 90.00) / 100, 0.70)
    size_tolerance = max(min(config['AUTO'].get('size_tolerance', 1 if meta['unattended'] else 30), 100), 1) / 100

    cleaned_meta_name = preprocess_string(meta['clean_name'])

    for name, dupe_size in dupes.items():
        if isinstance(dupe_size, str) and "GB" in dupe_size:
            dupe_size = float(dupe_size.replace(" GB", "")) * (1024 ** 3)  # Convert GB to bytes
        elif isinstance(dupe_size, (int, float)) and dupe_size != 0:
            meta_size = meta.get('content_size')
            if meta_size is None:
                meta_size = extract_size_from_torrent(meta['base_dir'], meta['uuid'])
            dupe_size = int(dupe_size)   
            if abs(meta_size - size) <= size_tolerance * meta_size:
                cleaned_dupe_name = preprocess_string(name)
                similarity = SequenceMatcher(None, cleaned_meta_name, cleaned_dupe_name).ratio()
                if similarity >= similarity_threshold:
                    meta, skipped = handle_similarity(similarity, meta)
                    if skipped:
                        return meta, True  # True indicates skipped
        else:
            cleaned_dupe_name = preprocess_string(name)
            similarity = SequenceMatcher(None, cleaned_meta_name, cleaned_dupe_name).ratio()
            if similarity >= similarity_threshold:
                meta, skipped = handle_similarity(similarity, meta)
                if skipped:
                    return meta, True  # True indicates skipped

    console.print("[yellow]No dupes found above the similarity threshold. Uploading anyways.")
    meta['upload'] = True
    return meta, False  # False indicates not skipped

def extract_size_from_torrent(base_dir, uuid):
    torrent_path = f"{base_dir}/tmp/{uuid}/BASE.torrent"
    with open(torrent_path, 'rb') as f:
        torrent_data = bencode.decode(f.read())
    
    info = torrent_data[b'info']
    if b'files' in info:
        # Multi-file torrent
        return sum(file[b'length'] for file in info[b'files'])
    else:
        # Single-file torrent
        return info[b'length']


# Return True if banned group
def check_banned_group(tracker, banned_group_list, meta, skipped_details, path):
    if meta['tag'] == "":
        return False
    else:
        q = False
        for tag in banned_group_list:
            if isinstance(tag, list):
                if meta['tag'][1:].lower() == tag[0].lower():
                    console.print(f"[bold yellow]{meta['tag'][1:]}[/bold yellow][bold red] was found on [bold yellow]{tracker}'s[/bold yellow] list of banned groups.")
                    console.print(f"[bold red]NOTE: [bold yellow]{tag[1]}")
                    q = True
            else:
                if meta['tag'][1:].lower() == tag.lower():
                    console.print(f"[bold yellow]{meta['tag'][1:]}[/bold yellow][bold red] was found on [bold yellow]{tracker}'s[/bold yellow] list of banned groups.")
                    q = True
        if q:
            if meta.get('unattended', False) or not Confirm.ask("[bold red] Upload Anyways?"):
                return True
    return False

def get_missing(meta):
    info_notes = {
        'edition' : 'Special Edition/Release',
        'description' : "Please include Remux/Encode Notes if possible (either here or edit your upload)",
        'service' : "WEB Service e.g.(AMZN, NF)",
        'region' : "Disc Region",
        'imdb' : 'IMDb ID (tt1234567)',
        'distributor' : "Disc Distributor e.g.(BFI, Criterion, etc)"
    }
    missing = []
    if meta.get('imdb_id', '0') == '0':
        meta['imdb_id'] = '0'
        meta['potential_missing'].append('imdb_id')
    if len(meta['potential_missing']) > 0:
        for each in meta['potential_missing']:
            if str(meta.get(each, '')).replace(' ', '') in ["", "None", "0"]:
                if each == "imdb_id":
                    each = 'imdb' 
                missing.append(f"--{each} | {info_notes.get(each)}")
    if missing != []:
        console.print(Rule("Potentially missing information", style="bold yellow"))
        for each in missing:
            if each.split('|')[0].replace('--', '').strip() in ["imdb"]:
                console.print(Text(each, style="bold red"))
            else:
                console.print(each)

    console.print()
    return

def print_banner():
    ascii_art = r"""
    
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::    _   _ ____  _     ___    _    ____       _   _ _____ _     ____  _____ ____     ::
::   | | | |  _ \| |   / _ \  / \  |  _ \     | | | | ____| |   |  _ \| ____|  _ \    ::
::   | | | | |_) | |  | | | |/ _ \ | | | |    | |_| |  _| | |   | |_) |  _| | |_) |   ::
::   | |_| |  __/| |__| |_| / ___ \| |_| |    |  _  | |___| |___|  __/| |___|  _ <    ::
::    \___/|_|   |_____\___/_/   \_\____/     |_| |_|_____|_____|_|   |_____|_| \_\   ::
::                                                                                    ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::     
                                                    
    """
    console.print(Align.center(Text(f"\n\n{ascii_art}\n", style='bold')))

def list_directory(directory):
    items = []
    for file in os.listdir(directory):
        if not file.startswith('.'):
            items.append(os.path.abspath(os.path.join(directory, file)))
    return items


if __name__ == '__main__':
    pyver = platform.python_version_tuple()
    if int(pyver[0]) != 3:
        console.print("[bold red]Python2 Detected, please use python3")
        exit()
    else:
        if int(pyver[1]) <= 6:
            console.print("[bold red]Python <= 3.6 Detected, please use Python >=3.7")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(do_the_thing(base_dir))
        else:
            asyncio.run(do_the_thing(base_dir))
        
