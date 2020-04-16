import io
import aiohttp
import math
import discord
from sklearn import metrics, cluster
from numpy import asarray
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


session = aiohttp.ClientSession()


def pixels(im):
    width, height = im.size
    for x in range(width):
        for y in range(height):
            yield im.getpixel((x, y))


def format_col(rgb):
    r, g, b = map(int, rgb)
    base = f'{r:02x}{g:02x}{b:02x}'
    code = '#' + base
    return code, (r, g, b)


def find_cols(im):
    pxs = asarray(list(pixels(im.convert('RGB'))))
    best_score = -1
    best_clt = 0
    for clusters in range(2, 10):
        clt = cluster.KMeans(n_clusters=clusters, n_init=1)
        clt.fit(pxs)
        score = metrics.silhouette_score(
            pxs, clt.labels_, metric='euclidean', sample_size=100
        )
        if score > best_score:
            best_score = score
            best_clt = clt
    return list(map(format_col, best_clt.cluster_centers_.tolist()))


def transform_channel(value):
    if value < 10:
        return value / 3294
    return (value/269 + 0.0513) ** 2.4


def contrast_col(rgb):
    rg, gg, bg = map(transform_channel, rgb)
    lum = 0.2126*rg + 0.7152*gg + 0.0722*bg
    if lum < 0.5:
        return (255, 255, 255)
    return (0, 0, 0)


def draw_cols(cols, bytes_io, scale=30):
    width = min((len(cols), 3))
    height = math.ceil(len(cols) / width)
    im = Image.new('RGBA', (width*scale*4, height*scale), color=(255,)*4)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 
        size=scale//2
    )
    for index, col in enumerate(cols):
        code, rgb = col
        inverse = [*contrast_col(rgb)]
        inverse.append(255)
        inverse = tuple(inverse)
        rgb = [*rgb]
        rgb.append(255)
        rgb = tuple(rgb)
        x = index % width
        y = index // width
        w, h = draw.textsize(code, font=font)
        draw.rectangle(
            [x*scale*4, y*scale, (x+1)*scale*4, (y+1)*scale], rgb, rgb
        )
        draw.text(
            [x*scale*4 + w/2, y*scale + h/2], 
            code, inverse, font=font
        )
    im.save(bytes_io, format='PNG')
    bytes_io.seek(0)


async def download(url, bytesio):
    async with session.get(url) as res:
        if res.status == 200:
            bytesio.write(await res.read())
            bytesio.seek(0)
            return 0
        else:
            return 1


async def main(ctx, url_or_user):
    data = io.BytesIO()
    if ctx.message.attachments:
        await ctx.message.attachments[0].save(data)
    elif url_or_user:
        if isinstance(url_or_user, discord.Member):
            url = str(url_or_user.avatar_url)
        else:
            url = url_or_user
        status = await download(url, data)
        if status:
            return await ctx.send('Error downloading image.')
    else:
        url = str(ctx.author.avatar_url)
        status = await download(url, data)
        if status:
            return await ctx.send('Error downloading image.')
    try:
        im = Image.open(data)
    except UnidentifiedImageError:
        return await ctx.send('That doesn\'t look like an image.')
    cols = find_cols(im)
    out = io.BytesIO()
    draw_cols(cols, out)
    f = discord.File(out, filename='colours.png')
    e = discord.Embed(description='```' + ' '.join(i[0] for i in cols) + '```')
    e.set_image(url='attachment://colours.png')
    await ctx.send(embed=e, file=f)
