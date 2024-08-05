import argparse
import urllib.parse
import os
import datetime
import traceback
from src.console import console


class Args():
    """
    A class to handle and parse command-line arguments for the script.
    """
    def __init__(self, config):
        """
        Initialize Args with configuration settings.

        :param config: Dictionary containing configuration settings.
        """
        self.config = config

    def parse(self, args, meta):
        """
        Parse command-line arguments using argparse.

        :param args: List of command-line arguments.
        :param meta: Metadata dictionary to store argument values.
        :return: Parsed arguments as a dictionary.
        """
        input = args
        parser = argparse.ArgumentParser()

        # Define arguments for the parser
        parser.add_argument('path', nargs='*', help="Path to file/directory")
        parser.add_argument('-fd', '--full-directory', dest='full_dir', action='store_true', help="Uploads Folder + ALL Content Within")
        parser.add_argument('-s', '--screens', type=int, default=int(self.config['DEFAULT']['screens']), help="Number of screenshots")
        parser.add_argument('-c', '--category', nargs='*', help="Category [MOVIE, TV, FANRES]", choices=['movie', 'tv', 'fanres'])
        parser.add_argument('-t', '--type', nargs='*', help="Type [DISC, REMUX, ENCODE, WEBDL, WEBRIP, HDTV]", choices=['disc', 'remux', 'encode', 'webdl', 'web-dl', 'webrip', 'hdtv'])
        parser.add_argument('--source', nargs='*', help="Source [Blu-ray, BluRay, DVD, HDDVD, WEB, HDTV, UHDTV]", choices=['Blu-ray', 'BluRay', 'DVD', 'HDDVD', 'WEB', 'HDTV', 'UHDTV'], dest="manual_source")
        parser.add_argument('-res', '--resolution', nargs='*', help="Resolution [2160p, 1080p, 1080i, 720p, 576p, 576i, 480p, 480i, 8640p, 4320p, OTHER]", choices=['2160p', '1080p', '1080i', '720p', '576p', '576i', '480p', '480i', '8640p', '4320p', 'other'])
        parser.add_argument('-tmdb', '--tmdb', nargs='*', help="TMDb ID", type=str, dest='tmdb_manual')
        parser.add_argument('-imdb', '--imdb', nargs='*', help="IMDb ID", type=str)
        parser.add_argument('-mal', '--mal', nargs='*', help="MAL ID", type=str)
        parser.add_argument('-g', '--tag', nargs='*', help="Release Group Tag", type=str)
        parser.add_argument('-serv', '--service', nargs='*', help="Streaming Service", type=str)
        parser.add_argument('-dist', '--distributor', nargs='*', help="Disc Distributor e.g.(Criterion, BFI, etc.)", type=str)
        parser.add_argument('-edition', '--edition', '--repack', nargs='*', help="Edition/Repack String e.g.(Director's Cut, Uncut, Hybrid, REPACK, REPACK3)", type=str, dest='manual_edition', default="")
        parser.add_argument('-season', '--season', nargs='*', help="Season (number)", type=str)
        parser.add_argument('-episode', '--episode', nargs='*', help="Episode (number)", type=str)
        parser.add_argument('-daily', '--daily', nargs=1, help="Air date of this episode (YYYY-MM-DD)", type=datetime.date.fromisoformat, dest="manual_date")
        parser.add_argument('--no-season', dest='no_season', action='store_true', help="Remove Season from title")
        parser.add_argument('--no-year', dest='no_year', action='store_true', help="Remove Year from title")
        parser.add_argument('--no-aka', dest='no_aka', action='store_true', help="Remove AKA from title")
        parser.add_argument('--no-dub', dest='no_dub', action='store_true', help="Remove Dubbed from title")
        parser.add_argument('--no-tag', dest='no_tag', action='store_true', help="Remove Group Tag from title")
        parser.add_argument('-ns', '--no-seed', action='store_true', help="Do not add torrent to the client")
        parser.add_argument('-year', '--year', dest='manual_year', nargs='?', type=int, default=0, help="Year")
        parser.add_argument('-ptp', '--ptp', nargs='*', help="PTP torrent id/permalink", type=str)
        parser.add_argument('-blu', '--blu', nargs='*', help="BLU torrent id/link", type=str)
        parser.add_argument('-hdb', '--hdb', nargs='*', help="HDB torrent id/link", type=str)
        parser.add_argument('-d', '--desc', nargs='*', help=r'\"[b]Custom Description[/b]\"')
        parser.add_argument('-pb', '--desclink', nargs='*', help=r'\"https://pastebin.com/URL\"')
        parser.add_argument('-df', '--descfile', nargs='*', help=r'\"\path\to\description.txt\"')
        parser.add_argument('-aid', '--auto-insert-desc', dest='auto_desc', action='store_true', help='Uses (file or season folder).txt or description.txt existing in upload path')
        parser.add_argument('-ih', '--imghost', nargs='*', help="Image Host", choices=['imgbb', 'ptpimg', 'imgbox', 'pixhost', 'lensdump'])
        parser.add_argument('-siu', '--skip-imagehost-upload', dest='skip_imghost_upload', action='store_true', help="Skip Uploading to an image host")
        parser.add_argument('-th', '--torrenthash', nargs='*', help="Torrent Hash to re-use from your client's session directory")
        parser.add_argument('-nfo', '--nfo', action='store_true', help="Use .nfo in directory for description")
        parser.add_argument('-k', '--keywords', nargs='*', help="Add comma separated keywords e.g. 'keyword, keyword2, etc'")
        parser.add_argument('-reg', '--region', nargs='*', help="Region for discs")
        parser.add_argument('-a', '--anon', action='store_true', help="Upload anonymously")
        parser.add_argument('-st', '--stream', action='store_true', help="Stream Optimized Upload")
        parser.add_argument('-webdv', '--webdv', action='store_true', help="Contains a Dolby Vision layer converted using dovi_tool")
        parser.add_argument('-hc', '--hardcoded-subs', action='store_true', help="Contains hardcoded subs", dest="hardcoded-subs")
        parser.add_argument('-pr', '--personalrelease', action='store_true', help="Personal Release")
        parser.add_argument('-sdc','--skip-dupe-check', action='store_true', help="Pass if you know this is a dupe (Skips dupe check)", dest="dupe")
        parser.add_argument('-debug', '--debug', action='store_true', help="Debug Mode, will run through all the motions providing extra info, but will not upload to trackers.")
        parser.add_argument('-ffdebug', '--ffdebug', action='store_true', help="Will show info from ffmpeg while taking screenshots.")
        parser.add_argument('-m', '--manual', action='store_true', help="Manual Mode. Returns link to ddl screens/base.torrent")
        parser.add_argument('-nh', '--nohash', action='store_true', help="Don't hash .torrent")
        parser.add_argument('-rh', '--rehash', action='store_true', help="DO hash .torrent")
        parser.add_argument('-ps', '--piece-size-max', dest='piece_size_max', nargs='*', help="Maximum piece size in MiB", choices=[1, 2, 4, 8, 16], type=int)
        parser.add_argument('-dr', '--draft', action='store_true', help="Send to drafts (BHD)")
        parser.add_argument('-tc', '--torrent-creation', dest='torrent_creation', nargs='*', help="What tool should be used to create the base .torrent", choices=['torf', 'torrenttools', 'mktorrent'])
        parser.add_argument('-client', '--client', nargs='*', help="Use this torrent client instead of default")
        parser.add_argument('-qbt', '--qbit-tag', dest='qbit_tag', nargs='*', help="Add to qbit with this tag")
        parser.add_argument('-qbc', '--qbit-cat', dest='qbit_cat', nargs='*', help="Add to qbit with this category")
        parser.add_argument('-rtl', '--rtorrent-label', dest='rtorrent_label', nargs='*', help="Add to rtorrent with this label")
        parser.add_argument('-tk', '--trackers', nargs='*', help="Upload to these trackers, space separated (--trackers blu bhd)")
        parser.add_argument('-rt', '--randomized', nargs='*', help="Number of extra torrents with random infohash", default=0)
        parser.add_argument('-aq', '--auto-queue', dest='auto_queue', help="Automatically queue files in a directory")
        parser.add_argument('-sq', '--show-queue', dest='show_queue', action='store_true', help="Show the list of queued files")
        parser.add_argument('-delay', '--delay', dest='delay', type=int, help='Delay between queued torrents in seconds')
        parser.add_argument('-random', '--random', action='store_true', help="Randomize queue order")
        parser.add_argument('-fa', '--full-auto', dest='full_auto', nargs='?', const=True, default=False, type=str, help=argparse.SUPPRESS)
        parser.add_argument('-ua', '--unattended', action='store_true', help=argparse.SUPPRESS)
        parser.add_argument('-vs', '--vapoursynth', action='store_true', help="Use vapoursynth for screens (requires vs install)")
        parser.add_argument('-cleanup', '--cleanup', action='store_true', help="Clean up tmp directory")
        parser.add_argument('-reconfig', '--reconfig', action='store_true', help="Auto Update Config")
        parser.add_argument('-fl', '--freeleech', nargs='*', default=0, dest="freeleech", help="Freeleech Percentage")
        
        # Parse arguments and handle unknown arguments
        args, before_args = parser.parse_known_args(input)
        args = vars(args)

        # Check if 'full_auto' argument is set
        if args.get('full_auto', False):
            # Set 'unattended' and 'auto_desc' to True
            # Assign 'full_auto' value to 'auto_queue'
            args['unattended'] = args['auto_desc'] = True 
            args['auto_queue'] = args['full_auto']

        # Check if there are unknown arguments and the specified path does not exist
        if len(before_args) >= 1 and not os.path.exists(' '.join(args['path'])):
            for each in before_args:
                # Add unknown arguments to 'path'
                args['path'].append(each)
                # Check if the updated 'path' exists
                if os.path.exists(' '.join(args['path'])):
                    # If any ".mkv" file is in 'before_args'
                    if any(".mkv" in x for x in before_args):
                        # If the updated 'path' contains ".mkv", exit loop
                        if ".mkv" in ' '.join(args['path']):
                            break
                    else:
                        # Exit loop if '.mkv' is not found
                        break

        # Check if either 'tmdb_manual' or 'imdb' is present in the meta dictionary
        if meta.get('tmdb_manual') is not None or meta.get('imdb') is not None:
            # Set both 'tmdb_manual' and 'imdb' to None if either is present
            meta['tmdb_manual'] = meta['imdb'] = None



        # Iterate over each key in the 'args' dictionary
        for key in args:
            value = args.get(key)
            # Proceed only if the value is not None or an empty list
            if value not in (None, []):
                # Check if the value is a list
                if isinstance(value, list):
                    # Convert the list to a string representation
                    value2 = self.list_to_string(value)
                    
                    # Handle specific keys with custom processing
                    if key == 'type':
                        # Convert 'type' value to uppercase and remove hyphens
                        meta[key] = value2.upper().replace('-', '')
                    elif key == 'tag':
                        # Prefix 'tag' value with a hyphen
                        meta[key] = f"-{value2}"
                    elif key == 'screens':
                        # Convert 'screens' value to integer
                        meta[key] = int(value2)
                    elif key == 'season':
                        # Assign 'season' value to 'manual_season'
                        meta['manual_season'] = value2
                    elif key == 'episode':
                        # Assign 'episode' value to 'manual_episode'
                        meta['manual_episode'] = value2
                    elif key == 'manual_date':
                        # Assign 'manual_date' value to itself
                        meta['manual_date'] = value2
                    elif key == 'tmdb_manual':
                        # Parse 'tmdb_manual' ID and update 'category' and 'tmdb_manual'
                        meta['category'], meta['tmdb_manual'] = self.parse_tmdb_id(value2, meta.get('category'))
                    elif key == 'ptp':
                        # Process 'ptp' value, extract torrent ID if URL or use it directly
                        if value2.startswith('http'):
                            parsed = urllib.parse.urlparse(value2)
                            try:
                                meta['ptp'] = urllib.parse.parse_qs(parsed.query)['torrentid'][0]
                            except:
                                console.print('[red]Your terminal ate part of the url, please surround in quotes next time, or pass only the torrent ID.')
                                console.print('[red]Continuing without -ptp')
                        else:
                            meta['ptp'] = value2
                    elif key == 'blu':
                        # Process 'blu' value, extract ID from URL if necessary
                        if value2.startswith('http'):
                            parsed = urllib.parse.urlparse(value2)
                            try:
                                blupath = parsed.path
                                if blupath.endswith('/'):
                                    blupath = blupath[:-1]
                                meta['blu'] = blupath.split('/')[-1]
                            except:
                                console.print('[red]Unable to parse id from url')
                                console.print('[red]Continuing without --blu')
                        else:
                            meta['blu'] = value2
                    elif key == 'hdb':
                        # Process 'hdb' value, extract ID from URL if necessary
                        if value2.startswith('http'):
                            parsed = urllib.parse.urlparse(value2)
                            try:
                                meta['hdb'] = urllib.parse.parse_qs(parsed.query)['id'][0]
                            except:
                                console.print('[red]Your terminal ate part of the url, please surround in quotes next time, or pass only the torrent ID.')
                                console.print('[red]Continuing without -hdb')
                        else:
                            meta['hdb'] = value2
                    else:
                        # Default case for other list values
                        meta[key] = value2
                else:
                    # Handle non-list values
                    meta[key] = value
            elif key in ("manual_edition"):
                # Assign value directly to 'manual_edition' if present
                meta[key] = value
            elif key in ("freeleech"):
                # Set 'freeleech' to 100 if present
                meta[key] = 100
            elif key in ("tag") and value == []:
                # Set 'tag' to an empty string if the value is an empty list
                meta[key] = ""
            else:
                # Use the existing value from 'meta' or set it to None
                meta[key] = meta.get(key, None)
            
            # Handle specific key 'trackers' without additional processing
            if key in ('trackers'):
                meta[key] = value

        return meta, parser, before_args

    def list_to_string(self, list):
        """
        Convert a list of strings into a single space-separated string.

        Args:
            list (list): List of strings to be converted.

        Returns:
            str: A space-separated string of list elements or "None" if conversion fails.
        """
        # Check if the list has exactly one element
        if len(list) == 1:
            return str(list[0])
        try:
            # Join list elements into a single string separated by spaces
            result = " ".join(list)
        except:
            # Return "None" if joining fails
            result = "None"
        return result

    def parse_tmdb_id(self, id, category):
        """
        Parse a TMDb ID to extract the numeric ID and update the category.

        Args:
            id (str): The TMDb ID string to be parsed.
            category (str): The initial category to be updated based on the ID.

        Returns:
            tuple: A tuple containing the updated category and the parsed ID.
        """
        # Convert ID to lowercase and strip leading whitespace
        id = id.lower().lstrip()
        
        # Determine category and extract numeric ID based on the prefix
        if id.startswith('tv'):
            id = id.split('/')[1]
            category = 'TV'
        elif id.startswith('movie'):
            id = id.split('/')[1]
            category = 'MOVIE'
        else:
            id = id
        
        return category, id