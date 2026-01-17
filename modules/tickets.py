import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
from datetime import datetime
import re

# ========== CLASSES PRINCIPAIS ==========

class TicketFinalizadoView(ui.View):
    """View após ticket fechado - APENAS STAFF VÊ"""
    def __init__(self, ticket_owner_id, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id
        self.ticket_channel = ticket_channel
    
    @ui.button(label="✅ Finalizar Ticket", style=ButtonStyle.green, custom_id="finalizar_ticket")
    async def finalizar_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # APENAS STAFF pode finalizar
        staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode finalizar!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Embed de finalização
        embed = discord.Embed(
            title="🏁 Ticket Finalizado",
            description=f"Ticket finalizado por {interaction.user.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Finalizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Remover botões
        self.clear_items()
        await interaction.message.edit(view=self)
        
        await self.ticket_channel.send(embed=embed)
        
    
    @ui.button(label="🔄 Reabrir Ticket", style=ButtonStyle.blurple, custom_id="reabrir_ticket")
    async def reabrir_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # APENAS STAFF pode reabrir
        staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode reabrir!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Reabrir canal (tornar escrevível novamente)
        overwrites = self.ticket_channel.overwrites
        for target, overwrite in overwrites.items():
            if isinstance(target, discord.Role) and target.name == "@everyone":
                overwrite.send_messages = True
        
        await self.ticket_channel.edit(overwrites=overwrites)
        
        # Remover "🔒-" do nome se existir
        if self.ticket_channel.name.startswith("🔒-"):
            novo_nome = f"🎫-{self.ticket_channel.name[2:]}"
            await self.ticket_channel.edit(name=novo_nome)
        
        # Embed de reabertura + botões ABAIXO
        embed_reaberto = discord.Embed(
            title="🔄 Ticket Reaberto",
            description=f"Ticket reaberto por {interaction.user.mention}",
            color=discord.Color.blue()
        )
        
        # View com botões Deletar e Fechar
        reaberto_view = TicketReabertoView(self.ticket_owner_id, self.ticket_channel)
        
        # Remover botões antigos
        self.clear_items()
        await interaction.message.edit(view=self)
        
        # Enviar NOVA mensagem com botões ABAIXO do embed
        await self.ticket_channel.send(embed=embed_reaberto)
        await self.ticket_channel.send("**Painel de Controle:**", view=reaberto_view)

class TicketReabertoView(ui.View):
    """View quando ticket é reaberto - com Deletar e Fechar"""
    def __init__(self, ticket_owner_id, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id
        self.ticket_channel = ticket_channel
    
    @ui.button(label="🔒 Fechar Ticket", style=ButtonStyle.gray, emoji="🔒", custom_id="close_ticket_reaberto", row=0)
    async def close_ticket_reaberto(self, interaction: discord.Interaction, button: ui.Button):
        # QUALQUER PESSOA pode fechar (quem abriu ou staff)
        if interaction.user.id != self.ticket_owner_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas quem abriu ou ADMs podem fechar!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Fechar canal
        overwrites = self.ticket_channel.overwrites
        for target, overwrite in overwrites.items():
            if isinstance(target, discord.Role) and target.name == "@everyone":
                overwrite.send_messages = False
        
        await self.ticket_channel.edit(overwrites=overwrites)
        await self.ticket_channel.edit(name=f"🔒-{self.ticket_channel.name[2:]}")
        
        # Remover botões
        self.clear_items()
        await interaction.message.edit(view=self)
        
        # Criar painel de ticket fechado
        try:
            user = await interaction.client.fetch_user(self.ticket_owner_id)
            user_info = f"{user.mention}\nID: `{user.id}`"
        except:
            user_info = f"ID: `{self.ticket_owner_id}`"
        
        embed_fechado = discord.Embed(
            title="📋 Ticket Fechado",
            description=(
                f"**👤 Usuário:** {user_info}\n"
                f"**👑 Fechado por:** {interaction.user.mention}\n"
                f"**📅 Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            ),
            color=discord.Color.orange()
        )
        
        # Enviar embed primeiro
        await self.ticket_channel.send(embed=embed_fechado)
        
        # Enviar botões em mensagem SEPARADA
        await self.ticket_channel.send("**Painel de Controle (apenas staff):**", view=TicketFinalizadoView(self.ticket_owner_id, self.ticket_channel))
    
    @ui.button(label="🗑️ Deletar Ticket", style=ButtonStyle.red, emoji="🗑️", custom_id="delete_ticket_reaberto", row=0)
    async def delete_ticket_reaberto(self, interaction: discord.Interaction, button: ui.Button):
        # APENAS STAFF pode deletar
        staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode deletar tickets!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Confirmar deleção
        embed = discord.Embed(
            title="🗑️ Ticket Deletado",
            description=f"Ticket deletado por {interaction.user.mention}",
            color=discord.Color.red()
        )
        
        await self.ticket_channel.send(embed=embed)
        
        # Esperar 3 segundos e deletar
        await asyncio.sleep(3)
        await self.ticket_channel.delete()
        
        # DM para o usuário
        try:
            user = await interaction.client.fetch_user(self.ticket_owner_id)
            await user.send("🗑️ Seu ticket foi deletado pela equipe de suporte.")
        except:
            pass

class TicketStaffView(ui.View):
    """View inicial do ticket aberto - com Deletar e Fechar"""
    def __init__(self, ticket_owner_id, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id
        self.ticket_channel = ticket_channel
    
    @ui.button(label="🔒 Fechar Ticket", style=ButtonStyle.gray, emoji="🔒", custom_id="close_ticket_staff", row=0)
    async def close_ticket_staff(self, interaction: discord.Interaction, button: ui.Button):
        # QUALQUER PESSOA pode fechar (quem abriu ou staff)
        if interaction.user.id != self.ticket_owner_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas quem abriu ou ADMs podem fechar!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Fechar canal
        overwrites = self.ticket_channel.overwrites
        for target, overwrite in overwrites.items():
            if isinstance(target, discord.Role) and target.name == "@everyone":
                overwrite.send_messages = False
        
        await self.ticket_channel.edit(overwrites=overwrites)
        await self.ticket_channel.edit(name=f"🔒-{self.ticket_channel.name[2:]}")
        
        # Remover TODOS os botões da mensagem atual
        self.clear_items()
        await interaction.message.edit(view=self)
        
        # CRIAR NOVO PAINEL DE TICKET FECHADO
        try:
            user = await interaction.client.fetch_user(self.ticket_owner_id)
            user_info = f"{user.mention}\nID: `{user.id}`"
        except:
            user_info = f"ID: `{self.ticket_owner_id}`"
        
        embed_fechado = discord.Embed(
            title="📋 Ticket Fechado",
            description=(
                f"**👤 Usuário:** {user_info}\n"
                f"**👑 Fechado por:** {interaction.user.mention}\n"
                f"**📅 Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            ),
            color=discord.Color.orange()
        )
        
        # Enviar embed primeiro
        await self.ticket_channel.send(embed=embed_fechado)
        
        # Enviar botões em mensagem SEPARADA
        await self.ticket_channel.send("**Painel de Controle (apenas staff):**", view=TicketFinalizadoView(self.ticket_owner_id, self.ticket_channel))
    
    
    @ui.button(label="🗑️ Deletar Ticket", style=ButtonStyle.red, emoji="🗑️", custom_id="delete_ticket_staff", row=0)
    async def delete_ticket_staff(self, interaction: discord.Interaction, button: ui.Button):
        # APENAS STAFF pode deletar
        staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode deletar tickets!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Confirmar deleção
        embed = discord.Embed(
            title="🗑️ Ticket Deletado",
            description=f"Ticket deletado por {interaction.user.mention}",
            color=discord.Color.red()
        )
        
        await self.ticket_channel.send(embed=embed)
        
        # Esperar 3 segundos e deletar
        await asyncio.sleep(3)
        await self.ticket_channel.delete()
        
        # DM para o usuário
        try:
            user = await interaction.client.fetch_user(self.ticket_owner_id)
            await user.send("🗑️ Seu ticket foi deletado pela equipe de suporte.")
        except:
            pass

class TicketOpenView(ui.View):
    """View inicial - apenas botão para abrir ticket"""
    def __init__(self):
        super().__init__(timeout=None)
    
       @ui.button(label="Abrir Ticket", style=ButtonStyle.primary, emoji="🎫", custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Responder IMEDIATAMENTE
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 1. VERIFICAÇÃO DE CATEGORIA
            canal_ticket_base = None
            for channel in interaction.guild.text_channels:
                if "ticket" in channel.name.lower() and "🎟️" in channel.name:
                    canal_ticket_base = channel
                    break
            
            if not canal_ticket_base:
                await interaction.followup.send("❌ Canal de tickets base não encontrado! Procure um canal com 'ticket' e 🎟️ no nome.", ephemeral=True)
                return
            
            # 2. VERIFICAR SE JÁ TEM TICKET ABERTO
            categoria = canal_ticket_base.category
            if not categoria:
                await interaction.followup.send("❌ O canal base precisa estar em uma categoria!", ephemeral=True)
                return
            
            for channel in categoria.channels:
                if channel.topic and str(interaction.user.id) in channel.topic:
                    await interaction.followup.send(
                        f"❌ Você já tem um ticket aberto: {channel.mention}",
                        ephemeral=True
                    )
                    return
            
            # 3. CONFIGURAR PERMISSÕES
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # 4. ADICIONAR STAFF COM TRY-CATCH
            staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]
            for role_name in staff_roles:
                try:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            read_messages=True, 
                            send_messages=False,
                            read_message_history=True
                        )
                except Exception as e:
                    print(f"Aviso: Não consegui processar role {role_name}: {e}")
                    continue
            
            # 5. CRIAR CANAL DE TICKET
            ticket_channel = await interaction.guild.create_text_channel(
                name=f"🎫-{interaction.user.display_name[:20]}",  # Limitar nome
                category=categoria,
                overwrites=overwrites,
                topic=f"Ticket de {interaction.user.name} | ID: {interaction.user.id}",
                reason=f"Ticket criado por {interaction.user.name}"
            )
            
            # 6. ENVIAR MENSAGENS NO TICKET
            embed = discord.Embed(
                title=f"🎫 Ticket de {interaction.user.display_name}",
                description=(
                    f"**Aberto por:** {interaction.user.mention}\n"
                    f"**ID:** `{interaction.user.id}`\n"
                    f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                    "**📝 Descreva seu problema ou dúvida abaixo:**"
                ),
                color=discord.Color.purple()
            )
            
            staff_view = TicketStaffView(interaction.user.id, ticket_channel)
            
            # Primeiro o embed
            await ticket_channel.send(
                content=f"{interaction.user.mention} **Ticket criado!**\nEquipe será notificada em breve.",
                embed=embed
            )
            
            # Depois os botões
            await ticket_channel.send("**Painel de Controle:**", view=staff_view)
            
            # 7. NOTIFICAR STAFF (OPCIONAL)
            staff_mention = ""
            for role_name in ["𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫"]:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    staff_mention += f"{role.mention} "
            
            if staff_mention:
                await ticket_channel.send(f"{staff_mention}Novo ticket criado!")
            
            # 8. CONFIRMAÇÃO PARA O USUÁRIO
            await interaction.followup.send(
                f"✅ Ticket criado com sucesso! Acesse: {ticket_channel.mention}",
                ephemeral=True
            )
            
            print(f"✅ Ticket criado para {interaction.user.name}: {ticket_channel.name}")
            
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Não tenho permissão para criar canais ou gerenciar permissões!",
                ephemeral=True
            )
            print("❌ Erro de permissão ao criar ticket")
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Erro do Discord ao criar canal: {e.status}",
                ephemeral=True
            )
            print(f"❌ HTTPException: {e}")
        except Exception as e:
            await interaction.followup.send(
                "❌ Erro inesperado ao criar ticket. Contate um administrador.",
                ephemeral=True
            )
            print(f"❌ Erro grave em open_ticket: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
# ========== COMANDOS ==========

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        """Configura o painel de tickets"""
        
        embed = discord.Embed(
            title="🎫 **SISTEMA DE TICKETS**",
            description=(
                "Escolha uma opção com base no assunto que você\n"
                "deseja discutir com um membro da equipe através\n"
                "de um ticket:\n\n"
                "**📌 Observações:**\n"
                "• Evite abrir um ticket sem um motivo válido\n"
                "• Mantenha o respeito sempre\n"
                "• Descreva seu problema com detalhes\n"
                "• Aguarde pacientemente a resposta da equipe"
            ),
            color=discord.Color.purple()
        )
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1462150327070359707/1462151759337361654/ChatGPT_Image_17_de_jan._de_2026_18_28_54.png?ex=696d2670&is=696bd4f0&hm=10fbb4366a6ba683e0b93a90e2cc7e2b67748dcbdacee8fde06a768050748bd5")
        embed.set_footer(text="Atenção: Não abuse do sistema")
        
        view = TicketOpenView()
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticket_info(self, ctx, channel: discord.TextChannel = None):
        """Mostra informações de um ticket"""
        if channel is None:
            channel = ctx.channel
        
        if not channel.name.startswith("🎫-") and not channel.name.startswith("🔒-"):
            await ctx.send("❌ Este não é um canal de ticket!")
            return
        
        # Extrair informações do topic
        info = {}
        if channel.topic:
            if "ID:" in channel.topic:
                match = re.search(r'ID: (\d+)', channel.topic)
                if match:
                    info['user_id'] = match.group(1)
            
            if "Ticket de" in channel.topic:
                match = re.search(r'Ticket de (.+?) \|', channel.topic)
                if match:
                    info['username'] = match.group(1)
        
        embed = discord.Embed(
            title="📋 Informações do Ticket",
            description=f"Canal: {channel.mention}",
            color=discord.Color.blue()
        )
        
        if 'username' in info:
            embed.add_field(name="👤 Usuário", value=info['username'], inline=True)
        
        if 'user_id' in info:
            embed.add_field(name="🆔 ID Discord", value=f"`{info['user_id']}`", inline=True)
        
        embed.add_field(name="📅 Criado em", value=channel.created_at.strftime('%d/%m/%Y %H:%M'), inline=True)
        embed.add_field(name="🔒 Status", value="Fechado" if channel.name.startswith("🔒-") else "Aberto", inline=True)
        
        if "+" in channel.name:
            staff_name = channel.name.split("+")[-1]
            embed.add_field(name="👑 Staff Responsável", value=staff_name, inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Configura o sistema de tickets"""
    await bot.add_cog(TicketsCog(bot))
    print("✅ Módulo de tickets (versão final) carregado!")
