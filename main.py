import pickle
import discord
import requests
from discord.ext import commands, tasks

default_intents = discord.Intents.default().all()
default_intents.members = True
client = commands.Bot(command_prefix="!ts ", help_command=None, intents=default_intents, activity=discord.Streaming(name="Status: !ts help", url="https://www.twitch.tv/game_k_"))

try:
    with open("env.pkl", "rb") as file:
        channel_id, channel_status = pickle.load(file)
except:
    channel_id = 1112725656187453551
    channel_status = {}

def init_channels():
    # read channel file and init in dict if not exist
    for channel in open("./channels.txt", "r", encoding="utf8").read().split("\n"):
        if channel != "" and not channel.startswith("#") and channel not in channel_status.keys():
            channel_status[channel] = None

def save():
    with open("env.pkl", "wb") as file:
        pickle.dump([
            channel_id, 
            channel_status
        ], file)

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
    init_channels()
    task_loop.start()
    print(f"Connecté à {client.user.name}")

@tasks.loop(minutes=2)
async def task_loop():
    init_channels()
    for channel in channel_status.keys():
        status = is_stream(channel)
        if not channel_status[channel] and status:
            ctx = client.get_channel(channel_id)
            await ctx.send(f"**{channel}** est actuellement en live\nhttps://www.twitch.tv/{channel}")
        channel_status[channel] = status
    save()

@client.command()
async def help(ctx):
    await ctx.send("""```
┌─────────────────────────────────────────────────────────────────────┐
│                            TWITCH STATUS                            │
├─────────────────────────────────────────────────────────────────────┤
│     Préfix  : !ts                                                   │
│     Syntaxe : !ts <command>                                         │
├────────────────────────┬────────────────────────────────────────────┤
│        COMMAND         │                DESCRIPTION                 │
├────────────────────────┼────────────────────────────────────────────┤
│help                    │Affiche ce message                          │
│live                    │Cite toutes les chaînes enregisré et en live│
│append (add) <channel>  │Ajouter une chaîne à la liste               │
│remove (del) <channel>  │Supprimer une chaîne de la liste            │
│length (len)            │Affiche la longueur de la liste             │
│channels (all)          │Affiche toutes les chaînes enregisré        │
│status (get) <channel>  │Affiche le status de la chaîne demandé      │
└────────────────────────┴────────────────────────────────────────────┘```""")

@client.command()
async def live(ctx):
    live_channel = [channel for channel in channel_status.keys() if channel_status[channel]]
    if len(live_channel) > 0:
        live_channel = "**\n**".join(live_channel)
        await ctx.send(f"Voici la liste des personnes actuellement en live:\n**{live_channel}**")
    else:
        await ctx.send("😔 Désolé, d'après ma liste il n'y a pas de live")

@client.command(aliases=["add"])
async def append(ctx, channel):
    if channel in channel_status.keys():
        await ctx.send(f"🧐 Pas besoin, **{channel}** est **déjà enregistré** dans la liste")
    else:
        try:
            s = is_stream(channel)
            channel_status[channel] = s
            await ctx.send(f"😉👍 OK, **{channel}** a été **ajouté** à la liste")
            save()
        except:
            await ctx.send(f"😔 Désolé, mais je n'arrive pas à accéder à **{channel}**. Es-tu sûr de la syntaxe de la chaîne ?")

@client.command(aliases=["del"])
async def remove(ctx, channel):
    del channel_status[channel]
    await ctx.send(f"😉👍 OK, **{channel}** a été **supprimé** à la liste")
    save()

@client.command(aliases=["len"])
async def length(ctx):
    await ctx.send(f"Il y a actuellement **{len(channel_status.keys())}** chaîne(s) enregistré(s) dans la liste")

@client.command(aliases=["all"])
async def channels(ctx):
    channels_ = "**\n- **".join(channel_status.keys())
    await ctx.send(f"Voici ma liste:\n- **{channels_}**")

@client.command(aliases=["get"])
async def status(ctx, channel):
    try:
        is_recorded = ", mais cette chaîne n'est pas enregistré dans la liste" if channel not in channel_status.keys() else ""
        if is_stream(channel):
            await ctx.send(f"😉👍 Oui, **{channel}** est en live" + is_recorded)
        else:
            await ctx.send(f"😔 Non, **{channel}** n'est pas en live" + is_recorded)
    except:
        await ctx.send(f"😔 Désolé, mais je n'arrive pas à accéder à **{channel}**. Es-tu sûr de la syntaxe de la chaîne ?")

client.run(open("./token.txt", "r", encoding="utf8").read())
