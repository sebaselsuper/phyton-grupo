import discord
from discord.ext import commands
import random
import asyncio
import os
import yt_dlp as youtube_dl
import requests
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hola, soy un bot {bot.user}!')

@bot.command()
async def heh(ctx, count_heh=5):
    await ctx.send("he" * count_heh)

@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    if member.joined_at is None:
        await ctx.send(f'{member} has no join date.')
    else:
        await ctx.send(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

# FIX para yt_dlp
youtube_dl.utils.bug_reports_message = lambda *args, **kwargs: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4
}

ffmpeg_options = {
    'options': '-vn'  # sin video
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command()
async def play(ctx, *, url):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("¡No estás conectado a un canal de voz!")

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f'Reproduciendo: {player.title}')

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("¡No estoy conectado a un canal de voz!")

@bot.command()
async def meme(ctx):
    imagenes = os.listdir('meme')
    with open(f'meme/{random.choice(imagenes)}', 'rb') as f:
        # ¡Vamos a almacenar el archivo de la biblioteca Discord convertido en esta variable!
        picture = discord.File(f)
    # A continuación, podemos enviar este archivo como parámetro.
    await ctx.send(file=picture)

def get_duck_image_url():    
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']


@bot.command('duck')
async def duck(ctx):
    '''Una vez que llamamos al comando duck, 
    el programa llama a la función get_duck_image_url'''
    image_url = get_duck_image_url()
    await ctx.send(image_url)

def get_dog_image_url():    
    url = 'https://random.dog/woof.json'
    res = requests.get(url)
    data = res.json()
    return data['url']


@bot.command('dog')
async def dog(ctx):
    '''Una vez que llamamos al comando dog, 
    el programa llama a la función get_dog_image_url'''
    image_url = get_dog_image_url()
    await ctx.send(image_url)

def get_pokemon():
    pokemon_id = random.randint(1, 151)  # primeros 151 (generación 1)
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}'
    res = requests.get(url)
    data = res.json()
    nombre = data['name'].capitalize()
    imagen = data['sprites']['front_default']
    return nombre, imagen
@bot.command('pokemon')
async def pokemon(ctx):
    nombre, imagen = get_pokemon()
    embed = discord.Embed(title=f"🎮 ¡Has encontrado a {nombre}!")
    embed.set_image(url=imagen)
    await ctx.send(embed=embed)

#Buscar información de un anime usando la API de Kitsu
def buscar_anime(texto):
    url = f'https://kitsu.io/api/edge/anime?filter[text]={texto}'
    res = requests.get(url)
    data = res.json()
    if not data['data']:
        return None
    anime = data['data'][0]['attributes']
    titulo = anime['canonicalTitle']
    sinopsis = anime['synopsis'][:400] + "..."
    imagen = anime['posterImage']['original']
    return titulo, sinopsis, imagen
@bot.command('anime')
async def anime(ctx, *, nombre_anime):
    resultado = buscar_anime(nombre_anime)
    if resultado:
        titulo, sinopsis, imagen = resultado
        embed = discord.Embed(title=f"🎌 {titulo}", description=sinopsis)
        embed.set_image(url=imagen)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ No encontré ningún anime con ese nombre.")

bot.run("")
