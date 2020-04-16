import discord
from discord.ext import commands, tasks
from datetime import timedelta, datetime
import sqlite3


connection = None
bot = None


def pretty_td(td):
    seconds = int(td.total_seconds())
    periods = {
        'month': 60*60*24*30,
        'day': 60*60*24,
        'hour': 60*60,
        'minute': 60,
    }
    parts = []
    for period in periods:
        if seconds >= periods[period]:
            num, seconds = divmod(seconds, periods[period])
            part = f'{num} {period}'
            if num != 1:
                part += 's'
            parts.append(part)
    if not parts:
        return 'less than a minute'
    elif len(parts) == 1:
        return parts[0]
    else:
        return ', '.join(parts[:-1]) + ' and ' + parts[-1]


def time_conv(raw):
    parts = raw.split(' ')
    time = {}
    periods = {
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'M': 'months'
    }
    for part in parts:
        if not part:
            continue
        name = part[-1]
        if name not in periods:
            raise commands.CommandError(
                f'`{name}` is not a recognised time period.'
            )
        period = periods[name]
        if period in time:
            raise commands.CommandError(
                f'Value for `{period}` specified twice.'
            )
        main = part[:-1]
        if not main:
            raise commands.CommandError(
                f'No value given for `{period}` even though it\'s specified.'
            )
        try:
            num = int(main)
        except ValueError:
            raise commands.CommandError(
                f'Invalid value for `{period}`: `{main}`.'
            )
        if num < 1:
            raise commands.CommandError(
                f'Values should not be less than one.'
            )
        time[period] = num
    if not time:
        raise commands.CommandError('No time values specified.')
    return timedelta(**time)


def execute(query, *params):
    cursor = connection.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    connection.commit()
    return rows


def add_timer(time, message):
    end = datetime.now() + time
    channel = message.channel.id
    message = message.id
    execute(
        'INSERT INTO timers (end, channel, message) VALUES (?, ?, ?);',
        end, channel, message
    )


async def get_timers():
    rows = execute(
        'SELECT end AS "[timestamp]", channel, message FROM timers;'
    )
    for row in rows:
        if row[0] < datetime.now():
            execute('DELETE FROM timers WHERE message=?;', row[2])
        channel = bot.get_channel(row[1])
        if not channel:
            continue
        message = await channel.fetch_message(row[2])
        if not message:
            continue
        yield row[0], message


async def on_ready(bot_):
    global connection, bot
    bot = bot_
    connection = sqlite3.connect(
        'db.sqlite3', 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
    )
    execute('''
        CREATE TABLE IF NOT EXISTS timers (
            end TIMESTAMP, channel INTEGER, message INTEGER
        );
    ''')
    update_all.start()
    print('Ready!')


@tasks.loop(minutes=1)
async def update_all():
    async for end, message in get_timers():
        if end < datetime.now():
            time_left = '**Time up!**'
        else:
            time = end - datetime.now()
            time_left = f'**{pretty_td(time)} remaining.**'
        e = discord.Embed(
            title='Timer', description=time_left, colour=0x7289DA,
            timestamp=end
        )
        e.set_footer(text='Ends at ')
        await message.edit(embed=e, content=None)


async def main(ctx, time):
    message = await ctx.send('*One moment please...*')
    add_timer(time, message)
    update_all.restart()