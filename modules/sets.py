import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
from datetime import datetime
import re

# ========== CLASSES DO SISTEMA DE SET ==========

class SetFinalizadoView(ui.View):
    """View após set ser aprovado/recusado - APENAS STAFF VÊ"""
    def __init__(self, fivem_id, game_nick, user_id):
        super().__init__(timeout=None)
        self.fivem_id = fivem_id
        self.game_nick = game_nick
        self.user_id = user_id
    
    @ui.button(label="✅ Concluir Pedido", style=ButtonStyle.green, custom_id="concluir_set")
    async def concluir_set(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🏁 Pedido Concluído",
            description=f"Pedido concluído por {interaction.user.mention}",
            color=discord.Color.green()
        )
        
        self.clear_items()
        await interaction.message.edit(view=self)
        await interaction.channel.send(embed=embed)
    
    @ui.button(label="🗑️ Excluir Pedido", style=ButtonStyle.red, custom_id="excluir_set")
    async def excluir_set(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🗑️ Pedido Excluído",
            description=f"Pedido excluído por {interaction.user.mention}",
            color=discord.Color.red()
        )
        
        await interaction.channel.send(embed=embed)
        await asyncio.sleep(3)
        await interaction.channel.delete()

class SetStaffView(ui.View):
    """View com botões para staff aprovar/recusar set"""
    def __init__(self, fivem_id, game_nick, user_id, discord_user):
        super().__init__(timeout=None)
        self.fivem_id = fivem_id
        self.game_nick = game_nick
        self.user_id = user_id
        self.discord_user = discord_user
    
    @ui.button(label="✅ Aprovar Set", style=ButtonStyle.green, custom_id="aprovar_set", row=0)
    async def aprovar_set(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode aprovar!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Buscar membro no servidor
            member = interaction.guild.get_member(self.user_id)
            
            if member:
                # Criar nickname (máximo 32 caracteres)
                novo_nick = f"MEM | {self.game_nick} - {self.fivem_id}"
                if len(novo_nick) > 32:
                    # Encurtar se necessário
                    excesso = len(novo_nick) - 32
                    novo_nick = f"MEM | {self.game_nick[:15]} - {self.fivem_id[:10]}"
                
                # Mudar nickname
                await member.edit(nick=novo_nick)
                
                # Dar cargo de membro
                𝐌𝐞𝐦𝐛𝐫𝐨 = discord.utils.get(interaction.guild.roles, name="𝐌𝐞𝐦𝐛𝐫𝐨")
                if 𝐌𝐞𝐦𝐛𝐫𝐨:
                    await member.add_roles(𝐌𝐞𝐦𝐛𝐫𝐨)
                
                # Embed de aprovação
                embed_aprovado = discord.Embed(
                    title="✅ SET APROVADO!",
                    description=(
                        f"**👤 Discord:** {member.mention}\n"
                        f"**🎮 ID Fivem:** `{self.fivem_id}`\n"
                        f"**👤 Nick do Jogo:** `{self.game_nick}`\n"
                        f"**👑 Aprovado por:** {interaction.user.mention}\n"
                        f"**📅 Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                        f"✅ **Nickname alterado para:** `{novo_nick}`"
                    ),
                    color=discord.Color.green()
                )
                
                # Remover botões de aprovar/recusar
                self.clear_items()
                await interaction.message.edit(embed=embed_aprovado, view=self)
                
                # Adicionar view de concluir/excluir
                finalizado_view = SetFinalizadoView(self.fivem_id, self.game_nick, self.user_id)
                await interaction.channel.send("**Controles Finais:**", view=finalizado_view)
                
                # Notificação no canal
                await interaction.followup.send(
                    f"✅ Set de {member.mention} aprovado!\nNickname: `{novo_nick}`",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Usuário não encontrado! ID: `{self.user_id}`",
                    ephemeral=True
                )
                
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Não tenho permissão para alterar nickname!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Erro ao aprovar set: {e}")
            await interaction.followup.send(
                "❌ Erro ao aprovar set!",
                ephemeral=True
            )
    
    @ui.button(label="❌ Recusar Set", style=ButtonStyle.red, emoji="🚫", custom_id="recusar_set", row=0)
    async def recusar_set(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode recusar!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Embed de recusa
        embed_recusado = discord.Embed(
            title="❌ SET RECUSADO",
            description=(
                f"**🎮 ID Fivem:** `{self.fivem_id}`\n"
                f"**👤 Nick do Jogo:** `{self.game_nick}`\n"
                f"**👑 Recusado por:** {interaction.user.mention}\n"
                f"**📅 Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            ),
            color=discord.Color.red()
        )
        
        # Remover botões de aprovar/recusar
        self.clear_items()
        await interaction.message.edit(embed=embed_recusado, view=self)
        
        # Adicionar view de concluir/excluir
        finalizado_view = SetFinalizadoView(self.fivem_id, self.game_nick, self.user_id)
        await interaction.channel.send("**Controles Finais:**", view=finalizado_view)
        
        await interaction.followup.send(
            "✅ Set recusado!",
            ephemeral=True
        )

class SetForm(ui.Modal, title="📝 Pedido de Set"):
    """Modal para coletar dados do set"""
    
    fivem_id = ui.TextInput(
        label="Digite seu ID do Jogo (Fivem):",
        placeholder="Ex: 2314",
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )
    
    game_nick = ui.TextInput(
        label="Digite seu Nick do Jogo:",
        placeholder="Ex: João silva",
        style=discord.TextStyle.short,
        required=True,
        max_length=32
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # ========== VALIDAÇÃO DO ID (APENAS NÚMEROS) ==========
            if not self.fivem_id.value.isdigit():
                error_msg = await interaction.followup.send(
                    "❌ **ERRO:** ID do Fivem deve conter APENAS números!\nExemplo: `12344`",
                    ephemeral=True,
                    wait=True
                )
                await asyncio.sleep(5)
                await error_msg.delete()
                return
            
            # ========== VALIDAÇÃO DO NICK ==========
            def nick_valido(nick):
                padrao = r'^[a-zA-Z0-9 _\-\.]+$'
                return bool(re.match(padrao, nick))
            
            if not nick_valido(self.game_nick.value):
                error_msg = await interaction.followup.send(
                    "❌ **ERRO:** Nick do Jogo inválido!\nUse apenas: letras, espaço, _, -, .",
                    ephemeral=True,
                    wait=True
                )
                await asyncio.sleep(5)
                await error_msg.delete()
                return
            # ========== ENCONTRAR CANAL #aprovamento ==========
            canal_aprovamento = discord.utils.get(interaction.guild.text_channels, name="𝐀𝐩𝐫𝐨𝐯𝐚𝐦𝐞𝐧𝐭𝐨")
            
            if not canal_aprovamento:
                error_msg = await interaction.followup.send(
                    "❌ Canal #aprovamento não encontrado!",
                    ephemeral=True,
                    wait=True
                )
                await asyncio.sleep(5)
                await error_msg.delete()
                return
            
            # ========== VERIFICAR SE ID JÁ EXISTE ==========
            id_existente = False
            async for message in canal_aprovamento.history(limit=100):
                if message.embeds and len(message.embeds) > 0:
                    embed_desc = message.embeds[0].description or ""
                    if f"**🎮 ID Fivem:** `{self.fivem_id.value}`" in embed_desc:
                        id_existente = True
                        break
            
            if id_existente:
                error_msg = await interaction.followup.send(
                    f"❌ O ID Fivem `{self.fivem_id.value}` já está em uso!",
                    ephemeral=True,
                    wait=True
                )
                await asyncio.sleep(5)
                await error_msg.delete()
                return
            
            # ========== CRIAR EMBED DO PEDIDO ==========
            embed = discord.Embed(
                title=" NOVO PEDIDO DE SET",
                description=(
                    f"**👤 Discord:** {interaction.user.mention}\n"
                    f"**🆔 Discord ID:** `{interaction.user.id}`\n"
                    f"**🎮 ID Fivem:** `{self.fivem_id.value}`\n"
                    f"**👤 Nick do Jogo:** `{self.game_nick.value}`\n"
                    f"**📅 Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                    "**⏳ Status:** Aguardando aprovação"
                ),
                color=discord.Color.purple()
            )
            
            # ========== ENVIAR PARA 𝐀𝐩𝐫𝐨𝐯𝐚𝐦𝐞𝐧𝐭𝐨 ==========
            view = SetStaffView(self.fivem_id.value, self.game_nick.value, interaction.user.id, interaction.user)
            await canal_aprovamento.send(embed=embed, view=view)
            
            # ========== CONFIRMAÇÃO PARA O USUÁRIO ==========
            success_msg = await interaction.followup.send(
                f"✅ **Pedido enviado!**\n"
                f"**ID Fivem:** `{self.fivem_id.value}`\n"
                f"**Nick:** `{self.game_nick.value}`\n\n"
                f"A equipe analisará, e já lhe dara uma noticia!",
                ephemeral=True,
                wait=True
            )
            await asyncio.sleep(10)
            await success_msg.delete()
            
        except Exception as e:
            print(f"❌ Erro no pedido de set: {e}")
            error_msg = await interaction.followup.send(
                "❌ Erro ao enviar pedido!",
                ephemeral=True,
                wait=True
            )
            await asyncio.sleep(5)
            await error_msg.delete()

class SetOpenView(ui.View):
    """View inicial - botão para pedir set"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="Peça seu Set!", style=ButtonStyle.primary, custom_id="pedir_set")
    async def pedir_set(self, interaction: discord.Interaction, button: ui.Button):
        modal = SetForm()
        await interaction.response.send_modal(modal)

# ========== COMANDOS DO SISTEMA DE SET ==========

def setup(bot):
    """Configura o sistema de pedido de set"""
    
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setup_set(ctx):
        """Configura o painel de pedido de set no canal atual"""
        
        embed = discord.Embed(
            title=" **PEÇA SEU SET AQUI!**",
            description=(
                "Clique no botão abaixo e peça seu\n"
                "aprovamento para receber seu set\n"
                "personalizado no servidor.\n\n"
                "**📌 Instruções:**\n"
                "1. Clique em **'Peça seu Set!'**\n"
                "2. Digite seu **ID do Fivem**\n"
                "3. Digite seu **Nick do Jogo**\n"
            ),
            color=discord.Color.purple()
        )
        
        # BANNER DO SET (use seu próprio)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1460761801515073650/1460761861015339058/ChatGPT_Image_12_de_jan._de_2026_21_20_43.png")
        
        embed.set_footer(text="IDs únicos obrigatórios • Aprovação em até 1h")
        
        view = SetOpenView()
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()
    
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def check_id(ctx, *, fivem_id: str):
        """Verifica se um ID Fivem já está em uso"""
        canal_aprovamento = discord.utils.get(ctx.guild.text_channels, name="𝐀𝐩𝐫𝐨𝐯𝐚𝐦𝐞𝐧𝐭𝐨")
        
        if not canal_aprovamento:
            await ctx.send("❌ Canal #aprovamento não encontrado!")
            return
        
        # Validar se é número
        if not fivem_id.isdigit():
            await ctx.send("❌ ID deve conter apenas números!")
            return
        
        encontrado = False
        mensagem_link = None
        
        async for message in canal_aprovamento.history(limit=100):
            if message.embeds and len(message.embeds) > 0:
                embed = message.embeds[0]
                if embed.description and f"**🎮 ID Fivem:** `{fivem_id}`" in embed.description:
                    encontrado = True
                    mensagem_link = message.jump_url
                    break
        
        if encontrado:
            embed = discord.Embed(
                title="🔍 ID Encontrado",
                description=f"ID `{fivem_id}` já está em uso!",
                color=discord.Color.orange()
            )
            embed.add_field(name="Link do Pedido", value=f"[Clique aqui]({mensagem_link})")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"✅ ID `{fivem_id}` não está em uso!")
    
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def sets_pendentes(ctx):
        """Mostra todos os pedidos de set pendentes"""
        canal_aprovamento = discord.utils.get(ctx.guild.text_channels, name="𝐀𝐩𝐫𝐨𝐯𝐚𝐦𝐞𝐧𝐭𝐨")
        
        if not canal_aprovamento:
            await ctx.send("❌ Canal #aprovamento não encontrado!")
            return
        
        pedidos_pendentes = []
        
        async for message in canal_aprovamento.history(limit=50):
            if message.embeds and len(message.embeds) > 0:
                embed = message.embeds[0]
                if "Aguardando aprovação" in (embed.description or ""):
                    pedidos_pendentes.append(message)
        
        if not pedidos_pendentes:
            await ctx.send("✅ Nenhum pedido de set pendente!")
            return
        
        embed = discord.Embed(
            title="📋 Pedidos de Set Pendentes",
            description=f"Total: **{len(pedidos_pendentes)}** pedidos",
            color=discord.Color.blue()
        )
        
        for i, msg in enumerate(pedidos_pendentes[:5], 1):
            pedido_embed = msg.embeds[0]
            
            # Extrair informações do embed
            descricao = pedido_embed.description or ""
            
            # Encontrar ID Fivem
            id_match = re.search(r'\*\*🎮 ID Fivem:\*\* `([^`]+)`', descricao)
            id_fivem = id_match.group(1) if id_match else "Não encontrado"
            
            # Encontrar Nick
            nick_match = re.search(r'\*\*👤 Nick do Jogo:\*\* `([^`]+)`', descricao)
            nick = nick_match.group(1) if nick_match else "Não encontrado"
            
            embed.add_field(
                name=f"Pedido #{i}",
                value=f"**ID:** `{id_fivem[:15]}...`\n**Nick:** `{nick}`\n[Ver pedido]({msg.jump_url})",
                inline=True
            )
        
        if len(pedidos_pendentes) > 5:
            embed.set_footer(text=f"Mostrando 5 de {len(pedidos_pendentes)} pedidos")
        
        await ctx.send(embed=embed)
    
    print("✅ Módulo de sets carregado com sucesso!")
