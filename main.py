import tomlkit, nextcord, pathlib, datetime
from nextcord import SlashOption
from nextcord.ext import commands

def readT(part_str: str, entry_str: str, do=dict):
    if pathlib.Path(part_str).exists():
        return do(tomlkit.load(open(part_str))[entry_str])
    else:
        return do()
def writeT(part_str: str, entry_str: str, value_obj):
    if pathlib.Path(part_str).exists():
        entry_doc = tomlkit.load(open(part_str))
    else:
        entry_doc = tomlkit.document()
    entry_doc[entry_str] = value_obj
    with open(part_str,'w') as target_handle:
        tomlkit.dump(entry_doc,target_handle)

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(Intents=intents)

def is_author(interaction):
    return interaction.user.id in [int(n) for n in readT("settings.toml","author",do=list)]

@bot.event
async def on_ready():
    print(F"Logged in as {bot.user} [{bot.user.id}]")

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="echo",
    description="repeats the given text",
)
async def echo(
    interaction: nextcord.Interaction,
    text: str = SlashOption(
        name="text",
        description="text to repeat",
    )
):
    if is_author(interaction):
        await interaction.response.send_message(text)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="whoami",
    description="show your brief intro",
)
async def whoami(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        await interaction.response.send_message("遵命，汝為 {}【ID: {}】".format(interaction.user.name,interaction.user.id))

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="show_channel",
    description="show my target channel",
)
async def show_channel(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        channel_str = readT("settings.toml","channel",do=str)
        await interaction.response.send_message(F"遵命，目標頻道為 <#{channel_str}>")

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="set_channel",
    description="change target channel",
)
async def set_channel(
    interaction: nextcord.Interaction,
    link: str = SlashOption(
        name="link",
        description="https://dis...com/ch...s/123/123 form",
    )
) -> None:
    if is_author(interaction):
        target_msg = link.replace(" ","/")
        target_list = target_msg.split("/")
        server_str = readT("settings.toml","server",do=str)
        if server_str in target_list:
            channel_str = target_list[-1]
            channel_int = int(channel_str)
            writeT("settings.toml","channel",channel_int)
            await interaction.response.send_message(F"目標頻道設定為 <#{channel_str}>")
        else:
            await interaction.response.send_message("目標頻道不在本伺服器内")

async def update_thread(interaction: nextcord.Interaction) -> None:
    thread_list = await interaction.guild.active_threads()
    if pathlib.Path("thread.toml").exists():
        thread_doc = tomlkit.load(open("thread.toml"))
    else:
        thread_doc = tomlkit.document()
    for thread_obj in thread_list:
        parent_id_str = str(thread_obj.parent_id)
        parent_table = thread_doc.get(parent_id_str,tomlkit.table())
        parent_table[str(thread_obj.id)] = thread_obj.name
        thread_doc[parent_id_str] = parent_table
    with open("thread.toml","w") as toml_handle:
        tomlkit.dump(thread_doc,toml_handle)

