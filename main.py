from types import NoneType
import discord, logging, datetime, json, pathlib

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
output_str = 'run-{}.log'.format(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8),name="UTC+8")).strftime("%Y%m%d"))
handler = logging.FileHandler(filename=output_str, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def readJ(part_str,entry_str):
    return json.load(open(part_str))[entry_str]
def writeJ(part_str,entry_dict):
    with open(part_str,'w') as target_handle:
        json.dump(entry_dict,target_handle,indent=0)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('急急如律令之列出ID'):
        await message.channel.send("聽命於 {}【{}】".format(message.author.name,message.author.id))
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
            target_id = readJ("settings.json","anchor")
            target_channel = client.get_channel(channel_str)
            async for history_message in target_channel.history(limit=200):
                if history_message.author == client.user and target_id == 0:
                    target_id = history_message.id
            hi_msg = await message.channel.send('收到，處理資訊中')
            with open("record.json",'w') as target_handle:
                json.dump(record_dict,target_handle,indent=0)
            sorted_thread_list = sorted([n for n in record_dict.keys()], key=lambda x : record_dict[x]["parent_id"])
            beautify_msg_list = list()
            beautify_embed_msg_list = list()
            beauty_msg = '＃{n} 討論串： https://discord.com/channels/{s}/{c}'
            beauty_embed_none_msg = '現在在 <#{p}> 有 ＃{n} 討論串，歡迎到 [＃{n}](https://discord.com/channels/{s}/{c}) 討論串參與討論'
            beauty_embed_text_msg = '現在在 <#{p}> 有開啟 ＃{n} 討論串，歡迎到 <#{c}> 討論串參與討論'
            for k in sorted_thread_list:
                thread_channel = client.get_channel(k)
                beautify_msg_list.append(beauty_msg.format(n=record_dict[k]["name"],s=server_str,c=k))
                if isinstance(thread_channel, NoneType):
                    beautify_embed_msg_list.append(beauty_embed_none_msg.format(p=record_dict[k]["parent_id"],n=record_dict[k]["name"],s=server_str,c=k))
                else:
                    beautify_embed_msg_list.append(beauty_embed_text_msg.format(p=record_dict[k]["parent_id"],n=record_dict[k]["name"],c=k))
            if target_id != 0:
                delete_msg = await target_channel.fetch_message(target_id)
                await delete_msg.delete()
            embed_msg = discord.Embed(
                title="討論串集散地", 
                description="\n".join(beautify_embed_msg_list), 
                color=discord.Color.blue()
            )
            target_msg = await target_channel.send(content="\n".join(beautify_msg_list),embed=embed_msg)
            await hi_msg.edit(content=F"完成！請前往<#{channel_str}>查看\n🔗：https://discord.com/channels/{server_str}/{channel_str}/{target_msg.id}")

token = open("token.txt").read().splitlines()[0]
client.run(token)
