import asyncio
import datetime
import json
import logging
import configparser
from pathlib import Path

import discord
from discord.ext import commands

def config_load():
    """
    Load the configuration settings for the bot.
    """
    from data.config import config
    return config

async def run():
    """
    Start the bot. Initialize any required sessions or connections here, 
    and pass them to the bot as keyword arguments if needed.
    """
    # Load configuration settings
    config = config_load()
    
    # Create an instance of the bot with the configuration settings
    bot = Bot(config=config, description=config['DISCORD']['discord_bot_description'])
    
    try:
        # Start the bot using the provided token
        await bot.start(config['DISCORD']['discord_bot_token'])
    except KeyboardInterrupt:
        # Handle graceful shutdown on keyboard interrupt
        await bot.logout()

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix_,
            description=kwargs.pop('description')
        )
        # Initialize bot attributes
        self.start_time = None
        self.app_info = None
        self.config = config_load()
        
        # Schedule tasks to run in the background
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        """
        Waits for the bot to connect to Discord and records the start time.
        Can be used to calculate uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def get_prefix_(self, bot, message):
        """
        A coroutine to get the command prefix. It allows for asynchronous operations
        such as fetching the prefix from a database. 
        """
        prefix = [self.config['DISCORD']['command_prefix']]
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def load_all_extensions(self):
        """
        Loads all .py files in the /cogs/ directory as cog extensions.
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)  # Ensure on_ready has completed
        
        # Load each cog extension
        cogs = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in cogs:
            try:
                self.load_extension(f'cogs.{extension}')
                print(f'Loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'Failed to load extension {error}')
            print('-' * 10)

    async def on_ready(self):
        """
        Called when the bot has connected or resumed connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Using discord.py version: {discord.__version__}\n'
              f'Owner: {self.app_info.owner}\n')
        print('-' * 10)
        
        # Send a message to a specified channel when the bot is online
        channel = self.get_channel(int(self.config['DISCORD']['discord_channel_id']))
        await channel.send(f'{self.user.name} is now online')

    async def on_message(self, message):
        """
        Triggered for every message received by the bot. Ignores messages from bots.
        """
        if message.author.bot:
            return  # Ignore messages from bots
        await self.process_commands(message)

if __name__ == '__main__':
    # Set up logging configuration
    logging.basicConfig(level=logging.INFO)

    # Get the default event loop
    loop = asyncio.get_event_loop()
    
    # Run the main coroutine until it completes
    loop.run_until_complete(run())