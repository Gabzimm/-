intents = discord.Intents.default()
intents.members = True  # NECESSÁRIO PARA DETECTAR NOVOS MEMBROS

bot = commands.Bot(command_prefix="!", intents=intents)

# CONFIGURAÇÕES
TOKEN = "1213819385576300595"
CARGO_ID = 1460747749241913434  # ID DO CARGO AUTOMÁTICO

@bot.event
async def on_ready():
    print(f" Bot conectado como {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        cargo = member.guild.get_role(CARGO_ID)
        if cargo:
            await member.add_roles(cargo)
            print(f"Cargo '{cargo.name}' adicionado para {member.name}")
        else:
            print(" Cargo não encontrado")
    except Exception as e:
        print(f"Erro ao dar cargo: {e}")
