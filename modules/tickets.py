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
            # 1. VERIFICAÇÃO DO CANAL BASE
            canal_ticket_base = None
            for channel in interaction.guild.text_channels:
                # Procura por "ticket" (case insensitive) e emoji 🎟️
                channel_lower = channel.name.lower()
                if ("ticket" in channel_lower or "tícket" in channel_lower or "𝐓𝐢𝐜𝐤𝐞𝐭" in channel.name) and "🎟️" in channel.name:
                    canal_ticket_base = channel
                    break
            
            if not canal_ticket_base:
                # Tenta encontrar qualquer canal com "ticket" no nome
                for channel in interaction.guild.text_channels:
                    if "ticket" in channel.name.lower():
                        canal_ticket_base = channel
                        break
            
            if not canal_ticket_base:
                await interaction.followup.send(
                    "❌ Canal de tickets não encontrado! Um administrador precisa criar um canal com 'ticket' no nome.",
                    ephemeral=True
                )
                return
            
            print(f"📌 Canal base encontrado: {canal_ticket_base.name}")
            
            # 2. VERIFICAR SE JÁ TEM TICKET ABERTO
            categoria = canal_ticket_base.category
            if not categoria:
                # Se não tiver categoria, usa a categoria do canal atual
                categoria = interaction.channel.category
                if not categoria:
                    await interaction.followup.send(
                        "❌ Não foi possível determinar a categoria para o ticket!",
                        ephemeral=True
                    )
                    return
            
            print(f"📌 Categoria definida: {categoria.name}")
            
            # Verificar tickets existentes
            tickets_abertos = []
            for channel in categoria.channels:
                if channel.topic and str(interaction.user.id) in channel.topic:
                    tickets_abertos.append(channel)
            
            if tickets_abertos:
                await interaction.followup.send(
                    f"❌ Você já tem {'um ticket' if len(tickets_abertos) == 1 else f'{len(tickets_abertos)} tickets'} aberto(s): "
                    f"{', '.join([c.mention for c in tickets_abertos])}",
                    ephemeral=True
                )
                return
            
            # 3. CONFIGURAR PERMISSÕES
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False
                ),
                interaction.user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    attach_files=True,
                    read_message_history=True
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_channels=True,
                    manage_messages=True
                )
            }
            
            # 4. ADICIONAR STAFF
            staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", 
                          "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]
            
            staff_encontradas = 0
            for role_name in staff_roles:
                try:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,  # Staff pode escrever
                            manage_messages=True,
                            read_message_history=True
                        )
                        staff_encontradas += 1
                        print(f"✅ Role de staff adicionada: {role_name}")
                except Exception as e:
                    print(f"⚠️ Aviso com role {role_name}: {e}")
                    continue
            
            if staff_encontradas == 0:
                print("⚠️ Nenhuma role de staff encontrada!")
            
            # 5. CRIAR CANAL DE TICKET
            # Limpar nome do usuário para evitar problemas
            nome_usuario = interaction.user.display_name
            nome_usuario_limpo = ''.join(c for c in nome_usuario if c.isalnum() or c in [' ', '-', '_'])
            if not nome_usuario_limpo.strip():
                nome_usuario_limpo = f"user-{interaction.user.id}"
            
            nome_canal = f"🎫-{nome_usuario_limpo[:20]}"
            
            print(f"📝 Criando canal: {nome_canal}")
            
            ticket_channel = await interaction.guild.create_text_channel(
                name=nome_canal,
                category=categoria,
                overwrites=overwrites,
                topic=f"Ticket de {interaction.user.name} | ID: {interaction.user.id}",
                reason=f"Ticket criado por {interaction.user.name} ({interaction.user.id})"
            )
            
            print(f"✅ Canal criado: {ticket_channel.name}")
            
            # 6. ENVIAR MENSAGENS NO TICKET
            embed = discord.Embed(
                title=f"🎫 Ticket de {interaction.user.display_name}",
                description=(
                    f"**👤 Aberto por:** {interaction.user.mention}\n"
                    f"**🆔 ID:** `{interaction.user.id}`\n"
                    f"**📅 Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                    "**📝 Descreva seu problema ou dúvida abaixo:**\n"
                    "• Seja claro e objetivo\n"
                    "• Forneça todas as informações necessárias\n"
                    "• Aguarde a resposta da equipe"
                ),
                color=discord.Color.purple()
            )
            embed.set_footer(text="Equipe de suporte será notificada automaticamente")
            
            staff_view = TicketStaffView(interaction.user.id, ticket_channel)
            
            # Enviar mensagens
            mensagem_embed = await ticket_channel.send(
                content=f"## 👋 Olá {interaction.user.mention}!\nSeu ticket foi criado com sucesso.",
                embed=embed
            )
            
            mensagem_botoes = await ticket_channel.send(
                "**🔧 Painel de Controle:**",
                view=staff_view
            )
            
            # Fixar mensagens importantes
            try:
                await mensagem_embed.pin()
                await mensagem_botoes.pin()
            except:
                pass
            
            # 7. NOTIFICAR STAFF
            mention_roles = []
            for role_name in ["00, 𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫"]:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    mention_roles.append(role.mention)
            
            if mention_roles:
                mensagem_staff = await ticket_channel.send(
                    f"{' '.join(mention_roles)}\n"
                    f"📬 **Novo ticket criado!**\n"
                    f"**Usuário:** {interaction.user.mention} (`{interaction.user.id}`)\n"
                    f"**Ticket:** {ticket_channel.mention}"
                )
                
                try:
                    await mensagem_staff.pin()
                except:
                    pass
            
            # 8. CONFIRMAÇÃO PARA O USUÁRIO
            await interaction.followup.send(
                f"✅ **Ticket criado com sucesso!**\n"
                f"Acesse: {ticket_channel.mention}\n"
                f"A equipe foi notificada e responderá em breve.",
                ephemeral=True
            )
            
            print(f"🎉 Ticket criado com sucesso para {interaction.user.name}")
            
        except discord.Forbidden as e:
            print(f"❌ ERRO DE PERMISSÃO: {e}")
            await interaction.followup.send(
                "❌ **Erro de permissão!**\n"
                "O bot precisa das permissões:\n"
                "• Gerenciar Canais\n"
                "• Gerenciar Permissões\n"
                "• Enviar Mensagens\n"
                "• Fixar Mensagens",
                ephemeral=True
            )
        except discord.HTTPException as e:
            print(f"❌ ERRO HTTP: {e.status} - {e.text}")
            await interaction.followup.send(
                f"❌ **Erro do Discord:** {e.status}\n"
                "Tente novamente em alguns instantes.",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ ERRO INESPERADO: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            
            await interaction.followup.send(
                "❌ **Erro inesperado ao criar ticket.**\n"
                "Os administradores foram notificados.",
                ephemeral=True
            )

# ========== COMANDOS ==========

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="setup_tickets")
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        """Configura o painel de tickets"""
        
        embed = discord.Embed(
            title="🎫 **SISTEMA DE TICKETS**",
            description=(
                "**Clique no botão abaixo para abrir um ticket**\n\n"
                "Escolha esta opção se você precisa de ajuda com:\n"
                "• Problemas no servidor\n"
                "• Dúvidas sobre cargos\n"
                "• Reportar jogadores\n"
                "• Outras questões importantes\n\n"
                "**📌 Observações:**\n"
                "• Evite abrir tickets sem motivo válido\n"
                "• Mantenha o respeito sempre\n"
                "• Descreva seu problema com detalhes\n"
                "• Aguarde pacientemente a resposta"
            ),
            color=discord.Color.purple()
        )
        
        # URL da imagem do seu servidor (mantida a mesma)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1462150327070359707/1462151759337361654/ChatGPT_Image_17_de_jan._de_2026_18_28_54.png?ex=696d2670&is=696bd4f0&hm=10fbb4366a6ba683e0b93a90e2cc7e2b67748dcbdacee8fde06a768050748bd5")
        embed.set_footer(text="Hospital APP • Suporte 24h")
        
        view = TicketOpenView()
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()
        
        print(f"✅ Painel de tickets configurado por {ctx.author.name}")
    
    @commands.command(name="ticket_info")
    @commands.has_permissions(administrator=True)
    async def ticket_info(self, ctx, channel: discord.TextChannel = None):
        """Mostra informações de um ticket"""
        if channel is None:
            channel = ctx.channel
        
        if not channel.name.startswith(("🎫-", "🔒-")):
            await ctx.send("❌ Este não é um canal de ticket!")
            return
        
        # Extrair informações do topic
        user_id = None
        username = "Desconhecido"
        
        if channel.topic:
            # Procurar ID
            import re
            match_id = re.search(r'ID:\s*(\d+)', channel.topic)
            if match_id:
                user_id = match_id.group(1)
            
            # Procurar nome
            match_name = re.search(r'Ticket de\s*(.+?)\s*\||$', channel.topic)
            if match_name:
                username = match_name.group(1).strip()
        
        embed = discord.Embed(
            title="📋 Informações do Ticket",
            description=f"**Canal:** {channel.mention}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="👤 Usuário", value=username, inline=True)
        
        if user_id:
            embed.add_field(name="🆔 ID Discord", value=f"`{user_id}`", inline=True)
            try:
                user = await self.bot.fetch_user(int(user_id))
                embed.add_field(name="🎭 Tag", value=f"{user}", inline=True)
            except:
                pass
        
        embed.add_field(name="📅 Criado em", value=channel.created_at.strftime('%d/%m/%Y %H:%M'), inline=True)
        embed.add_field(name="🔒 Status", value="Fechado" if channel.name.startswith("🔒-") else "Aberto", inline=True)
        
        # Contar mensagens
        try:
            count = 0
            async for _ in channel.history(limit=None):
                count += 1
            embed.add_field(name="💬 Mensagens", value=str(count), inline=True)
        except:
            pass
        
        await ctx.send(embed=embed)
    
    @commands.command(name="fechar_ticket")
    async def fechar_ticket(self, ctx):
        """Fecha o ticket atual (disponível para quem abriu ou staff)"""
        if not ctx.channel.name.startswith(("🎫-", "🔒-")):
            await ctx.send("❌ Este comando só funciona em canais de ticket!")
            return
        
        # Extrair ID do usuário do topic
        user_id = None
        if ctx.channel.topic:
            import re
            match = re.search(r'ID:\s*(\d+)', ctx.channel.topic)
            if match:
                user_id = int(match.group(1))
        
        # Verificar permissão
        if ctx.author.id != user_id and not ctx.author.guild_permissions.administrator:
            # Verificar se é staff
            staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "𝐌𝐨𝐝𝐞𝐫"]
            if not any(role.name in staff_roles for role in ctx.author.roles):
                await ctx.send("❌ Apenas quem abriu o ticket ou staff pode fechá-lo!")
                return
        
        # Fechar canal
        overwrites = ctx.channel.overwrites
        for target, overwrite in overwrites.items():
            if isinstance(target, discord.Role) and target.name == "@everyone":
                overwrite.send_messages = False
        
        await ctx.channel.edit(overwrites=overwrites)
        
        # Atualizar nome se necessário
        if ctx.channel.name.startswith("🎫-"):
            await ctx.channel.edit(name=f"🔒-{ctx.channel.name[2:]}")
        
        embed = discord.Embed(
            title="🔒 Ticket Fechado",
            description=f"Fechado por: {ctx.author.mention}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        await ctx.send(embed=embed)
        print(f"✅ Ticket fechado por {ctx.author.name}")

async def setup(bot):
    """Configura o sistema de tickets"""
    await bot.add_cog(TicketsCog(bot))
    print("✅ Módulo de tickets (versão final) carregado!")
