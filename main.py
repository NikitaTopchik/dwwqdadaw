import os
from discord.ext import commands
from up import keep_alive
import discord
import random
import asyncio
import requests
from quickdb import SQLITE
db = SQLITE()


def get_prefix(client, message):
    if not message.guild: return
    pref = db.get(f"prefix_{message.guild.id}")
    if pref == None:
       return "f!" # дефолтный префикс
    else:
       return pref

def get_all_members(client):
    allm = 0
    for g in client.guilds:
        for m in g.members:
            allm += 1
    return allm

client = commands.Bot(command_prefix = get_prefix, help_command=None, intents = discord.Intents.all())


ban_words = ['еблан, Еблан']


def simplify_word(word):
    last_letter = ''
    result = ''
    for letter in word:
        if letter != last_letter:
            last_letter = letter
            result += letter

    return result
  
@client.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, pref = None):
    if pref == None:
       return await ctx.send(embed=discord.Embed(title="<:no_check:963100302238679070> | Ошибка", description="Пожалуйста укажите префикс `f!setprefix [префикс]`", color=0xff9500))
    db.set(f"prefix_{ctx.guild.id}", pref)
    await ctx.send(embed=discord.Embed(title="<:yes_check:963100268692648106> | Успешно", description=f"Префикс изменен на '{pref}'", color=0xff9500))


@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author.bot:
        return

    msg_words = [simplify_word(word) for word in message.content.split()]

    for word in msg_words:
        if word in ban_words:
            try:
                await message.delete()
            except:
                print('Ошибка при удалении сообщения')
            await message.channel.send(
                f'{message.author.mention} **написал запрещенное слово:** `{word}`'
            )
            return


@client.command()
async def help(ctx):
  embed=discord.Embed(title="<:docs:958956360530272347> | Список команд", description="⠀", color=0xff8800) 
  embed.add_field(name=":video_game: | Развлечения", value=" f!cube - кубик рубика \n ", 
  inline=True)
  embed.add_field(name=":police_officer: | Модерация", value="  f!warn [участник] [причина] - выдать предупреждение участнику \n f!kick [участник] [причина] - выгнать участника \n f!ban [участник] - забанить участника \n f!unban [айди-участника] - разбанить участника \n ", 
  inline=True)
  embed.add_field(name=":page_with_curl: | Информация (бот)", value="f!help - хелп-меню \n f!ping - задержка бота (пинг) \n f!bot - Вывести информацию о боте \n ", 
  inline=False)
  embed.add_field(name="📋 | Информация (участник-сервер)", value="f!avatar - аватар участника \n f!serverinfo - информация о сервере \n ",
  inline=True)
  embed.add_field(name="🔧 | Утилиты", value="f!short [сыллка] - сократить сыллку \n f!poll [вопрос] - создать опрос \n f!invite [айди сервера] - получить сыллку на сервер по айди (на котором есть бот) \n f!servers - сервера на которых есть бот \n f!role [участник] [роль] - выдать роль участнику \n f!clear [сообщения] - удалить определенное количество сообщений \n f!dm [участник] [сообщение] - отправить сообщение участнику в лс \n f!embed [заголово-пиши-так] [описание-пишите-так] [футер пиши так] - создать эмблему по команде \n f!youtubes [запрос] - поиск видео в ютубе \n f!setprefix [префикс] - установить пользовательский префикс \n ", 
  inline=True)
  await ctx.send(embed=embed)
  print("была использована команда help \n")

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=1, limit_amount=1):
    await ctx.channel.purge(limit=amount+1)  
    author = ctx.message.author
    embed = discord.Embed(description= f'✅ Очищено успешно \n 👤 Очистил:{author} \n 📄 Количество: {amount} ')
    await ctx.send(embed=embed)

@client.command()
async def warn(ctx, member: discord.Member, *, reason):
    db.add(f'warns_{member.id}', 1)
    await ctx.send(f'Пользователю {member.mention} выдано предупреждение по причине: {reason}')

@client.command()
async def warns(ctx):
   warns = db.get(f'warns_{ctx.author.id}')
   if warns == None: warns = 0
   await ctx.send(f'У тебя {warns} предупреждений')
  

