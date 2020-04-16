async def imitate(ctx, user, message):
    whs = await ctx.channel.webhooks()
    if whs:
        wh = whs[0]
    else:
        wh = await ctx.channel.create_webhook(name='Toolkit')
    await wh.send(
        message, username=user.display_name, avatar_url=str(user.avatar_url)
    )
    await ctx.message.delete()