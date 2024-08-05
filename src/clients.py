from torf import Torrent
import xmlrpc.client
import bencode
import os
import qbittorrentapi
from deluge_client import DelugeRPCClient, LocalDelugeRPCClient
import base64
from pyrobase.parts import Bunch
import errno
import asyncio
import ssl
import shutil
import time
from src.console import console

class Clients:
    """
    Handles adding torrents to the client.
    """
    def __init__(self, config):
        self.config = config

    async def add_to_client(self, meta, tracker):
        """
        Adds a torrent to the specified torrent client.

        Args:
            meta (dict): Metadata for the torrent.
            tracker (str): Tracker name.
        """
        # Construct the torrent file path
        torrent_path = f"{meta['base_dir']}/tmp/{meta['uuid']}/[{tracker}]{meta['clean_name']}.torrent"

        # Check if seeding is disabled
        if meta.get('no_seed', False):
            console.print("[bold red]--no-seed was passed, so the torrent will not be added to the client")
            console.print("[bold yellow]Add torrent manually to the client")
            return

        # Check if the torrent file exists
        if os.path.exists(torrent_path):
            torrent = Torrent.read(torrent_path)
        else:
            return

        # Determine the default torrent client
        default_torrent_client = meta.get('client', self.config['DEFAULT'].get('default_torrent_client', 'none'))
        
        # Skip if no client is specified
        if default_torrent_client == 'none':
            return 

        client = self.config['TORRENT_CLIENTS'].get(default_torrent_client)
        torrent_client = client['torrent_client']

        # Map local and remote paths
        local_path, remote_path = await self.remote_path_map(meta)

        console.print(f"[bold green]Adding to {torrent_client}")

        # Add the torrent to the appropriate client
        if torrent_client.lower() == "rtorrent":
            path = os.path.dirname(meta['path']) if meta['full_dir'] else meta['path']
            self.rtorrent(path, torrent_path, torrent, meta, local_path, remote_path, client)
        elif torrent_client.lower() == "qbit":
            path = os.path.dirname(meta['path']) if meta['full_dir'] else meta['path']
            await self.qbittorrent(path, torrent, local_path, remote_path, client, meta['is_disc'], meta['filelist'], meta)
        elif torrent_client.lower() == "deluge":
            path = os.path.dirname(meta['path']) if meta['full_dir'] or meta['type'] == "DISC" else meta['path']
            self.deluge(path, torrent_path, torrent, local_path, remote_path, client, meta)
        elif torrent_client.lower() == "watch":
            shutil.copy(torrent_path, client['watch_folder'])

        return

    async def remote_path_map(self, meta):
        # Placeholder method for remote path mapping
        return meta['local_path'], meta['remote_path']

    def rtorrent(self, path, torrent_path, torrent, meta, local_path, remote_path, client):
        # Placeholder method for rTorrent integration
        pass

    async def qbittorrent(self, path, torrent, local_path, remote_path, client, is_disc, filelist, meta):
        # Placeholder method for qBittorrent integration
        pass

    def deluge(self, path, torrent_path, torrent, local_path, remote_path, client, meta):
        # Placeholder method for Deluge integration
        pass

    async def find_existing_torrent(self, meta):
        """
        Finds an existing torrent based on metadata and client configuration.

        Args:
            meta (dict): Metadata for the torrent.

        Returns:
            str or None: The path to the existing torrent if found, otherwise None.
        """
        # Determine the default torrent client
        default_torrent_client = meta.get('client') or self.config['DEFAULT'].get('default_torrent_client', 'none')

        # Return None if no client is specified
        if default_torrent_client == 'none':
            return None

        client = self.config['TORRENT_CLIENTS'].get(default_torrent_client)
        torrent_client = client.get('torrent_client', 'none').lower()
        torrent_storage_dir = client.get('torrent_storage_dir')

        # Check if torrent storage directory is properly configured
        if torrent_storage_dir is None and torrent_client != "watch":
            console.print(f'[bold red]Missing torrent_storage_dir for {default_torrent_client}')
            return None
        elif not os.path.exists(str(torrent_storage_dir)) and torrent_client != "watch":
            console.print(f"[bold red]Invalid torrent_storage_dir path: [bold yellow]{torrent_storage_dir}")
            return None

        torrenthash = None

        # Validate and check for existing torrent files
        if torrent_storage_dir and os.path.exists(torrent_storage_dir):
            if meta.get('torrenthash'):
                valid, torrent_path = await self.is_valid_torrent(meta, f"{torrent_storage_dir}/{meta['torrenthash']}.torrent", meta['torrenthash'], torrent_client, print_err=True)
                if valid:
                    torrenthash = meta['torrenthash']
            elif meta.get('ext_torrenthash'):
                valid, torrent_path = await self.is_valid_torrent(meta, f"{torrent_storage_dir}/{meta['ext_torrenthash']}.torrent", meta['ext_torrenthash'], torrent_client, print_err=True)
                if valid:
                    torrenthash = meta['ext_torrenthash']

            # Special handling for qBittorrent if enabled
            if torrent_client == 'qbit' and not torrenthash and client.get('enable_search', False):
                torrenthash = await self.search_qbit_for_torrent(meta, client)
                if not torrenthash:
                    console.print("[bold yellow]No Valid .torrent found")

            if not torrenthash:
                return None

            # Validate the found torrent
            torrent_path = f"{torrent_storage_dir}/{torrenthash}.torrent"
            valid2, torrent_path = await self.is_valid_torrent(meta, torrent_path, torrenthash, torrent_client, print_err=False)
            if valid2:
                return torrent_path

        return None

    async def is_valid_torrent(self, meta, torrent_path, torrenthash, torrent_client, print_err=False):
        """
        Checks if the given torrent file is valid based on several criteria.

        Args:
            meta (dict): Metadata for the torrent.
            torrent_path (str): Path to the torrent file.
            torrenthash (str): Hash of the torrent.
            torrent_client (str): Name of the torrent client.
            print_err (bool): Whether to print error messages.

        Returns:
            tuple: A tuple containing a boolean indicating validity and the path to the torrent file.
        """
        valid = False
        wrong_file = False
        err_print = ""

        # Normalize torrent hash and path based on the torrent client
        if torrent_client in ('qbit', 'deluge'):
            torrenthash = torrenthash.lower().strip()
            torrent_path = torrent_path.replace(torrenthash.upper(), torrenthash)
        elif torrent_client == 'rtorrent':
            torrenthash = torrenthash.upper().strip()
            torrent_path = torrent_path.replace(torrenthash.upper(), torrenthash)

        # Log the path if debugging is enabled
        if meta.get('debug', False):
            console.log(torrent_path)

        # Check if the torrent file exists
        if os.path.exists(torrent_path):
            torrent = Torrent.read(torrent_path)
            # Check for disc and file basename match
            if meta.get('is_disc'):
                torrent_filepath = os.path.commonpath(torrent.files)
                if os.path.basename(meta['path']) in torrent_filepath:
                    valid = True
            # Validate single file scenario
            if len(torrent.files) == len(meta['filelist']) == 1:
                if os.path.basename(torrent.files[0]) == os.path.basename(meta['filelist'][0]):
                    if str(torrent.files[0]) == os.path.basename(torrent.files[0]):
                        valid = True
                else:
                    wrong_file = True
            # Validate multiple files scenario
            elif len(torrent.files) == len(meta['filelist']):
                torrent_filepath = os.path.commonpath(torrent.files)
                actual_filepath = os.path.commonpath(meta['filelist'])
                local_path, remote_path = await self.remote_path_map(meta)
                if local_path.lower() in meta['path'].lower() and local_path.lower() != remote_path.lower():
                    actual_filepath = torrent_path.replace(local_path, remote_path)
                    actual_filepath = torrent_path.replace(os.sep, '/')
                if meta.get('debug', False):
                    console.log(f"torrent_filepath: {torrent_filepath}")
                    console.log(f"actual_filepath: {actual_filepath}")
                if torrent_filepath in actual_filepath:
                    valid = True
        else:
            console.print(f'[bold yellow]{torrent_path} was not found')

        # Check the validity of the torrent based on piece size and number of pieces
        if valid:
            if os.path.exists(torrent_path):
                reuse_torrent = Torrent.read(torrent_path)
                if (reuse_torrent.pieces >= 7000 and reuse_torrent.piece_size < 8388608) or (reuse_torrent.pieces >= 4000 and reuse_torrent.piece_size < 4194304):
                    err_print = "[bold yellow]Too many pieces exist in current hash. REHASHING"
                    valid = False
                elif reuse_torrent.piece_size < 32768:
                    err_print = "[bold yellow]Piece size too small to reuse"
                    valid = False
                elif wrong_file:
                    err_print = "[bold red] Provided .torrent has files that were not expected"
                    valid = False
                else:
                    err_print = f'[bold green]REUSING .torrent with infohash: [bold yellow]{torrenthash}'
        else:
            err_print = '[bold yellow]Unwanted Files/Folders Identified'

        if print_err:
            console.print(err_print)

        return valid, torrent_path

    def rtorrent(self, path, torrent_path, torrent, meta, local_path, remote_path, client):
        """
        Handles adding a torrent to rTorrent and setting up fast-resume data.

        Args:
            path (str): Path where the torrent should be added.
            torrent_path (str): Path to the torrent file.
            torrent (Torrent): Torrent object.
            meta (dict): Metadata related to the torrent.
            local_path (str): Local path for comparison.
            remote_path (str): Remote path to be used.
            client (dict): Client configuration including rTorrent URL.

        Raises:
            EnvironmentError: If there is an error creating fast-resume data.
        """
        # Connect to rTorrent
        rtorrent = xmlrpc.client.Server(client['rtorrent_url'], context=ssl._create_stdlib_context())
        
        # Read and prepare metainfo from the torrent file
        metainfo = bencode.bread(torrent_path)
        try:
            fast_resume = self.add_fast_resume(metainfo, path, torrent)
        except EnvironmentError as exc:
            console.print("[red]Error making fast-resume data (%s)" % (exc,))
            raise

        # Write the fast-resume data to a new file if different from original metainfo
        new_meta = bencode.bencode(fast_resume)
        if new_meta != metainfo:
            fr_file = torrent_path.replace('.torrent', '-resume.torrent')
            console.print("Creating fast resume")
            bencode.bwrite(fast_resume, fr_file)

        # Check if the path is a directory
        isdir = os.path.isdir(path)
        
        # Handle remote path mounting if necessary
        modified_fr = False
        if local_path.lower() in path.lower() and local_path.lower() != remote_path.lower():
            path_dir = os.path.dirname(path)
            path = path.replace(local_path, remote_path)
            path = path.replace(os.sep, '/')
            shutil.copy(fr_file, f"{path_dir}/fr.torrent")
            fr_file = f"{os.path.dirname(path)}/fr.torrent"
            modified_fr = True
        if not isdir:
            path = os.path.dirname(path)

        # Add and start the torrent in rTorrent
        console.print("[bold yellow]Adding and starting torrent")
        rtorrent.load.start_verbose('', fr_file, f"d.directory_base.set={path}")
        time.sleep(1)
        
        # Add labels to the torrent
        if client.get('rtorrent_label'):
            rtorrent.d.custom1.set(torrent.infohash, client['rtorrent_label'])
        if meta.get('rtorrent_label'):
            rtorrent.d.custom1.set(torrent.infohash, meta['rtorrent_label'])

        # Clean up modified fast-resume file location
        if modified_fr:
            os.remove(f"{path_dir}/fr.torrent")
        if meta.get('debug', False):
            console.print(f"[cyan]Path: {path}")

        return

    async def qbittorrent(self, path, torrent, local_path, remote_path, client, is_disc, filelist, meta):
        """
        Handles adding a torrent to qBittorrent and rechecking it.

        Args:
            path (str): Path where the torrent should be added.
            torrent (Torrent): Torrent object.
            local_path (str): Local path for comparison.
            remote_path (str): Remote path to be used.
            client (dict): Client configuration including qBittorrent details.
            is_disc (bool): Flag indicating if it's a disc type.
            filelist (list): List of files associated with the torrent.
            meta (dict): Metadata related to the torrent.
        """
        # Check if path is a directory
        isdir = os.path.isdir(path)
        if not isdir and len(filelist) == 1:
            path = os.path.dirname(path)
        if len(filelist) != 1:
            path = os.path.dirname(path)
        
        # Handle remote path mounting
        if local_path.lower() in path.lower() and local_path.lower() != remote_path.lower():
            path = path.replace(local_path, remote_path)
            path = path.replace(os.sep, '/')
        if not path.endswith(os.sep):
            path = f"{path}/"
        
        # Initialize qBittorrent client
        qbt_client = qbittorrentapi.Client(
            host=client['qbit_url'],
            port=client['qbit_port'],
            username=client['qbit_user'],
            password=client['qbit_pass'],
            VERIFY_WEBUI_CERTIFICATE=client.get('VERIFY_WEBUI_CERTIFICATE', True)
        )
        
        console.print("[bold yellow]Adding and rechecking torrent")
        try:
            qbt_client.auth_log_in()
        except qbittorrentapi.LoginFailed:
            console.print("[bold red]INCORRECT QBIT LOGIN CREDENTIALS")
            return
        
        # Determine automatic torrent management
        auto_management = False
        am_config = client.get('automatic_management_paths', '')
        if isinstance(am_config, list):
            for each in am_config:
                if os.path.normpath(each).lower() in os.path.normpath(path).lower():
                    auto_management = True
        else:
            if os.path.normpath(am_config).lower() in os.path.normpath(path).lower() and am_config.strip() != "":
                auto_management = True
        
        # Set qBittorrent category and content layout
        qbt_category = client.get("qbit_cat") if not meta.get("qbit_cat") else meta.get('qbit_cat')
        content_layout = client.get('content_layout', 'Original')
        
        # Add the torrent to qBittorrent
        qbt_client.torrents_add(
            torrent_files=torrent.dump(),
            save_path=path,
            use_auto_torrent_management=auto_management,
            is_skip_checking=True,
            content_layout=content_layout,
            category=qbt_category
        )
        
        # Wait for up to 30 seconds for qBittorrent to return the download
        for _ in range(30):
            if len(qbt_client.torrents_info(torrent_hashes=torrent.infohash)) > 0:
                break
            await asyncio.sleep(1)
        
        # Resume the torrent and add tags if available
        qbt_client.torrents_resume(torrent.infohash)
        if client.get('qbit_tag') is not None:
            qbt_client.torrents_add_tags(tags=client.get('qbit_tag'), torrent_hashes=torrent.infohash)
        if meta.get('qbit_tag') is not None:
            qbt_client.torrents_add_tags(tags=meta.get('qbit_tag'), torrent_hashes=torrent.infohash)
        
        console.print(f"Added to: {path}")

    def deluge(self, path, torrent_path, torrent, local_path, remote_path, client, meta):
        """
        Handles adding a torrent to Deluge.

        Args:
            path (str): Path where the torrent should be added.
            torrent_path (str): Path to the torrent file.
            torrent (Torrent): Torrent object.
            local_path (str): Local path for comparison.
            remote_path (str): Remote path to be used.
            client (dict): Client configuration including Deluge details.
            meta (dict): Metadata related to the torrent.
        """
        # Initialize Deluge client
        client = DelugeRPCClient(
            client['deluge_url'],
            int(client['deluge_port']),
            client['deluge_user'],
            client['deluge_pass']
        )
        
        # Connect to Deluge
        client.connect()
        if client.connected:
            console.print("Connected to Deluge")
            
            # Check if path is a directory
            isdir = os.path.isdir(path)
            
            # Handle remote path mounting
            if local_path.lower() in path.lower() and local_path.lower() != remote_path.lower():
                path = path.replace(local_path, remote_path)
                path = path.replace(os.sep, '/')
            
            # Set path to directory of the given path
            path = os.path.dirname(path)
            
            # Add torrent to Deluge
            client.call(
                'core.add_torrent_file',
                torrent_path,
                base64.b64encode(torrent.dump()),
                {'download_location': path, 'seed_mode': True}
            )
            if meta['debug']:
                console.print(f"[cyan]Path: {path}")
        else:
            console.print("[bold red]Unable to connect to Deluge")

    def add_fast_resume(self, metainfo, datapath, torrent):
        """
        Add fast resume data to a metafile dictionary.

        Args:
            metainfo (dict): The metafile dictionary to which resume data will be added.
            datapath (str): The base path where torrent data is located.
            torrent (Torrent): Torrent object containing torrent information.

        Returns:
            dict: Updated metafile dictionary with fast resume data.
        """
        # Get list of files from the metainfo
        files = metainfo["info"].get("files", None)
        single = files is None
        
        # Handle single file case
        if single:
            if os.path.isdir(datapath):
                datapath = os.path.join(datapath, metainfo["info"]["name"])
            files = [Bunch(
                path=[os.path.abspath(datapath)],
                length=metainfo["info"]["length"],
            )]

        # Prepare resume data
        resume = metainfo.setdefault("libtorrent_resume", {})
        resume["bitfield"] = len(metainfo["info"]["pieces"]) // 20
        resume["files"] = []
        piece_length = metainfo["info"]["piece length"]
        offset = 0

        for fileinfo in files:
            # Get the path into the filesystem
            filepath = os.sep.join(fileinfo["path"])
            if not single:
                filepath = os.path.join(datapath, filepath.strip(os.sep))

            # Check file size
            if os.path.getsize(filepath) != fileinfo["length"]:
                raise OSError(
                    errno.EINVAL,
                    "File size mismatch for %r [is %d, expected %d]" % (
                        filepath, os.path.getsize(filepath), fileinfo["length"],
                    )
                )

            # Add resume data for this file
            resume["files"].append(dict(
                priority=1,
                mtime=int(os.path.getmtime(filepath)),
                completed=(offset + fileinfo["length"] + piece_length - 1) // piece_length
                        - offset // piece_length,
            ))
            offset += fileinfo["length"]

        return metainfo

    async def remote_path_map(self, meta):
        """
        Map the local and remote paths based on the torrent client's configuration and meta information.

        Args:
            meta (dict): Metadata dictionary containing path information.

        Returns:
            tuple: Local path and remote path as strings.
        """
        # Determine the torrent client
        if meta.get('client', None) is None:
            torrent_client = self.config['DEFAULT']['default_torrent_client']
        else:
            torrent_client = meta['client']
        
        # Get local and remote paths from the configuration
        local_path = list_local_path = self.config['TORRENT_CLIENTS'][torrent_client].get('local_path', '/LocalPath')
        remote_path = list_remote_path = self.config['TORRENT_CLIENTS'][torrent_client].get('remote_path', '/RemotePath')
        
        # Handle case where local_path is a list
        if isinstance(local_path, list):
            for i in range(len(local_path)):
                if os.path.normpath(local_path[i]).lower() in meta['path'].lower():
                    list_local_path = local_path[i]
                    list_remote_path = remote_path[i]

        # Normalize paths
        local_path = os.path.normpath(list_local_path)
        remote_path = os.path.normpath(list_remote_path)
        
        # Ensure remote path ends with a separator
        if local_path.endswith(os.sep):
            remote_path = remote_path + os.sep

        return local_path, remote_path