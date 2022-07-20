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

@bot.event
async def on_ready():
    print(F"Logged in as {bot.user}")

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
    await interaction.response.send_message(text)

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="whoami",
    description="show your brief intro",
)
async def whoami(interaction: nextcord.Interaction) -> None:
    await interaction.response.send_message("遵命，汝為 {}【ID: {}】".format(interaction.user.name,interaction.user.id))

@bot.slash_command(
    guild_ids=[readT("settings.toml","server",do=int)],
    name="channel",
    description="show my target channel",
)
async def channel(interaction: nextcord.Interaction) -> None:
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

    else:
        await ctx.respond("目標頻道不在本伺服器内")

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
