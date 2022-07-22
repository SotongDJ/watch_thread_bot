from discord import SlashOption
import tomlkit, nextcord, pathlib
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

bot = commands.Bot()

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

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="show_active",
    description="show active threads",
)
async def show_active(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        thread_list = await interaction.guild.active_threads()
        update_thread(interaction)
        thread_str = "\n".join(["{}: <#{}>".format(n.name,n.id) for n in thread_list])
        if thread_str == "":
            thread_str = "no active thread"
        await interaction.response.send_message(thread_str)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="show_archived",
    description="show archived threads",
)
async def show_archived(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        thread_list = await interaction.guild.active_threads()
        thread_id_list = [n.id for n in thread_list]
        if pathlib.Path("thread.toml").exists():
            thread_doc = tomlkit.load(open("thread.toml"))
        else:
            thread_doc = tomlkit.document()
        memory_dict = dict()
        for thread_table in thread_doc.values():
            memory_thread_dict = {str(x):str(y) for x,y in thread_table.items() if int(x) not in thread_id_list}
            if len(memory_thread_dict) > 0:
                memory_dict.update(memory_thread_dict)
        msg_str = '＃{} 討論串：\nhttps://discord.com/channels/{}/{}'
        server_str = readT("settings.toml","server",do=int)
        thread_str = "\n".join([msg_str.format(name_str,server_str,id_str) for id_str,name_str in memory_dict.items()])
        await interaction.response.send_message(thread_str)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="show_memory",
    description="show threads that store in memory",
)
async def show_memory(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        if pathlib.Path("thread.toml").exists():
            thread_doc = tomlkit.load(open("thread.toml"))
        else:
            thread_doc = tomlkit.document()
        server_str = readT("settings.toml","server",do=int)
        msg_channel_str = '【<#{}> 頻道討論串】'
        msg_thread_str = '＃{} 討論串：\nhttps://discord.com/channels/{}/{}'
        msg_list = list()
        for channel_id_str, thread_table in thread_doc.items():
            memory_thread_dict = {str(x):str(y) for x,y in thread_table.items()}
            if len(memory_thread_dict) > 0:
                msg_list.append(msg_channel_str.format(channel_id_str))
                msg_list.extend([msg_thread_str.format(name_str,server_str,id_str) for id_str,name_str in memory_thread_dict.items()])
                msg_list.append("")
        thread_str = "\n".join(msg_list)
        await interaction.response.send_message(thread_str)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="push",
    description="push update",
)
async def push_update(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        if pathlib.Path("thread.toml").exists():
            thread_doc = tomlkit.load(open("thread.toml"))
        else:
            thread_doc = tomlkit.document()
        server_str = readT("settings.toml","server",do=int)
        msg_channel_str = '【<#{}> 頻道討論串】'
        msg_thread_str = '＃{} 討論串：\nhttps://discord.com/channels/{}/{}'
        msg_list = list()
        for channel_id_str, thread_table in thread_doc.items():
            memory_thread_dict = {str(x):str(y) for x,y in thread_table.items()}
            if len(memory_thread_dict) > 0:
                msg_list.append(msg_channel_str.format(channel_id_str))
                msg_list.extend([msg_thread_str.format(name_str,server_str,id_str) for id_str,name_str in memory_thread_dict.items()])
                msg_list.append("")
        thread_str = "\n".join(msg_list)
        channel_int = readT("settings.toml","channel",do=int)
        target_msg = await interaction.guild.get_channel(channel_int).send(thread_str)
        reply_str = F"完成！請前往<#{channel_int}>查看\n🔗：https://discord.com/channels/{server_str}/{channel_int}/{target_msg.id}"
        await interaction.response.send_message(reply_str)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="delete",
    description="delete bot msgs in target channel",
)
async def delete(interaction: nextcord.Interaction) -> None:
    if is_author(interaction):
        msg_list = list()
        channel_int = readT("settings.toml","channel",do=int)
        async for msg in interaction.guild.get_channel(channel_int).history(limit=100):
            if msg.author.id == bot.user.id:
                msg_list.append(msg)
        # reply_str = "\n".join([n.content for n in msg_list])
        # await interaction.response.send_message(reply_str)
        await interaction.guild.get_channel(channel_int).delete_messages(msg_list)
        await interaction.response.send_message("Deleted msg count: {}".format(len(msg_list)))