async def send_thread_list(interaction: nextcord.Interaction, exclude_list: list=list()) -> str:
    if pathlib.Path("thread.toml").exists():
        thread_doc = tomlkit.load(open("thread.toml"))
    else:
        thread_doc = tomlkit.document()
    server_int = readT("settings.toml","server",do=int)
    msg_channel_str = '【<#{}> 頻道】'
    msg_thread_str = '＃{} 討論串：\nhttps://discord.com/channels/{}/{}'
    msg_list = list()
    for channel_id_str, thread_table in thread_doc.items():
        memory_thread_dict = {str(x):str(y) for x,y in thread_table.items() if int(x) not in exclude_list}
        if len(memory_thread_dict) > 0:
            msg_list.append(msg_channel_str.format(channel_id_str))
            msg_list.extend([msg_thread_str.format(name_str,server_int,id_str) for id_str,name_str in memory_thread_dict.items()])
            msg_list.append("\t")
    output_msg_list = list()
    output_msg = ""
    for msg_str in msg_list:
        if len(output_msg+"\n"+msg_str) > 1800:
            output_msg_list.append(output_msg)
            output_msg = msg_str
        else:
            output_msg = output_msg+"\n"+msg_str
    output_msg_list.append(output_msg)
    channel_int = readT("settings.toml","channel",do=int)
    target_id_int = 0
    if len(output_msg_list) > 0:
        for output_msg in output_msg_list:
            if target_id_int == 0:
                target_msg = await interaction.guild.get_channel(channel_int).send(output_msg)
                target_id_int = target_msg.id
            else:
                await interaction.guild.get_channel(channel_int).send(output_msg)
    else:
        target_msg = await interaction.guild.get_channel(channel_int).send("錯誤 - 查無資料")
        target_id_int = target_msg.id
    reply_str = F"完成！請前往<#{channel_int}>查看\n🔗：https://discord.com/channels/{server_int}/{channel_int}/{target_id_int}"
    return reply_str

# @bot.slash_command(
#     guild_ids=[readT("settings.toml","server",do=int)],
#     name="show_active",
#     description="show active threads",
# )
# async def show_active(interaction: nextcord.Interaction) -> None:
#     if is_author(interaction):
#         thread_list = await interaction.guild.active_threads()
#         await update_thread(interaction)
#         thread_str = "\n".join(["{}: <#{}>".format(n.name,n.id) for n in thread_list])
#         if thread_str == "":
#             thread_str = "沒有活躍的討論串"
#         await interaction.response.send_message(thread_str)

# @bot.slash_command(
#     guild_ids=[readT("settings.toml","server",do=int)],
#     name="show_archived",
#     description="show archived threads",
# )
# async def show_archived(interaction: nextcord.Interaction) -> None:
#     if is_author(interaction):
#         thread_list = await interaction.guild.active_threads()
#         thread_id_list = [n.id for n in thread_list]
#         reply_str = await send_thread_list(interaction, exclude_list=thread_id_list)
#         await interaction.response.send_message(reply_str)

# @bot.slash_command(
#     guild_ids=[readT("settings.toml","server",do=int)],
#     name="show_memory",
#     description="show threads that store in memory",
# )
# async def show_memory(interaction: nextcord.Interaction) -> None:
#     if is_author(interaction):
#         reply_str = await send_thread_list(interaction)
#         await interaction.response.send_message(reply_str)

# @bot.slash_command(
#     guild_ids=[readT("settings.toml","server",do=int)],
#     name="push",
#     description="push update",
# )
# async def push_update(interaction: nextcord.Interaction,sub=False) -> None:
#     if is_author(interaction):
#         await update_thread(interaction)
#         reply_str = await send_thread_list(interaction)
#         if sub:
#             return reply_str
#         else:
#             await interaction.response.send_message(reply_str)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="delete",
    description="delete bot msgs in target channel",
)
async def delete(interaction: nextcord.Interaction,sub=False) -> None:
    if is_author(interaction):
        msg_list = list()
        channel_int = readT("settings.toml","channel",do=int)
        now_date = datetime.datetime.now()
        ten_days = now_date - datetime.timedelta(days=10)
        async for msg in interaction.guild.get_channel(channel_int).history(limit=100,after=ten_days):
            if msg.author.id == bot.user.id:
                msg_list.append(msg)
        await interaction.guild.get_channel(channel_int).delete_messages(msg_list)
        reply_str = "已刪除 {} 個訊息".format(len(msg_list))
        if sub:
            return reply_str
        else:
            await interaction.response.send_message(reply_str)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="update",
    description="update thread list",
)
async def update(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        reply_delete_str = await delete(interaction,sub=True)
        reply_push_str = await push_update(interaction,sub=True)
        await interaction.response.send_message(F"{reply_delete_str}\n{reply_push_str}")

token = open("token.txt").read().splitlines()[0]
bot.run(token)
