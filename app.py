import discord
from discord.ext import commands
import discord.app_commands
from groq import Groq

groq = Groq(api_key="GroqのAPIキーをここに")
current = "main"

intents = discord.Intents.all()
client = discord.Client(intents=intents)
slash = discord.app_commands.CommandTree(client)

async def setup_hook():
    global slash
    await slash.sync()
client.setup_hook = setup_hook

instances = {
    "main": [
        {
            "role": "system",
            "content": "あなたは日本語で答えないといけません",
        },
    ]
}

def chat(prompt: str):
    global client, instances, current
    messages = instances[current]
    messages.append({
        "role": "user",
        "content": prompt,
    })
    chat_completion = groq.chat.completions.create(
        messages = messages,
        temperature = 0.2,
        model = "llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

@client.event
async def on_ready():
    print('Logged in!')

@slash.command(name="instance-create", description="Create instance")
@discord.app_commands.describe(name="Name of the instance", setting="Setting of the chat")
async def new(ctx, name: str, setting: str):
    global instances, current
    instances[name] = [
         {
             "role": "system",
             "content": setting,
         },
    ]
    await ctx.response.send_message(f"New instance is created of {name}!")

@slash.command(name="show-current", description="Show current instance")
async def show(ctx):
    global instances, current
    def format_history(x):
        return f"{x['role']}: \"{x['content']}\""
    text = "\n".join(list(map(format_history, instances[current])))
    await ctx.response.send_message(f'Current instance is "{current}".\nMessage history is below:\n{text}')


@slash.command(name="instance-change", description="Change current instance")
@discord.app_commands.describe(name="Name of the instance")
async def change(ctx, name: str):
    global instances, current
    if name in instances:
        current = name
        await ctx.response.send_message(f"current instance is changed: {name}!")
    else:
        await ctx.response.send_message(f"Error! the instance is not exist")

@slash.command(name="instance-delete", description="Change current instance")
async def delete(ctx):
    global instances, current
    if current in instances:
        del instances[current]
        await ctx.response.send_message(f"current instance is deleted!")
    else:
         await ctx.response.send_message(f"Error! the instance is not exist")


async def reply(message):
    async with message.channel.typing():
        content = message.content.replace("<@1296442378760093717>", "").strip();
        if (result := chat(content)) != "":
            await message.channel.send(result)
            print(f'reply of "{content}" is "{result}"')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user in message.mentions:
        await reply(message)

client.run("Discordボットのトークンをここに")
