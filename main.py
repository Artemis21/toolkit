from discord.ext import commands
import discord
import typing
import logging
import re
import traceback

from tools import eyedropper
from tools import countdown as ctd_main
from tools import imitate
from tools import dice


class Help(commands.DefaultHelpCommand):
    brief = 'Shows this message.'
    help = 'Provides help on a command.'

    async def send_bot_help(self, cogs):
        lines = []
        for cog in cogs:
            for command in cogs[cog]:
                if command.hidden:
                    continue
                line ='**{}** *{}*'.format(
                    self.get_command_signature(command),
                    command.brief or Help.brief
                )
                if line not in lines:     # known bug where commands with
                    lines.append(line)    # aliases are duplicated
        text = '\n'.join(lines)
        e = discord.Embed(title='Help', color=0x00FF66, description=text)
        await self.get_destination().send(embed=e)

    async def send_command_help(self, command):
        desc = (command.help or Help.help).replace(
            '{{pre}}', bot.command_prefix
        )
        title = self.get_command_signature(command)
        e = discord.Embed(title=title, color=0x00FF66, description=desc)
        await self.get_destination().send(embed=e)

    async def send_cog_help(self, cog):
        await self.send_bot_help(bot.cogs)


logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix='--')
bot.help_command = Help()
TOKEN = 'Njk5Mzg0NzQ2NzI3MTc4MjQ1.XpTo2g._eKyv8WVg1iK2wfJXlusclmX5dU'
DESC = (
    'Toolkit is a collection of simple tools for Discord made by Artemis#8799.'
)
INVITE = (
    'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=8'
    '&scope=bot'
)
ADVERT = 'Order a bot at artybot.xyz.'
AD_ICON = 'https://artybot.xyz/static/icon.png'


@bot.event
async def on_ready():
    await ctd_main.on_ready(bot)


@bot.event
async def on_command_error(ctx, error):
    rawtitle = type(error).__name__
    rawtitle = re.sub('([a-z])([A-Z])', r'\1 \2', rawtitle)
    title = rawtitle[0].upper() + rawtitle[1:].lower()
    e = discord.Embed(color=0xFF0066, title=title, description=str(error))
    await ctx.send(embed=e)
    if hasattr(error, 'original'):
        err = error.original
        traceback.print_tb(err.__traceback__)
        print(f'{type(err).__name__}: {err}.')


@bot.command(brief='About the bot.')
async def about(ctx):
    '''Provides some details relating to the bot.
    '''
    e = discord.Embed(colour=0x0066FF, title='About', description=DESC)
    e.set_thumbnail(url=bot.user.avatar_url)
    e.add_field(name='Guilds', value=len(bot.guilds))
    e.add_field(
        name='Invite',
        value=f'**[Click Here]({INVITE.format(bot.user.id)})**'
    )
    e.add_field(
        name='Discord API ping', value=f'{str(bot.latency * 1000)[:3]}ms'
    )
    e.set_footer(text=ADVERT, icon_url=AD_ICON)
    await ctx.send(embed=e)


@bot.command(brief='Get colors from an image.', aliases=['p'])
async def pick(ctx, url_or_user: typing.Union[discord.Member, str]=None):
    """
    Find the colors present in an image. Either upload an attachment or
    send a link or mention a user for their avatar. If you do none of these,
    the bot will use your avatar.

    Short name: `p`

    Examples:
    `{{pre}}pick https://example.com/image.png`
    `{{pre}}p` (with image attachted)
    `{{pre}}p @Artemis`
    `{{pre}}pick`
    """
    await eyedropper.main(ctx, url_or_user)


@bot.command(brief='Start a countdown.', aliases=['c'])
async def countdown(ctx, *, time: ctd_main.time_conv):
    """
    Start a countdown. Time should be specified in `m`inutes, `h`ours, `d`ays and `M`onths.

    Short name: `c`

    Examples:
    `{{pre}}countdown 1M 14d`
    `{{pre}}c 12h`
    """
    await ctd_main.main(ctx, time)


@bot.command(brief='Imitate someone.', aliases=['s'])
@commands.guild_only()
async def sudo(ctx, user: discord.Member, *, message):
    """Send a message that looks like it's from someone else.

    Short name: `s`

    Examples:
    `{{pre}}sudo @Artemis My name isn't Artemis.`
    `{{pre}}s @Someone Light theme is good.`
    """
    await imitate.imitate(ctx, user, message)


@bot.command(brief='Roll Star Wars dice.', aliases=['sw'])
async def starwars(ctx, *, all_dice: dice.dice_args):
    """Roll some Star Wars Fantasy Flight Gaming dice.

    Short name: `sw`

    Examples:
    `{{pre}}starwars 10 red, 5 black`
    `{{pre}}sw 1 green, 3 white, 2 black`
    """
    await dice.roll_sw(ctx, all_dice)


@bot.command(brief='Roll L5R dice.', aliases=['l5r'])
async def fiverings(ctx, *, all_dice: dice.dice_args):
    """Roll some Legend of the Five Rings dice.

    Short name: `l5r`

    Examples:
    `{{pre}}fiverings 2 black`
    `{{pre}}l5r 10 white, 3 black`
    """
    await dice.roll_l5r(ctx, all_dice)


@bot.command(brief='See the guilds.', hidden=True)
@commands.is_owner()
async def snoop(ctx):
    """See servers with their counts and invites."""
    rows = []
    for i in bot.guilds:
        line = f'{i.name} | {len(i.members)}'
        try:
            invs = await i.invites()
            line = invs[0].url
        except Exception:
            pass
        rows.append(line)
    await ctx.send('\n'.join(rows))


bot.run(TOKEN)