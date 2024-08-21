import discord 
import time
import asyncio

from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from yt_dlp import YoutubeDL

async def setup(bot):
    await bot.add_cog(music_cog(bot))

class music_cog(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None
    
    def search_yt(self, item): 
        with YoutubeDL(self.YDL_OPTIONS) as ydl: 
            try: 
                
                info = ydl.extract_info(url = "ytsearch:%s" % item, download = False)['entries'][0]
            except Exception: 
                return False
            
        return {'source': info['url'], 'title': info['title']}
    
    def play_next(self): 
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, interaction: discord.Interaction):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            currentSong = self.music_queue[0][0]
            
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await interaction.followup.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url = f"ytsearch:{currentSong['title']}", download = False)['entries'][0]
                nowPlayingEmbed = discord.Embed(title= "Now Playing: " + currentSong['title'], color= 15548997)
                nowPlayingEmbed.set_thumbnail(url= info['thumbnail']) 
                nowPlayingEmbed.add_field(name = "Requested By", value = interaction.user.name, inline=True)
                nowPlayingEmbed.add_field(name = "Duration", value = time.strftime('%H:%M:%S', time.gmtime(info['duration'])), inline=True)
                await interaction.followup.send(embed = nowPlayingEmbed)
          
        else:
            self.is_playing = False

    async def play_command(self, interaction: discord.Interaction, youtube_url_or_title:str):         
        voice_channel = interaction.user.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await interaction.followup.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(youtube_url_or_title)
            if type(song) == type(True):
               
               await interaction.followup.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                
                await interaction.followup.send("``"+song["title"] + "``" + " added to the queue" + " at position " + "``" + str(len(self.music_queue)) + "``")
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music(interaction)
                    print("playing song")

    @app_commands.command(name = "play", description="plays a song on YouTube with the given URL or Title")
    @app_commands.describe(youtube_url_or_title = "What's the URL or title of the song you wish to play?")
    async def play(self, interaction: discord.Interaction, youtube_url_or_title:str): 
        await interaction.response.send_message("Playing Song...") 
        await self.play_command(interaction, youtube_url_or_title)
        
    @app_commands.command(name = "yts", description="searches for a song on YouTube with the given Title")
    @app_commands.describe(youtube_title = "What's the title of the song you wish to search?")
    async def ytsearch(self, interaction: discord.Interaction, youtube_title:str): 
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            await interaction.response.send_message("Searching for " + youtube_title + "...")
            videoResults = ydl.extract_info(f"ytsearch5:{youtube_title}", download=False)['entries']
        
            if len(videoResults) > 0 : 
                ytEmbed = discord.Embed(title= "Results For " + youtube_title, color= 15548997)
                ytEmbed.set_thumbnail(url="https://assets.stickpng.com/images/580b57fcd9996e24bc43c545.png")
                ytSearchResultView = View()
                for i in range(5) : 
                  ytEmbed.add_field(name = "Result " + str(i + 1), value = videoResults[i]['title'], inline=True)
                  ytEmbed.add_field(name = '\u200b', value = '\u200b', inline = False)

                  ytResultButtonLD = Button(label = str(i + 1), style = discord.ButtonStyle.grey, emoji="📻", row=1, custom_id= "ytResultButtonLD" + str(i+1))

                  async def ytResultButtonLD_callback(button_interaction): 
                    if(button_interaction.data['custom_id'] == "ytResultButtonLD1"):
                        print(videoResults[0]['original_url'])
                        await button_interaction.response.defer()  
                        await self.play_command(interaction, str(videoResults[0]['original_url']))          

                    elif(button_interaction.data['custom_id']  == "ytResultButtonLD2"):
                        print(videoResults[1]['original_url'])
                        await button_interaction.response.defer()
                       
                        await self.play_command(interaction, videoResults[1]['original_url'])
                        
                    elif(button_interaction.data['custom_id'] == "ytResultButtonLD3"):
                        print(videoResults[2]['original_url'])
                        await button_interaction.response.defer()
                        await self.play_command(interaction, videoResults[2]['original_url'])
                        
                    elif(button_interaction.data['custom_id'] == "ytResultButtonLD4"):
                        print(videoResults[3]['original_url'])
                        await button_interaction.response.defer()
                        await self.play_command(interaction, videoResults[3]['original_url'])                  
                    
                    elif(button_interaction.data['custom_id'] == "ytResultButtonLD5"):
                        print(videoResults[4]['original_url'])
                        await button_interaction.response.defer()
                        await self.play_command(interaction, videoResults[4]['original_url'])
                        
                  ytResultButtonLD.callback = ytResultButtonLD_callback
                  ytSearchResultView.add_item(ytResultButtonLD)

                await interaction.followup.send(embed = ytEmbed, view = ytSearchResultView)
            else :
                print("No Results Found!")

                   
    
    @app_commands.command(name = "pausesong", description="Pauses the song currently playing")
    async def pausesong(self, interaction: discord.Interaction): 
        if self.is_playing: 
            self.is_playing = False 
            self.is_paused = True 
            await interaction.response.send_message("Song has paused")
            self.vc.pause()

        elif self.is_paused:
            self.is_playing = True 
            self.is_paused = False
            await interaction.response.send_message("Song has resumed")
            self.vc.resume() 
            

    @app_commands.command(name = "resumesong", description="Resumes the song currently paused")
    async def resumesong(self, interaction: discord.Interaction): 
        if self.is_paused: 
            self.is_playing = True 
            self.is_paused = False
            await interaction.response.send_message("Song has resumed")
            self.vc.resume()
            
    
    @app_commands.command(name = "skip", description="Skips the song currently playing")
    async def skip(self, interaction: discord.Interaction): 
        if self.vc != None and self.vc: 
            await interaction.response.send_message("Skipped song")
            self.vc.stop()        
            await self.play_music(interaction)
            
    
    @app_commands.command(name = "queue", description="Shows the song queue")
    async def queue(self, interaction: discord.Interaction): 
        retval = ""
        for i in range(0, len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if (i > 5): break
            retval += self.music_queue[i][0]['title'] + "\n"
            print("test: " + retval)

        if retval != "":
            await interaction.response.send_message(retval)
        else:
            await interaction.response.send_message("No music in queue")
    
    @app_commands.command(name = "clear", description="Clears the song queue")
    async def clear(self, interaction: discord.Interaction):
       if self.vc != None and self.is_playing:
            self.vc.stop()
       self.music_queue = []
       await interaction.response.send_message("Music queue cleared")
    
    @app_commands.command(name = "leave", description="Media Bot leaves VC")
    async def leave(self, interaction: discord.Interaction):
        self.is_playing = False
        self.is_paused = False 
        await self.vc.disconnect()
        await interaction.response.send_message("Leaving VC")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
         # Ignore if change from voice channels not from bot
        if not member.id == self.bot.user.id:
            return
    
        # Ignore if change from voice channels was triggered by disconnect()
        elif before.channel is not None:
            return

        # Check if playing when in voice channel, every 180 seconds
        else:
            voice = after.channel.guild.voice_client
            while True:
                await asyncio.sleep(300)
            
                # If not playing, disconnect
                if voice.is_playing() == False:
                    print("disconnecting from vc!")
                    await voice.disconnect()
                    break

