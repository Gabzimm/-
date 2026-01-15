from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os
import sys

# ==================== KEEP-ALIVE SERVER ====================
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot Discord está online! Acesse /health para status."

@app.route('/health')
def health():
    return "🟢 ONLINE", 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Servidor keep-alive iniciado na porta 8080")

# ==================== BOT DISCORD ====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot logado como: {bot.user}')
    print(f'🆔 ID: {bot.user.id}')
    print(f'📡 Ping: {round(bot.latency * 1000)}ms')
    print('🚀 Bot pronto para uso!')

@bot.command()
async def ping(ctx):
    """Responde com a latência do bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! {latency}ms')

@bot.command()
async def hello(ctx):
    """Diz olá"""
    await ctx.send(f'👋 Olá {ctx.author.mention}!')

# ==================== INICIALIZAÇÃO ====================
if __name__ == '__main__':
    print("🚀 Iniciando bot Discord...")
    
    # Verificar token
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado!")
        print("💡 Adicione em: Render Dashboard → Environment → Add Variable")
        print("   Nome: DISCORD_TOKEN")
        print("   Valor: seu_token_do_discord")
        sys.exit(1)
    
    print("✅ Token encontrado")
    
    # Iniciar keep-alive
    keep_alive()
    
    # Iniciar bot
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ ERRO: Token inválido ou expirado!")
        print("💡 Gere um novo token em: https://discord.com/developers/applications")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