token = open("token.txt").read().splitlines()[0]
bot.run(token)
"""
    if message.content.startswith('急急如律令之更新列表'):
        author_list = readJ("settings.json","author")
        if message.author.id in author_list:
            record_dict = dict()
            if pathlib.Path("record.json").exists():
                record_dict.update({int(x):y for x,y in json.load(open("record.json")).items()})
            for guild in client.get_all_channels():
                if isinstance(guild, discord.TextChannel):
                    for thread in guild.threads:
                        record_dict[thread.id] = {"parent_id":thread.parent_id,"name":thread.name}
            server_str = readJ("settings.json","server")
            channel_str = readJ("settings.json","channel")
            target_id_list = readJ("settings.json","anchor")
            target_channel = client.get_channel(channel_str)
            async for history_message in target_channel.history(limit=200):
                if history_message.author == client.user and target_id_list == list():
                    target_id_list = [history_message.id]
            hi_msg = await message.channel.send('收到，處理資訊中')
            with open("record.json",'w') as target_handle:
                json.dump(record_dict,target_handle,indent=0)
            sorted_thread_list = sorted([n for n in record_dict.keys()], key=lambda x : record_dict[x]["parent_id"])
            beautify_msg_list = list()
            # beautify_embed_msg_list = list()
            beauty_msg = '＃{n} 討論串：\nhttps://discord.com/channels/{s}/{c}'
            # beauty_embed_none_msg = '現在在 <#{p}> 有開啟 ＃{n} 討論串，\n歡迎到討論串參與討論'
            # beauty_embed_text_msg = '現在在 <#{p}> 有開啟 ＃{n} 討論串，\n歡迎到討論串參與討論（<#{c}>）'
            for k in sorted_thread_list:
                # thread_channel = client.get_channel(k)
                beautify_msg_list.append(beauty_msg.format(n=record_dict[k]["name"],s=server_str,c=k))
                # if isinstance(thread_channel, NoneType):
                #     beautify_embed_msg_list.append(beauty_embed_none_msg.format(p=record_dict[k]["parent_id"],n=record_dict[k]["name"]))
                # else:
                #     beautify_embed_msg_list.append(beauty_embed_text_msg.format(p=record_dict[k]["parent_id"],n=record_dict[k]["name"],c=k))
            if target_id_list != list():
                for target_id in target_id_list:
                    delete_msg = await target_channel.fetch_message(target_id)
                    await delete_msg.delete()
            \"""
            embed_msg = discord.Embed(
                title="討論串集散地", 
                description="\n".join(beautify_embed_msg_list), 
                color=discord.Color.blue()
            )
            \"""
            # target_msg = await target_channel.send(content="\n".join(beautify_msg_list),embed=embed_msg)
            # output_msg = "\n".join(beautify_embed_msg_list) + "\n\n" + "\n".join(beautify_msg_list)
            # output_msg = "\n".join(beautify_msg_list)
            output_msg = ""
            output_msg_list = list()
            for beautify_msg_str in beautify_msg_list:
                if len(output_msg+"\n"+beautify_msg_str) > 1800:
                    output_msg_list.append(output_msg)
                    output_msg = beautify_msg_str
                else:
                    output_msg = output_msg+"\n"+beautify_msg_str
            target_id_list = list()
            link_list = list()
            for output_msg in output_msg_list:
                target_msg = await target_channel.send(content=output_msg)
                target_id_list.append(target_msg.id)
                link_list.append(F"🔗：https://discord.com/channels/{server_str}/{channel_str}/{target_msg.id}")
            await hi_msg.edit(content=F"完成！請前往<#{channel_str}>查看\n"+"\n\n".join(link_list))
            writeJ("settings.json","anchor",target_id_list)
"""
