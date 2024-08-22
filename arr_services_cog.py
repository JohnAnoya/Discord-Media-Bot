import discord 
import win32serviceutil
import os

from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View #pip install -U git+https://github.com/Pycord-Development/pycord
from py1337x import py1337x #pip install 1337x (https://github.com/hemantapkh/1337x)
from qbittorrentapi import Client  #pip install qbittorrent-api (https://qbittorrent-api.readthedocs.io/en/latest/)
from arrapi import SonarrAPI, RadarrAPI

async def setup(bot): 
    await bot.add_cog(arr_services_cog(bot))

torrents = py1337x()
qBitClient = Client()

sonarr = SonarrAPI(os.environ.get('SONARR_URL'), os.environ.get('SONARR_API_KEY'))
radarr = RadarrAPI(os.environ.get('RADARR_URL'), os.environ.get("RADARR_API_KEY"))

#Login credentials for QBitTorrent WebUI
connection_info = dict(
    host = "localhost:8080/", 
    username = os.environ.get('QBIT_USERNAME'), 
    password = os.environ.get('QBIT_PASSWORD')
)

class arr_services_cog(commands.Cog): 
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(name = "mediahelp", description="bot commands for downloading media onto the jellyfin server")
    async def media_help(self, interaction: discord.Interaction): 
       help_embed = discord.Embed(title= "💭 Media Command List", color= 9936031)
       help_embed.add_field(name = "/search  Title | Media Type", value = "search for media with the given title", inline=False)
       help_embed.add_field(name = "/listlibrary Media Type", value = "Lists all shows or movies series ID", inline=False)
       help_embed.add_field(name = "/deletefromlibrary Media Type | Series ID", value = "Delete a show or movie with the given Series ID [use /listlibrary]", inline=False)
       help_embed.add_field(name = "/displaydownload Hash ID", value = "show a specific torrent using the hash id", inline=False)
       help_embed.add_field(name = "/displayalldownloads", value = "shows all torrents currently being downloaded", inline=False)
       help_embed.add_field(name = "/pause Hash ID", value = "pause a specific torrent using the hash id", inline=False)
       help_embed.add_field(name = "/pauseall", value = "pauses all torrents currently being downloaded", inline=False)
       help_embed.add_field(name = "/resume Hash ID", value = "resume a specific torrent using the hash id", inline=False)
       help_embed.add_field(name = "/resumeall", value = "resume all torrents currently being downloaded", inline=False)
       help_embed.add_field(name = "/deletedownload Hash ID", value = "delete a specific torrent using the hash id", inline=False)
       help_embed.add_field(name = "/deletealldownloads", value = "delete all torrents currently being downloaded", inline=False)
    
       await interaction.response.send_message(embed = help_embed)
    
    @app_commands.command(name = "ythelp", description="bot commands for playing YouTube music")
    async def yt_help(self, interaction: discord.Interaction): 
       help_embed = discord.Embed(title= "💭 YouTube Command List", color= 15548997)
       help_embed.add_field(name = "/yts Title", value = "search for youtube video with the given title", inline=False)
       help_embed.add_field(name = "/play Title or URL", value = "play a YouTube video with the given title or URL", inline=False)
       help_embed.add_field(name = "/queue", value = "shows all songs currently in the queue", inline=False)
       help_embed.add_field(name = "/pausesong", value = "pauses song that is currently playing", inline=False)
       help_embed.add_field(name = "/resumesong", value = "resumes song that is currently playing", inline=False)
       help_embed.add_field(name = "/skip", value = "skips song that is currently playing", inline=False)
       help_embed.add_field(name = "/clear", value = "clears the entire queue", inline=False)
       help_embed.add_field(name = "/leave", value = "leaves VC", inline=False)
    
       await interaction.response.send_message(embed = help_embed)
    
    @app_commands.command(name = "jellyfin", description="info for jellyfin (URL + login credentials)")
    async def jellyfin(self, interaction: discord.Interaction): 
       help_embed = discord.Embed(title= "💭 Jellyfin Info", color= 10181046)
       help_embed.add_field(name = "URL'", value = os.environ.get('JELLYFIN_URL'), inline=False)
       help_embed.add_field(name = "username", value = os.environ.get('JELLYFIN_SHARED_ACCOUNT_USER'), inline=False)
       help_embed.add_field(name = "password", value = os.environ.get('JELLYFIN_SHARED_ACCOUNT_PASS'), inline=False)
    
       await interaction.response.send_message(embed = help_embed)
    
    async def radarr_organization(interaction: discord.Interaction, media_name:str): 
       try: 
          if radarr.get_movie(radarr.search_movies(media_name)[0].id) is not None: 
             print("This Series Exists! " + "Name: " + radarr.search_movies(media_name)[0].title)
       except: 
          await interaction.channel.send("Series not found on Radarr (Movie Auto Organizer), looking up potential movies you are trying to download...")
          search_result = radarr.search_movies(media_name)
          search_count = len(search_result)
          search_count = min(5, search_count)
    
          if(search_count > 0): 
            organizer_embed = discord.Embed(title= "(Radarr) Auto Organizer: Please choose the correct movie", color= 12745742)
            embed_view = View()
    
            for i in range(search_count): 
              organizer_embed.add_field(name = "Result " + str(i + 1), value = search_result[i].title + " (" + str(search_result[i].year) + ")", inline=False)
              
              download_button = Button(label = str(i + 1), style = discord.ButtonStyle.grey, emoji="📺", row=1, custom_id= "organizeButtonLD" + str(i+1))
    
              #In order to determine when a button is being pressed I'm using callback functions
              async def button_callback(interaction): 
                if(interaction.data['custom_id'] == "organizeButtonLD1"): 
                  await interaction.response.defer()
                  await interaction.followup.send("Created movie folder for Result 1, Radarr will begin to download the series shortly!")
                  radarr.add_movie(movie_id=radarr.search_movies(media_name)[0].id, tmdb_id=radarr.search_movies(media_name)[0].tmdbId,  quality_profile="Any", root_folder="E:\Movies")
                   
                elif(interaction.data['custom_id'] == "organizeButtonLD2"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created movie folder for Result 2, Radarr will begin to download the series shortly!")
                  radarr.add_movie(movie_id=radarr.search_movies(media_name)[1].id, tmdb_id=radarr.search_movies(media_name)[1].tmdbId,  quality_profile="Any", root_folder="E:\Movies")
                 
                elif(interaction.data['custom_id'] == "organizeButtonLD3"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created movie folder for Result 3, Radarr will begin to download the series shortly!")
                  radarr.add_movie(movie_id=radarr.search_movies(media_name)[2].id, tmdb_id=radarr.search_movies(media_name)[2].tmdbId,  quality_profile="Any", root_folder="E:\Movies")
                 
                elif(interaction.data['custom_id'] == "organizeButtonLD4"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created movie folder for Result 4, Radarr will begin to download the series shortly!")
                  radarr.add_movie(movie_id=radarr.search_movies(media_name)[3].id, tmdb_id=radarr.search_movies(media_name)[3].tmdbId,  quality_profile="Any", root_folder="E:\Movies")
                  
                elif(interaction.data['custom_id'] == "organizeButtonLD5"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created movie folder for Result 5, Radarr will begin to download the series shortly!")
                  radarr.add_movie(movie_id=radarr.search_movies(media_name)[4].id, tmdb_id=radarr.search_movies(media_name)[4].tmdbId,  quality_profile="Any", root_folder="E:\Movies")
    
              download_button.callback = button_callback
              embed_view.add_item(download_button)
    
            await interaction.followup.send(embed = organizer_embed, view = embed_view) 
    
    async def sonarr_organization(interaction: discord.Interaction, media_name:str): 
        try: 
          if sonarr.get_series(sonarr.search_series(media_name)[0].id) is not None:
             print("This Series Exists! " + "Name: " + sonarr.search_series(media_name)[0].title)
    
        except:
          await interaction.channel.send("Series not found on Sonarr (Series Auto Organizer), looking up potential series you are trying to download...")
          
          world_filter_list = ['season', 'episode']
    
          new_series_title = str(media_name).lower()
          for word in world_filter_list:
            new_series_title = new_series_title.replace(word, "")
    
          search_result = sonarr.search_series(new_series_title)
          search_count = len(search_result)
          search_count = min(5, search_count)
    
          if(search_count > 0):
            organizer_embed = discord.Embed(title= "(Sonarr) Auto Organizer: Please choose the correct series", color= 8359053)
            organizer_embed.set_footer(text="(If none of these series are correct please search again including the year)", icon_url="https://www.pngmart.com/files/15/Red-Exclamation-Mark-Transparent-Background.png")
            search_result_view = View()
    
            for i in range (search_count):
              organizer_embed.add_field(name = "Result " + str(i + 1), value = search_result[i].title, inline=True)
              organizer_embed.add_field(name = "Seasons", value = len(search_result[i].seasons), inline=True)
              organizer_embed.add_field(name = "Year", value = search_result[i].year, inline=True)
           
              download_button = Button(label = str(i + 1), style = discord.ButtonStyle.grey, emoji="📺", row=1, custom_id= "organizeButtonLD" + str(i+1))
    
              #In order to determine when a button is being pressed I'm using callback functions
              async def button_callback(interaction): 
                if(interaction.data['custom_id'] == "organizeButtonLD1"): 
                  await interaction.response.defer()
                  await interaction.followup.send("Created series folder for Result 1, Sonarr will begin to download the series shortly!")
                  sonarr.add_series(series_id=sonarr.search_series(new_series_title)[0].id, tvdb_id=sonarr.search_series(new_series_title)[0].tvdbId, language_profile="English", quality_profile="Any", root_folder="E:\Shows")
                   
                elif(interaction.data['custom_id'] == "organizeButtonLD2"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created series folder for Result 2, Sonarr will begin to download the series shortly!")
                  sonarr.add_series(series_id=sonarr.search_series(new_series_title)[1].id, tvdb_id=sonarr.search_series(new_series_title)[1].tvdbId, language_profile="English", quality_profile="Any", root_folder="E:\Shows")
                 
                elif(interaction.data['custom_id'] == "organizeButtonLD3"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created series folder for Result 3, Sonarr will begin to download the series shortly!")
                  sonarr.add_series(series_id=sonarr.search_series(new_series_title)[2].id, tvdb_id=sonarr.search_series(new_series_title)[2].tvdbId, language_profile="English", quality_profile="Any", root_folder="E:\Shows")
                 
                elif(interaction.data['custom_id'] == "organizeButtonLD4"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created series folder for Result 4, Sonarr will begin to download the series shortly!")
                  sonarr.add_series(series_id=sonarr.search_series(new_series_title)[3].id, tvdb_id=sonarr.search_series(new_series_title)[3].tvdbId, language_profile="English", quality_profile="Any", root_folder="E:\Shows")
                  
                elif(interaction.data['custom_id'] == "organizeButtonLD5"):
                  await interaction.response.defer()
                  await interaction.followup.send("Created series folder for Result 5, Sonarr will begin to download the series shortly!")
                  sonarr.add_series(series_id=sonarr.search_series(new_series_title)[4].id, tvdb_id=sonarr.search_series(new_series_title)[4].tvdbId, language_profile="English", quality_profile="Any", root_folder="E:\Shows")
    
              download_button.callback = button_callback
              search_result_view.add_item(download_button)
    
            await interaction.followup.send(embed = organizer_embed, view = search_result_view) 
    
    @app_commands.command(name = "search", description="search for media (movies, tv, anime)")
    @app_commands.describe(media_name = "What Movie, TV Show or Anime should I search for?", 
                           media_type = "What type of media is this?")
    @app_commands.choices(media_type = [
       discord.app_commands.Choice(name = "Movie", value = "movies"),
       discord.app_commands.Choice(name = "TV Show", value = "tv"),
       discord.app_commands.Choice(name = "Anime", value = "anime")
    ])
    async def search(self, interaction: discord.Interaction, media_name:str, media_type: discord.app_commands.Choice[str]): 
       await interaction.response.defer()
       await interaction.followup.send("Searching for " + media_name + "...")
    
       if media_type.value == "tv" or media_type.value == "anime" : 
          await arr_services_cog.sonarr_organization(interaction, media_name)
          return
    
       elif media_type.value == "movies": 
          await arr_services_cog.radarr_organization(interaction, media_name)
          return
    
    @app_commands.command(name = "displaydownload", description="show torrent currently downloading (using a Hash ID)")
    @app_commands.describe(hash_id = "What is the hash ID of the torrent?")
    async def display_download(self, interaction: discord.Interaction, hash_id:str):
      showEmbed = discord.Embed(title= "Showing Torrent", color= 9936031)
    
      with Client(**connection_info) as qbt_client:
          for torrent in qbt_client.torrents.info():
            if (torrent.hash[-6:] == hash_id):
              showEmbed.add_field(name = "(HASH: " + str(torrent.hash[-6:]) + ")" + " NAME: " + str(torrent.name), value =  "PROGRESS: " + str(round(torrent.progress * 100.0, 2)) + "% (" + str(torrent.state) + ")", inline = False)
              await interaction.response.send_message(embed = showEmbed)
    
    @app_commands.command(name = "displayalldownloads", description="show all torrents currently downloading")
    async def display_all_downloads(self, interaction: discord.Interaction):
      show_all_embed = discord.Embed(title= "Showing All Torrents", color= 9936031)
      await interaction.response.send_message("Scanning for currently downloading torrents...")
      with Client(**connection_info) as qbt_client:
        for torrent in qbt_client.torrents.info():
          print(f"{torrent.hash[-6:]}: {torrent.name} ({torrent.state})")
        
          show_all_embed.add_field(name = "(HASH: " + str(torrent.hash[-6:]) + ")" + " NAME: " + str(torrent.name), value =  "PROGRESS: " + str(round(torrent.progress * 100.0, 2)) + "% ("  + str(torrent.state) + ")", inline = False)
    
      await interaction.followup.send(embed = show_all_embed) 
    
    @app_commands.command(name = "listlibrary", description="Lists all media library shows/movies and their series ID")
    @app_commands.describe( media_type = "Which type of media? (movies or shows)")
    @app_commands.choices(media_type = [
       discord.app_commands.Choice(name = "Movies", value = "movie"),
       discord.app_commands.Choice(name = "TV Shows/Anime", value = "show")
    ])
    async def list_library(self, interaction: discord.Interaction, media_type: discord.app_commands.Choice[str]): 
      list_library_embed = discord.Embed(title= "", description="", color= 9936031)
      match media_type.value :
          case "movie" :
            list_of_movies = radarr.all_movies()
            list_library_embed.title = "All Movies Within Library"
            await interaction.response.defer()
    
            for movie in list_of_movies: 
               list_library_embed.description = list_library_embed.description + movie._name + " (Series ID: " + str(movie.id) + ")\n"
    
            await interaction.followup.send(embed = list_library_embed)
            
          case "show": 
            listOfShows = sonarr.all_series()
            list_library_embed.title = "All Shows Within Library"
            await interaction.response.defer()
    
            for show in listOfShows: 
               list_library_embed.description = list_library_embed.description + show._name + " (Series ID: "  + str(show.id) + ")\n"
           
            await interaction.followup.send(embed = list_library_embed)    
    
    @app_commands.command(name = "deletefromlibrary", description="Delete a show or movie from the library (using the series ID)")
    @app_commands.describe( media_type = "Which type of media would you like to remove from the library? (Show or Movie)")
    @app_commands.choices(media_type = [
       discord.app_commands.Choice(name = "Movies", value = "movie"),
       discord.app_commands.Choice(name = "TV Shows/Anime", value = "show")
    ])
    async def delete_from_library(self, interaction: discord.Interaction, media_type: discord.app_commands.Choice[str], series_id: str):   
        OmbiDB = os.environ.get('OMBI_DB')
        match media_type.value :
          case "movie" : 
            await interaction.response.defer()
    
            movie_name = radarr.get_movie(series_id)._name
            radarr.delete_movie(series_id, deleteFiles=True)
    
            win32serviceutil.StopServiceWithDeps("ombi", waitSecs=5)
    
            try: 
              os.remove(OmbiDB)
              print("Deleted Movie")
            except OSError: 
              pass
        
            win32serviceutil.StartService("ombi")
    
            await interaction.followup.send("Successfully removed " + movie_name + " from the library! (This may take a few mins to sync with Jellyfin)")
            
          case "show" : 
            await interaction.response.defer()
    
            show_name = sonarr.get_series(series_id)._name
            sonarr.delete_series(series_id, deleteFiles=True)
    
            win32serviceutil.StopServiceWithDeps("ombi", waitSecs=5)
            
            try: 
              os.remove(OmbiDB)
              print("Deleted Show")
            except OSError: 
              pass
        
            win32serviceutil.StartService("ombi")
    
            await interaction.followup.send("Successfully removed " + show_name + " from the library! (This may take a few mins to sync with Jellyfin)")
               
    @app_commands.command(name = "pause", description="pause torrent currently downloading (using a Hash ID)")
    @app_commands.describe(hash_id = "What is the hash ID of the torrent?")
    async def pause(self, interaction: discord.Interaction, hash_id:str):
      pause_embed = discord.Embed(title= "⏸ Paused Torrent", color= 9936031)
      with Client(**connection_info) as qbt_client:
          for torrent in qbt_client.torrents.info():
            if (torrent.hash[-6:] == hash_id):
              qbt_client.torrents.pause(torrent.hash)
              pause_embed.add_field(name = "Torrent (" + torrent.hash[-6:] + ")", value = "download has been paused", inline=False)
              await interaction.response.send_message(embed = pause_embed)
    
    @app_commands.command(name = "pauseall", description="pause all torrents currently downloading")
    async def pause_all(self, interaction: discord.Interaction):
      pause_embed = discord.Embed(title= "⏸ All Torrents Paused", color= 9936031)
      with Client(**connection_info) as qbt_client:
        qbt_client.torrents.pause.all()
        pause_embed.add_field(name = "All Torrents", value="all downloads have been paused", inline = False)
        await interaction.response.send_message(embed = pause_embed)
    
    @app_commands.command(name = "resume", description="resume torrent currently downloading (using a Hash ID)")
    @app_commands.describe(hash_id = "What is the hash ID of the torrent?") 
    async def resume(self, interaction: discord.Interaction, hash_id:str):
      resume_embed = discord.Embed(title= "⏯ Resume Torrent ", color= 9936031)
      with Client(**connection_info) as qbt_client:
          for torrent in qbt_client.torrents.info():
            if (torrent.hash[-6:] == hash_id):
              qbt_client.torrents.resume(torrent.hash)
              resume_embed.add_field(name = "Torrent (" + torrent.hash[-6:] + ")", value = "download has been resumed", inline=False)
              await interaction.response.send_message(embed = resume_embed)
    
    @app_commands.command(name = "resumeall", description="resume all torrents currently downloading")
    async def resume_all(self, interaction: discord.Interaction):
      resume_embed = discord.Embed(title= "⏯ All Torrents Resumed", color= 9936031)
      with Client(**connection_info) as qbt_client:
        qbt_client.torrents.resume.all()
        resume_embed.add_field(name = "All Torrents", value="all downloads have been resumed", inline = False)
        await interaction.response.send_message(embed=resume_embed)
    
    @app_commands.command(name = "deletedownload", description="delete torrent currently downloading (using a Hash ID)")
    @app_commands.describe(hash_id = "What is the hash ID of the torrent?") 
    async def delete_download(self, interaction: discord.Interaction, hash_id:str):
      delete_embed = discord.Embed(title= "❌ Deleted Torrent", color= 15548997)
      with Client(**connection_info) as qbt_client:
          for torrent in qbt_client.torrents.info():
            if (torrent.hash[-6:] == hash_id):
              qbt_client.torrents.delete(torrent.hash)
              delete_embed.add_field(name = "Torrent (" + torrent.hash[-6:] + ")", value = "download has been deleted", inline=False)
              await interaction.response.send_message(embed = delete_embed)
    
    @app_commands.command(name = "deletealldownloads", description="delete all torrents currently downloading")
    async def delete_all_downloads(self, interaction: discord.Interaction):
      delete_embed = discord.Embed(title= "❌ All Torrents Deleted", color= 15548997)
      with Client(**connection_info) as qbt_client:
        qbt_client.torrents.delete.all()
        delete_embed.add_field(name = "All Torrents", value="all downloads have been deleted", inline = False)
        await interaction.response.send_message(embed = delete_embed)