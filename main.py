import discord
import requests
from discord.ext import commands, tasks



default_intents = discord.Intents.default().all()
default_intents.members = True
client = commands.Bot(command_prefix=None, help_command=None, intents=default_intents)

channels = [
    "duswl1214", 
    "bossberry_"
]

status = {}



def is_stream(channel:str):
    return requests.post(
        "https://gql.twitch.tv/gql#origin=twilight", 
        json={
            "operationName":"ReportMenuItem",
            "variables":{
                "channelLogin":channel
            },"extensions":{
                "persistedQuery":{
                    "version":1,
                    "sha256Hash":"8f3628981255345ca5e5453dfd844efffb01d6413a9931498836e6268692a30c"
                }
            }
        }, 
        headers={
            "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"
        }).json()["data"]["user"]["stream"] != None

@client.event
async def on_ready():
    for channel in channels:
        status[channel] = None
    task_loop.start()
    print(f"Connecté à {client.user.name}")

@tasks.loop(minutes=5)
async def task_loop():
    edit = False
    for channel in channels:
        s = is_stream(channel)
        if s != status[channel]:
            edit = True
        status[channel] = s

    if edit:
        pass

client.run('TOKEN')
