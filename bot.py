import discord
from creds import *
from discord.ext import commands
from sheet_transformer import SheetTransformer

client = commands.Bot(command_prefix='.', help_command=None)

@client.event
async def on_ready():
    print(f'SparkIEEE has logged in as {client.user}')

@client.command()
async def help(ctx):
    msg = 'Hello! I am **SparkIEEE**, an IEEE Discord bot created by Bryan Wong. \n' \
          'I can assist you with checking off project completion and more!\n\n' \
          f'**Commands:** \n' \
          f'To run a command, type in `{client.command_prefix}[command]`.\n' \
          f'For fields with multiple words (e.g. names), use quotation marks `""`\n' \
          '```projects             directory of current active projects\n' \
          'project p            lookup project deadlines, contact info, links, and more\n' \
          'status p u           lookup project completion status of member u in project p```\n' \
          '**Project Lead Commands:**\n' \
          '```checkoff p a u [v]   checkoff user u for project p, assignment a\n' \
          '                     v is the new value, by default it\'s "x"\n' \
          f'                     to add notes, {client.command_prefix}checkoff p a u "checkpoint 1"\n' \
          '```**Links:**\n'

    # todo: add image urls/descriptions
    ieee_website = discord.Embed(title='IEEE at UCLA Website',
                              url='https://ieeebruins.com/')
    ieee_linktree = discord.Embed(title='IEEE Linktree',
                                 url='https://linktr.ee/uclaieee')
    github = discord.Embed(title='SparkIEEE on Github',
                              url='https://github.com/bryanjwong/sparkieee')

    await ctx.send(msg)
    await ctx.send(embed=ieee_website)
    await ctx.send(embed=ieee_linktree)
    await ctx.send(embed=github)

@client.command()
async def projects(ctx):
    msg = 'Here is a list of our currently active projects:\n' \
          f'```{list(PROJECTS.keys())}```\n' \
          f'For more info about a particular project, use the `{client.command_prefix}project project_name` command.'
    await ctx.send(msg)

@client.command()
async def project(ctx, *args):
    if len(args) == 0:
        err_msg = 'Please supply the command with a project argument.\n' \
                  f'For example, `{client.command_prefix}project OPS` or `{client.command_prefix}project Micromouse`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
                  'Here is a list of our currently active projects:\n' \
                  f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        projects = ''
        if 'SPREAD_ID' in info:
            try:
                projects = f'**{args[0]} Projects:**'\
                           f'```{sheets.lookup(info["SPREAD_ID"])}```'
            except Exception as e:
                await ctx.send(e)
        leads = '\n'.join([f'{name}: @{id}' for name, id in info['LEADS'].items()])
        msg = f'{projects}' \
              f'**{args[0]} Project Leads:**\n' \
              f'```{leads}```' \
              f'**{args[0]} Links:**'
        e = discord.Embed(title=f'{args[0]} Facebook Group',
                          url=f'{info["FB_GROUP"]}')
        await ctx.send(msg, embed=e)

@client.command()
async def status(ctx, *args):
    if len(args) < 2:
        err_msg = 'Please supply the command with project and member name arguments.\n' \
            f'For example, `{client.command_prefix}status OPS "Kathy Daniels"` or ' \
            f'`{client.command_prefix}status Micromouse "Justin Jianto"`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
            'Here is a list of our currently active projects:\n' \
            f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        if 'SPREAD_ID' in info:
            try:
                msg = f'**{args[1]}\'s {args[0]} Project Status:**' \
                    f'```{sheets.lookup(info["SPREAD_ID"], name=args[1])}```'
            except Exception as e:
                await ctx.send(e)
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
        await ctx.send(msg)

@client.command()
async def checkoff(ctx, *args):
    if len(args) < 3:
        err_msg = 'Please supply the command with project, member name, and assignment arguments.\n' \
            f'For example, `{client.command_prefix}checkoff Aircopter "Jay Park" "Lab 1"` or ' \
            f'`{client.command_prefix}checkoff DAV "Fred Chu" "Deposit"`.'
        await ctx.send(err_msg)
    elif args[0].upper() not in PROJECTS.keys():
        err_msg = f'`{args[0]}` is not a valid project.\n' \
            'Here is a list of our currently active projects:\n' \
            f'```{list(PROJECTS.keys())}```\n'
        await ctx.send(err_msg)
    else:
        info = PROJECTS[args[0].upper()]
        new_val = 'x' if len(args) < 4 else args[3]
        if 'SPREAD_ID' in info:
            try:
                old_val = sheets.checkoff(info["SPREAD_ID"], assignment=args[1], name=args[2], val=new_val)
                if old_val == 'x':
                    msg = f'**{args[2]}** has already been checked off for **{args[0]} {args[1]}**.\n'
                else:
                    msg = f'**{args[2]}** has been checked off for **{args[0]} {args[1]}**!\n' \
                          f'```Value changed from "{old_val}" to "{new_val}"```'
            except Exception as e:
                await ctx.send(e)
        else:
            msg = f'{args[0]} does not currently have a checkoff sheet.'
        await ctx.send(msg)


@client.command()
async def extend(ctx, *args):
    pass

sheets = SheetTransformer()
client.run(BOT_TOKEN)

