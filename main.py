import os
from scrapper import NotifierVinted
import discord
from discord.ext import commands, tasks

researches = []

#instanciation du scrapper des pantalons
url = "https://www.vinted.fr/vetements?search_text=&catalog[]=261&brand_id[]=51989&brand_id[]=1755472&brand_id[]=364&size_id[]=206&size_id[]=207&order=newest_first"
filename = "pants.csv"
channel = 942125386735698020
pants = NotifierVinted(filename, url, channel)
researches.append(pants)

#instanciation du scrapper de ralph lauren
url = "https://www.vinted.fr/vetements?search_text=&brand_id[]=88&size_id[]=208&catalog[]=79&price_from=7&currency=EUR&price_to=20&order=newest_first"
filename = "ralph.csv"
channel = 828980947026313236
ralph = NotifierVinted(filename, url, channel)
researches.append(ralph)

#instanciation du scrapper t-shirt kaws
url = "https://www.vinted.fr/vetements?search_text=kaws&catalog[]=261&catalog[]=77&order=newest_first&size_id[]=208&brand_id[]=1153&brand_id[]=353723"
filename = "kaws.csv"
channel = 942159879982968913
kaws = NotifierVinted(filename, url, channel)
researches.append(kaws)

for research in researches:
    research.run()

#bot discord
client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    scrapper.start()
    print("Bot is online !")

@client.command()
async def clear(ctx, amount=10):
    """clear le chat"""
    await ctx.channel.purge(limit=amount+1) #+1 pour supprimer le message de commande aussi

#execute le scrapping toutes les minutes
@tasks.loop(seconds=60)
async def scrapper():#nouvelle recherche
    if not researches[0].searching_items:
        researches[0].searching_items == True
        print("new research!")
        for research in researches:
            new_items = research.get_new_items()

            #channel de notification
            channel = client.get_channel(research.channel)

            #si nouveaux items préparation envoie notifs
            if new_items:
                for new_item in new_items:
                    embed = discord.Embed()
                    embed.title = new_item['name']
                    embed.set_image(url=new_item['image'])
                    embed.description = f'price: {new_item["price"]}\nsize: {new_item["size"]}'
                    embed.url = new_item['link']
                    await channel.send(embed=embed)
        researches[0].searching_items


client.run("ODE5NzA3OTY4MTkwNDE0ODU4.YEqiiQ.c7UjyL50r6LQBzygX3y-CDDQ_Zw")