@client.command()
async def avatar(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author
    embed = discord.Embed(
        color=0xe67e22,
        title=f"Аватар участника - {member.name}",
        description=f"[Нажмите что бы скачать аватар]({member.avatar_url})")
    embed.set_image(url=member.avatar_url)
    await ctx.reply(embed=embed)
    print("была использована команда avatar \n")


@client.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, *, role: discord.Role):
    await member.add_roles(role)
    print("была использована команда role \n")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(
            embed=discord.Embed(title=":x: | **404**",
                                description=f'** Данная команда не найдена **',
                                color=0xe67e22))
        print("сработал ивент command_error \n")


@client.command()
async def embed(ctx, arg, arg1, *, arg2):
    embed = discord.Embed(title=arg, description=arg1, color=0xe67e22)
    embed.set_footer(text=arg2)
    await ctx.send(embed=embed)
    print("была использована команда embed \n")


@client.command()
async def serverinfo(ctx):
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)

    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(title=name + " Информация Сервера",
                          description=description,
                          color=0xe67e22)
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Создатель", value=owner, inline=True)
    embed.add_field(name="Айди сервера", value=id, inline=True)
    embed.add_field(name="Регион", value=region, inline=True)
    embed.add_field(name="Количество участников",
                    value=memberCount,
                    inline=True)

    await ctx.send(embed=embed)
    print("была использована команда serverinfo \n")


@client.command()
async def ping(ctx: commands.Context):
    emb = discord.Embed(
        description=
        f'** Состояние бота:** \n \n **Ping:** {round(client.latency * 1000)} ms.',
        color=0xe67e22)
    await ctx.send(embed=emb)
    print("была использована команда ping \n")


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason="No reason provided"):
    await user.kick(reason=reason)
    kick = discord.Embed(
        title=f":boot: Кикнут {user.name}!",
        description=f"Причина: {reason}\nКикнул: {ctx.author.mention}",
        color=0xe67e22)
    await ctx.message.delete()
    await ctx.channel.send(embed=kick)
    await user.send(embed=kick)
    print("была использована команда kick \n")


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, вы не указали пользователя')
        await ctx.message.purge(limit=1)
        await ctx.send(
            f'{ctx.author.mention}, у Вас недостаточно прав для использования этой команды!\nНедостающее право: Управлять сообщениями'
        )
        print("сработал ивент clear_error \n")


@client.command()
async def youtubes(ctx, *, arg1):
    emb = discord.Embed(
        title=':tada: | Успешно!',
        description=
        "Вот результаты повашему запросу: https://www.youtube.com/results?search_query="
        + arg1 + "",
        color=0xe67e22)
    await ctx.reply(embed=emb)
    print("была использована команда youtubes \n")


@client.command()
async def bot(ctx):
    emb = discord.Embed(
        title='ФСБ бот | Информация :bulb:',
        description=
        "Приветик! Меня зовут ФСБ бот, и возможно, я сделаю твоё пребывание в дискорде счастливым :ok_hand:\nВот кратенькая информация обо мне:\n\n:champagne_glass: Кол-во серверов:\n```"
        + str(len(client.guilds)) +
        "```\n🐍 Язык программирования:\n```Python 3.10.4```\n:notebook_with_decorative_cover: Библиотека:\n```discord.py```\n:star2: Дата создания:\n```08.04.2022```\n🧵 Последнее обновление:\n```08.06.2022```\n:trophy: Версия:\n```3.3.0 Release```",
        color=0xe67e22)
    await ctx.reply(embed=emb)
    print("была использована команда bot \n")


@client.command()
async def servers(ctx):
    r = [i.name for i in client.guilds]
    w = [i.id for i in client.guilds]
    await ctx.reply(
        embed=discord.Embed(title="сервера",
                            description=f"название\n \n{r}\nайди\n\n{w}",
                            color=discord.Color.red()))
    await ctx.message.delete()
    print("была использована команда rservers \n")


@client.command()
async def invite(ctx, server_id: int):
    guild = client.get_guild(server_id)
    invite = await guild.text_channels[0].create_invite(max_age=0,
                                                        max_uses=0,
                                                        temporary=False)
    await ctx.reply(f"https://discord.gg/{invite.code}")
    await ctx.message.delete()
    print("была использована команда cinviten \n")
  

