import discord
import json
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

# List of commands here:
# ?create
# ?cdelete
# ?clist
# ?cupdate

class Custom(commands.Cog):

    '''Custom Commands~'''

    def __init__(self, bot):
        self.bot = bot

    # Creating custom commands
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def create(self, ctx, cmd, *, txt):
        
        '''Creates a custom command'''

        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        # Check if the custom command doesnt exist
        if f'?{cmd}' not in custom_commands.keys():
            # Create the new command
            custom_commands[f'?{cmd}'] = txt
            
            # Save the new command
            with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
                json.dump(custom_commands, out, indent = 4)

            embed = discord.Embed(description = 'Command created!', colour = discord.Colour.from_rgb(0, 255, 0))
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description = 'Command already exists!', colour = discord.Colour.from_rgb(255, 0, 0))
            await ctx.send(embed=embed)

    # Delete custom commands
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def cdelete(self, ctx, cmd):
        
        '''Deletes a custom command'''

        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        # Delete the custom command
        custom_commands.pop(f'?{cmd}', None)
        
        # Save the new list of commands
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
            json.dump(custom_commands, out, indent = 4)

        embed = discord.Embed(description = 'Command deleted!', colour = discord.Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        
    # Update custom command
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def cupdate(self, ctx, cmd, *, txt):

        '''Updates a custom command'''

        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        # Check if the custom command exists
        if f'?{cmd}' in custom_commands.keys():
            
            # Update the command 
            custom_commands[f'?{cmd}'] = txt
            
            # Save the updated command
            with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
                json.dump(custom_commands, out, indent = 4)

            embed = discord.Embed(description = 'Command updated!', colour = discord.Colour.random())
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description = 'Command does not exist!', colour = discord.Colour.random())
            await ctx.send(embed=embed)
    
    # List custom commands
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command()
    async def clist(self, ctx):

        '''List the custom commands'''
        
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        commands = list(custom_commands.keys())
        embed = discord.Embed(
            title = 'List of Custom Commands',
            description = '\n'.join(commands),
            colour = discord.Colour.random()
        )

        embed.set_footer(text=f"Total of {len(commands)} custom commands")

        await ctx.send(embed=embed)

    # Executing custom commands
    @commands.Cog.listener()
    async def on_message(self, message):
        
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)

        # Get the custom command
        cmd = message.content.split(' ')[0]
        
        if cmd in custom_commands.keys():
            await message.channel.send(custom_commands[cmd])
            
async def setup(bot):
    await bot.add_cog(Custom(bot))
