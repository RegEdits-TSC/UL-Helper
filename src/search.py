import platform
import asyncio
import os
from src.console import console

class Search():
    """
    Logic for searching files and folders.
    """
    def __init__(self, config):
        self.config = config
        pass

    async def searchFile(self, filename):
        """
        Search for files with names matching the given filename.
        """
        os_info = platform.platform()
        filename = filename.lower()
        files_total = []
        if filename == "":
            console.print("nothing entered")
            return
        file_found = False
        words = filename.split()

        async def search_file(search_dir):
            """
            Helper function to search for files within a directory.
            """
            files_total_search = []
            console.print(f"Searching {search_dir}")
            for root, dirs, files in os.walk(search_dir, topdown=False):
                for name in files:
                    if not name.endswith('.nfo'):
                        l_name = name.lower()
                        os_info = platform.platform()
                        if await self.file_search(l_name, words):
                            file_found = True
                            if 'Windows' in os_info:
                                files_total_search.append(root + '\\' + name)
                            else:
                                files_total_search.append(root + '/' + name)
            return files_total_search

        config_dir = self.config['DISCORD']['search_dir']
        if isinstance(config_dir, list):
            for each in config_dir:
                files = await search_file(each)
                files_total = files_total + files
        else:
            files_total = await search_file(config_dir)
        return files_total

    async def searchFolder(self, foldername):
        """
        Search for folders with names matching the given foldername.
        """
        os_info = platform.platform()
        foldername = foldername.lower()
        folders_total = []
        if foldername == "":
            console.print("nothing entered")
            return
        folders_found = False
        words = foldername.split()

        async def search_dir(search_dir):
            """
            Helper function to search for folders within a directory.
            """
            console.print(f"Searching {search_dir}")
            folders_total_search = []
            for root, dirs, files in os.walk(search_dir, topdown=False):
                for name in dirs:
                    l_name = name.lower()
                    os_info = platform.platform()
                    if await self.file_search(l_name, words):
                        folders_found = True
                        if 'Windows' in os_info:
                            folders_total_search.append(root + '\\' + name)
                        else:
                            folders_total_search.append(root + '/' + name)
            return folders_total_search

        config_dir = self.config['DISCORD']['search_dir']
        if isinstance(config_dir, list):
            for each in config_dir:
                folders = await search_dir(each)
                folders_total = folders_total + folders
        else:
            folders_total = await search_dir(config_dir)
        return folders_total

    async def file_search(self, name, name_words):
        """
        Check if all words in name_words are present in the name.
        """
        check = True
        for word in name_words:
            if word not in name:
                check = False
                break
        return check