@client.command()
async def cube(ctx):
    d = random.randint(0, 5)
    if d == 0:
        await ctx.send(
            "https://media.discordapp.net/attachments/929051187364392963/934154132670013530/Picsart_22-01-21_23-27-48-717.jpg"
        )
    if d == 1:
        await ctx.send(
            "https://media.discordapp.net/attachments/929051187364392963/934154132913274950/Picsart_22-01-21_23-28-46-761.jpg"
        )
    if d == 2:
        await ctx.send(
            "https://media.discordapp.net/attachments/929051187364392963/934154133399826452/Picsart_22-01-21_23-30-48-924.jpg"
        )
    if d == 3:
        await ctx.send(
            "https://media.discordapp.net/attachments/929051187364392963/934154133668253696/Picsart_22-01-21_23-31-28-515.jpg"
        )
    if d == 4:
        await ctx.send(
            "https://media.discordapp.net/attachments/929051187364392963/934154133903138816/Picsart_22-01-21_23-33-42-872.jpg"
        )
    if d == 5:
        await ctx.send(
            "https://media.discordapp.net/attachments/929051187364392963/934154134150594591/Picsart_22-01-21_23-34-37-760.jpg"
        )
        print("была использована команда cube \n")


@client.command()
@commands.has_permissions(manage_messages=True)
async def dm(ctx, member: discord.Member = None, *, msg):
    await member.send(msg)
    await ctx.message.delete()
    print("была использована команда dm \n")


@client.command()
async def short(ctx, *, link):
    response = requests.get(f'https://clck.ru/--?url={link}')
    await ctx.reply(content=f'<{response.text}>')


@client.command()
async def verify(ctx):
    author = ctx.message.author
    guild = client.get_guild(975371875339354142)
    role = guild.get_role(975373713170124850)

    await author.add_roles(role)
    embed = discord.Embed(
        title="Успешно!",
        description="Вы были верефицированы на сервере `ФСБ Бот`")
    await ctx.reply(embed=embed)


@client.command(aliases=["bn"])
@commands.has_permissions(ban_members=True)   
async def ban(context, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await context.send(f'{member} забанен')


@client.command(aliases=["ub"])
@commands.has_permissions(ban_members=True)   
async def unban(context, id : int):
    user = await client.fetch_user(id)
    await context.guild.unban(user)
    await context.send(f'{user.name} теперь разбанен')


@client.command(aliases=["p"])
@commands.has_permissions(manage_messages=True)
async def poll(ctx, *, content:str):
  await ctx.channel.purge(limit=1)
  embed=discord.Embed(title="Новый опрос", description=f"{content}",  color=0x95a5a6)
  message = await ctx.channel.send(embed=embed)
  await message.add_reaction("👍")
  await message.add_reaction("👎")


#@client.event
#async def on_ready():
    #await client.change_presence(activity=discord.Streaming(
        #name="Upgrade: 50%", url="https://www.twitch.tv/404"))

@client.event
async def on_ready():
    print("Готов к работе")
    
    client.loop.create_task(status_task())

async def status_task():
    while True:
        await client.change_presence(activity=discord.Streaming(name="f!help | 24/7 Host!", url="https://www.twitch.tv/404"))
        await asyncio.sleep(10)
        await client.change_presence(activity=discord.Streaming(name="f!help | " + str(len(client.guilds)) + " Серверов!", url="https://www.twitch.tv/404"))
        await asyncio.sleep(10)
        await client.change_presence(activity=discord.Streaming(name= f"f!help | {get_all_members(client)} Участников", url="https://www.twitch.tv/404"))
        await asyncio.sleep(10)
        await client.change_presence(activity=discord.Streaming(name="f!help | Version: 3.3.0 Release", url="https://www.twitch.tv/404"))
        await asyncio.sleep(10)
        await client.change_presence(activity=discord.Streaming(name="f!help | Новый ФСБ Бот!", url="https://www.twitch.tv/404"))

keep_alive()
TOKEN = os.environ.get("")
client.run(OTg1MjQ2MzkxNjcwNTQyMzQ2.GF6S-o.RC4ao-8DLnGLPErdP9LH-KJhEflqrCiqYeveIM)