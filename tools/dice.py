import random
from discord.ext import commands


SW_DICE = {
    'blue': [
        (),
        (),
        ('success',),
        ('advantage',),
        ('advantage', 'advantage'),
        ('success', 'advantage')
    ],
    'green': [
        (),
        ('success',),
        ('success',),
        ('advantage',),
        ('advantage',),
        ('success', 'advantage'),
        ('advantage', 'advantage'),
        ('success', 'success')
    ],
    'yellow': [
        (),
        ('triumph',),
        ('success',),
        ('success',),
        ('advantage',),
        ('success', 'advantage'),
        ('success', 'advantage'),
        ('success', 'advantage'),
        ('success', 'success'),
        ('success', 'success'),
        ('advantage', 'advantage'),
        ('advantage', 'advantage')
    ],
    'black': [
        (),
        (),
        ('failure',),
        ('failure',),
        ('threat',),
        ('threat',)
    ],
    'purple': [
        (),
        ('failure',),
        ('threat',),
        ('threat',),
        ('threat',),
        ('failure', 'failure'),
        ('threat', 'failure'),
        ('threat', 'threat')
    ],
    'red': [
        (),
        ('despair',),
        ('failure',),
        ('failure',),
        ('threat',),
        ('threat',),
        ('failure', 'failure'),
        ('failure', 'failure'),
        ('threat', 'threat'),
        ('threat', 'threat'),
        ('threat', 'failure'),
        ('threat', 'failure')
    ],
    'white': [
        ('light side',),
        ('light side',),
        ('light side', 'light side'),
        ('light side', 'light side'),
        ('light side', 'light side'),
        ('dark side',),
        ('dark side',),
        ('dark side',),
        ('dark side',),
        ('dark side',),
        ('dark side',),
        ('dark side', 'dark side')
    ]
}

L5R_DICE = {
    'black': [
        ('opportunity', 'strife'),
        ('success',),
        (),
        ('opportunity',),
        ('explosive success', 'strife'),
        ('success', 'strife')
    ],
    'white': [
        ('strife',),
        ('success',),
        ('success', 'strife'),
        ('opportunity',),
        ('strife', 'success'),
        (),
        ('success',),
        ('explosive success',),
        ('opportunity',),
        (),
        ('explosive success', 'strife'),
        ('success', 'opportunity')
    ]
}


def resolve_sw(results):
    resolution = {
        'successes': 0,
        'triumphs': 0,
        'despairs': 0,
        'advantages': 0,
        'light side': 0,
        'dark side':0
    }
    for result in results:
        if result == 'success':
            resolution['successes'] += 1
        elif result == 'advantage':
            resolution['advantages'] += 1
        elif result == 'triumph':
            resolution['successes'] += 1
            resolution['triumphs'] += 1
        elif result == 'failure':
            resolution['successes'] -= 1
        elif result == 'threat':
            resolution['advantages'] -= 1
        elif result == 'despair':
            resolution['successes'] -= 1
            resolution['despairs'] += 1
        elif result == 'light side':
            resolution['light side'] += 1
        elif result == 'dark side':
            resolution['dark side'] += 1
    if resolution['successes'] < 0:
        resolution['failures'] = resolution['successes'] * -1
        del resolution['successes']
    if resolution['advantages'] < 0:
        resolution['threats'] = resolution['advantages'] * -1
        del resolution['advantages']
    return resolution


def roll_many(roll, all_dice):
    results = []
    for die in roll:
        if die not in all_dice:
            raise ValueError(f'No such die: `{die}`.')
        for _ in range(roll[die]):
            results.extend(list(random.choice(all_dice[die])))
    return results


def resolve_l5r(results):
    counts = {}
    for result in results:
        if result in counts:
            counts[result] += 1
        else:
            counts[result] = 1
    return counts


def display_counts(counts):
    lines = []
    for name in counts:
        value = counts[name]
        lines.append(f'**{name}:** `{value}`')
    return '\n'.join(lines)


def dice_args(raw):
    values = {}
    see_help = ' For more, see the help command.'
    for item in raw.split(','):
        parts = item.strip().split(' ')
        if len(parts) != 2:
            raise commands.CommandError(
                f'Invalid dice specifier `{item}`.{see_help}'
            )
        raw_num, colour = parts
        try:
            number = int(raw_num)
        except ValueError:
            raise commands.CommandError(
                f'`{raw_num}` is not a number!{see_help}'
            )
        if number < 1:
            raise commands.CommandError(
                f'You can\'t roll `{number}` dice! Choose a number more than 0.'
                + see_help
            )
        if colour in values:
            raise commands.CommandError(
                f'You specified the `{colour}` die twice.{see_help}'
            )
        values[colour] = number
    return values


async def roll_sw(ctx, dice):
    """Roll Star Wars FFG dice, return the resolved result."""
    await ctx.send(display_counts(resolve_sw(roll_many(dice, SW_DICE))))


async def roll_l5r(ctx, dice):
    """Roll Legend of the Five Rings dice."""
    await ctx.send(display_counts(resolve_l5r(roll_many(dice, L5R_DICE))))

