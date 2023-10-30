from config import bot
from telethon import events
import pahe, kwik_token, helper
from FastTelethonhelper import fast_upload
import os

@bot.on(events.NewMessage(pattern="/start"))
async def _(event):
    await event.reply("Go Away.")


@bot.on(events.NewMessage(pattern="/search"))
async def _(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message('What is the name of the anime you want?')
        anime_name = await conv.get_response()
        anime_name = anime_name.raw_text
        await conv.send_message('loading...')
        options = pahe.search_apahe(anime_name)["data"]
        txt = "Choose from options below, reply a number only\n"
        for n, i in enumerate(options):
            txt += f"{n+1}. {i['title']}\n"
        
        await conv.send_message(txt)
        answer = await conv.get_response()
        answer = int(answer.raw_text) - 1
        choice = options[answer]
        txt=f"Title:{choice['title']}\nType:{choice['type']}\nEpisodes:{choice['episodes']}\nStatus:{choice['status']}"
        await conv.send_message(txt, file=choice["poster"])
        
        await conv.send_message("The episode range you want. example: 1-6")
        range = await conv.get_response()
        range = list(map(int, range.raw_text.split("-")))
        eps_ids = pahe.mid_apahe(choice["session"], range)
        eps_list = pahe.dl_apahe1(choice["session"], eps_ids)
        resolutions = "Choose option to download. Reply with number only\n0.All resolutions\n"
        for n, i in enumerate(eps_list[1]):
            resolutions += f"{n+1}. {i[1]} {i[2]}\n"

        await conv.send_message(resolutions)
        resolution_choice = await conv.get_response()
        resolution_choice = int(resolution_choice.raw_text) - 1
        
        await conv.send_message("Send me file name you want on these files in the following format.\nAnime Name - S1 UwU RES LANG.mkv\n UwU will be replaced by ep number.\nRES will be replaced by resolution\nLANG will be replaced by either sub/dub")
        name_format = await conv.get_response()
        name_format = name_format.raw_text.strip()
        thumb = choice["poster"]
        thumb = await helper.DownLoadFile(thumb, file_name="thumb.png")

    if resolution_choice == -1:
        for k, v in eps_list.items():
            for i in v:
                dl_link = pahe.dl_apahe2(i[0])
                dl_link = kwik_token.get_dl_link(dl_link)
                ep_num = k + range[0] - 1
                res = i[1].split()[0]
                lang = i[2]
                file_name = name_format.replace("UwU", str(ep_num)).replace("RES", res).replace("LANG", lang)
                reply = await event.reply(f"Starting download {file_name}")
                
                file = await helper.DownLoadFile(dl_link, file_name=file_name)
                res_file = await fast_upload(client = bot, file_location = file, reply = reply)
                await bot.send_message(event.chat_id, f"{file_name.replace('.mkv', '').replace('.mp4', '')}", file=res_file, force_document=True, thumb=thumb)
                reply.delete()
                os.remove(file)
    
    else:
        for k, v in eps_list.items():
            dl_link = pahe.dl_apahe2(v[resolution_choice][0])
            dl_link = kwik_token.get_dl_link(dl_link)
            ep_num = k + range[0] - 1
            res = v[resolution_choice][1]
            lang = v[resolution_choice][2]
            file_name = name_format.replace("UwU", str(ep_num)).replace("RES", str(res)).replace("LANG", lang)
            reply = await event.reply(f"Starting download {file_name}")
            file = await helper.DownLoadFile(dl_link, file_name=file_name)

            res_file = await fast_upload(client = bot, file_location = file, reply = reply)
            await bot.send_message(event.chat_id, f"{file_name.replace('.mkv', '').replace('.mp4', '')}", file=res_file, force_document=True, thumb=thumb)
            os.remove(file)
            reply.delete()


bot.start()

bot.run_until_disconnected()