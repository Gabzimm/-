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
        # Responder IMEDIATAMENTE com logs
        print(f"\n" + "="*60)
        print(f"🎯 [TICKET] Iniciando criação de ticket")
        print(f"🎯 [TICKET] Usuário: {interaction.user.name} ({interaction.user.id})")
        print(f"🎯 [TICKET] Servidor: {interaction.guild.name}")
        print(f"🎯 [TICKET] Canal de comando: {interaction.channel.name}")
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 1. VERIFICAÇÃO DO CANAL BASE
            print("🔍 [DEBUG] Procurando canal base 'ticket'...")
            canal_ticket_base = None
            
            # Lista todos os canais para debug
            print(f"📊 [DEBUG] Total de canais no servidor: {len(interaction.guild.text_channels)}")
            for i, channel in enumerate(interaction.guild.text_channels[:10]):  # Mostra apenas os primeiros 10
                print(f"  {i+1}. #{channel.name} (Categoria: {channel.category.name if channel.category else 'Nenhuma'})")
            
            for channel in interaction.guild.text_channels:
                channel_lower = channel.name.lower()
                # Procura de forma flexível
                if ("ticket" in channel_lower or "tícket" in channel_lower or "𝐓𝐢𝐜𝐤𝐞𝐭" in channel.name):
                    canal_ticket_base = channel
                    print(f"✅ [DEBUG] Canal base encontrado: '{channel.name}'")
                    print(f"   • Tem 🎟️? {'Sim' if '🎟️' in channel.name else 'Não'}")
                    print(f"   • Categoria: {channel.category.name if channel.category else 'Nenhuma'}")
                    break
            
            if not canal_ticket_base:
                print("❌ [DEBUG] Nenhum canal com 'ticket' no nome encontrado!")
                await interaction.followup.send(
                    "❌ **Erro:** Nenhum canal com 'ticket' no nome foi encontrado!\n"
                    "Um administrador precisa criar um canal chamado 'ticket' ou similar.",
                    ephemeral=True
                )
                return
            
            # 2. VERIFICAR CATEGORIA
            print("🔍 [DEBUG] Verificando categoria...")
            categoria = canal_ticket_base.category
            
            if not categoria:
                print("⚠️ [DEBUG] Canal base não está em categoria, usando categoria atual...")
                categoria = interaction.channel.category
            
            if not categoria:
                print("❌ [DEBUG] Nenhuma categoria disponível!")
                # Tenta criar uma categoria
                try:
                    print("🔄 [DEBUG] Tentando criar categoria '🎫 Tickets'...")
                    categoria = await interaction.guild.create_category("🎫 Tickets")
                    print(f"✅ [DEBUG] Categoria criada: {categoria.name}")
                except Exception as e:
                    print(f"❌ [DEBUG] Erro ao criar categoria: {e}")
                    await interaction.followup.send(
                        "❌ Não foi possível criar uma categoria para os tickets!",
                        ephemeral=True
                    )
                    return
            
            print(f"📌 [DEBUG] Categoria definida: '{categoria.name}' (ID: {categoria.id})")
            
            # 3. VERIFICAR TICKETS EXISTENTES
            print(f"🔍 [DEBUG] Verificando tickets existentes na categoria '{categoria.name}'...")
            print(f"📊 [DEBUG] Canais na categoria: {len(categoria.channels)}")
            
            tickets_abertos = []
            for channel in categoria.channels:
                print(f"  • Canal: #{channel.name} | Topic: {channel.topic[:50] if channel.topic else 'None'}")
                if channel.topic and str(interaction.user.id) in channel.topic:
                    tickets_abertos.append(channel)
                    print(f"⚠️ [DEBUG] Ticket já aberto encontrado: #{channel.name}")
            
            if tickets_abertos:
                print(f"❌ [DEBUG] Usuário já tem {len(tickets_abertos)} ticket(s) aberto(s)")
                await interaction.followup.send(
                    f"❌ Você já tem um ticket aberto: {tickets_abertos[0].mention}",
                    ephemeral=True
                )
                return
            
            print("✅ [DEBUG] Nenhum ticket aberto encontrado para este usuário")
            
            # 4. CONFIGURAR PERMISSÕES
            print("🔧 [DEBUG] Configurando permissões...")
            
            # Verificar permissões do bot
            print(f"🔑 [DEBUG] Permissões do bot no servidor:")
            perms = interaction.guild.me.guild_permissions
            print(f"  • Gerenciar Canais: {perms.manage_channels}")
            print(f"  • Gerenciar Permissões: {perms.manage_roles}")
            print(f"  • Gerenciar Mensagens: {perms.manage_messages}")
            print(f"  • Ver Canais: {perms.view_channel}")
            
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
                    manage_messages=True,
                    manage_roles=True
                )
            }
            
            # 5. ADICIONAR STAFF ROLES
            print("👑 [DEBUG] Buscando roles de staff...")
            staff_roles = ["00", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", 
                          "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐝𝐞 𝐅𝐚𝐦𝐫", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐦𝐞𝐧𝐭𝐨", "𝐌𝐨𝐝𝐞𝐫"]
            
            staff_encontradas = 0
            for role_name in staff_roles:
                try:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        print(f"✅ [DEBUG] Role '{role_name}' encontrada! (ID: {role.id})")
                        overwrites[role] = discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,
                            manage_messages=True,
                            read_message_history=True
                        )
                        staff_encontradas += 1
                    else:
                        print(f"⚠️ [DEBUG] Role '{role_name}' NÃO encontrada")
                except Exception as e:
                    print(f"❌ [DEBUG] Erro ao buscar role '{role_name}': {e}")
            
            print(f"👑 [DEBUG] {staff_encontradas}/{len(staff_roles)} roles de staff configuradas")
            
            # 6. CRIAR CANAL
            print("🛠️ [DEBUG] Criando canal de ticket...")
            
            # Preparar nome seguro
            nome_usuario = interaction.user.display_name
            nome_limpo = ''.join(c for c in nome_usuario if c.isalnum() or c in [' ', '-', '_', '.'])
            nome_limpo = nome_limpo.strip()
            
            if not nome_limpo or len(nome_limpo) < 2:
                nome_limpo = f"user-{interaction.user.id}"
            
            nome_canal = f"🎫-{nome_limpo[:25]}"
            print(f"📝 [DEBUG] Nome do canal: {nome_canal}")
            print(f"📝 [DEBUG] Tópico: Ticket de {interaction.user.name} | ID: {interaction.user.id}")
            
            try:
                ticket_channel = await interaction.guild.create_text_channel(
                    name=nome_canal,
                    category=categoria,
                    overwrites=overwrites,
                    topic=f"Ticket de {interaction.user.name} | ID: {interaction.user.id}",
                    reason=f"Ticket criado por {interaction.user.name} ({interaction.user.id})"
                )
                print(f"✅ [DEBUG] Canal criado com sucesso! #{ticket_channel.name}")
                print(f"   • ID: {ticket_channel.id}")
                print(f"   • Posição: {ticket_channel.position}")
                
            except discord.Forbidden as e:
                print(f"❌ [DEBUG] ERRO DE PERMISSÃO ao criar canal: {e}")
                raise
            except discord.HTTPException as e:
                print(f"❌ [DEBUG] ERRO HTTP ao criar canal: {e.status} - {e.text}")
                raise
            except Exception as e:
                print(f"❌ [DEBUG] ERRO DESCONHECIDO ao criar canal: {type(e).__name__}: {e}")
                raise
            
            # 7. ENVIAR MENSAGENS NO TICKET
            print("💬 [DEBUG] Enviando mensagens no ticket...")
            
            embed = discord.Embed(
                title=f"🎫 Ticket de {interaction.user.display_name}",
                description=(
                    f"**👤 Aberto por:** {interaction.user.mention}\n"
                    f"**🆔 ID:** `{interaction.user.id}`\n"
                    f"**📅 Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                    "**📝 Descreva seu problema ou dúvida abaixo:**"
                ),
                color=discord.Color.purple()
            )
            
            staff_view = TicketStaffView(interaction.user.id, ticket_channel)
            
            try:
                # Embed principal
                await ticket_channel.send(
                    content=f"## 👋 Olá {interaction.user.mention}!\nSeu ticket foi criado com sucesso.",
                    embed=embed
                )
                
                # Botões
                await ticket_channel.send("**🔧 Painel de Controle:**", view=staff_view)
                print("✅ [DEBUG] Mensagens enviadas no ticket")
                
            except Exception as e:
                print(f"⚠️ [DEBUG] Erro ao enviar mensagens: {e}")
                # Continua mesmo com erro nas mensagens
            
            # 8. NOTIFICAR STAFF
            print("🔔 [DEBUG] Notificando staff...")
            mention_roles = []
            for role_name in ["𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐒𝐮𝐛𝐥𝐢́𝐝𝐞𝐫", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫"]:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    mention_roles.append(role.mention)
            
            if mention_roles:
                try:
                    await ticket_channel.send(
                        f"{' '.join(mention_roles)}\n"
                        f"📬 **Novo ticket criado!**"
                    )
                    print(f"✅ [DEBUG] Staff notificado: {len(mention_roles)} roles mencionadas")
                except:
                    print("⚠️ [DEBUG] Não foi possível notificar staff")
            
            # 9. CONFIRMAR PARA O USUÁRIO
            print("📨 [DEBUG] Enviando confirmação para o usuário...")
            await interaction.followup.send(
                f"✅ **Ticket criado com sucesso!**\n"
                f"Acesse: {ticket_channel.mention}",
                ephemeral=True
            )
            
            print(f"🎉 [TICKET] Ticket criado com SUCESSO para {interaction.user.name}")
            print("="*60 + "\n")
            
        except discord.Forbidden as e:
            print(f"❌ [ERRO] PERMISSÃO NEGADA: {e}")
            print(f"❌ [ERRO] O bot não tem permissão para executar esta ação")
            await interaction.followup.send(
                "❌ **Erro de permissão!**\n"
                "O bot precisa das permissões:\n"
                "• Gerenciar Canais\n"
                "• Gerenciar Permissões\n"
                "• Gerenciar Mensagens",
                ephemeral=True
            )
            
        except discord.HTTPException as e:
            print(f"❌ [ERRO] HTTP {e.status}: {e.text}")
            await interaction.followup.send(
                f"❌ **Erro do Discord ({e.status}):**\n"
                f"Tente novamente em alguns instantes.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"❌ [ERRO] INESPERADO: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            
            await interaction.followup.send(
                f"❌ **Erro inesperado:**\n"
                f"`{type(e).__name__}: {str(e)[:150]}`",
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
        print(f"⚙️ [SETUP] Configurando painel de tickets por {ctx.author.name}")
        
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
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1462150327070359707/1462151759337361654/ChatGPT_Image_17_de_jan._de_2026_18_28_54.png?ex=696d2670&is=696bd4f0&hm=10fbb4366a6ba683e0b93a90e2cc7e2b67748dcbdacee8fde06a768050748bd5")
        embed.set_footer(text="Hospital APP • Suporte 24h")
        
        view = TicketOpenView()
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()
        
        print(f"✅ [SETUP] Painel de tickets configurado em #{ctx.channel.name}")
    
    @commands.command(name="ticket_info")
    @commands.has_permissions(administrator=True)
    async def ticket_info(self, ctx, channel: discord.TextChannel = None):
        """Mostra informações de um ticket"""
        if channel is None:
            channel = ctx.channel
        
        if not channel.name.startswith(("🎫-", "🔒-")):
            await ctx.send("❌ Este não é um canal de ticket!")
            return
        
        # Extrair informações
        user_id = None
        username = "Desconhecido"
        
        if channel.topic:
            match_id = re.search(r'ID:\s*(\d+)', channel.topic)
            if match_id:
                user_id = match_id.group(1)
            
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
        
        embed.add_field(name="📅 Criado em", value=channel.created_at.strftime('%d/%m/%Y %H:%M'), inline=True)
        embed.add_field(name="🔒 Status", value="Fechado" if channel.name.startswith("🔒-") else "Aberto", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="teste_ticket")
    async def teste_ticket(self, ctx):
        """Testa o sistema de tickets (apenas ADM)"""
        if not ctx.author.guild_permissions.administrator:
            return
        
        print(f"🧪 [TESTE] Teste iniciado por {ctx.author.name}")
        
        # Teste simples
        try:
            # Verificar permissões
            perms = ctx.guild.me.guild_permissions
            print(f"🧪 [TESTE] Permissões do bot:")
            print(f"  • Gerenciar Canais: {perms.manage_channels}")
            print(f"  • Gerenciar Permissões: {perms.manage_roles}")
            
            # Verificar se há canal ticket
            canal_ticket = None
            for channel in ctx.guild.text_channels:
                if "ticket" in channel.name.lower():
                    canal_ticket = channel
                    break
            
            if canal_ticket:
                print(f"🧪 [TESTE] Canal ticket encontrado: #{canal_ticket.name}")
            else:
                print("🧪 [TESTE] Nenhum canal ticket encontrado")
            
            await ctx.send(f"✅ Teste concluído! Verifique os logs do terminal.")
            
        except Exception as e:
            print(f"❌ [TESTE] Erro: {e}")
            await ctx.send(f"❌ Erro no teste: {e}")

async def setup(bot):
    """Configura o sistema de tickets"""
    await bot.add_cog(TicketsCog(bot))
    print("✅ Módulo de tickets carregado com DEBUG ATIVADO!")
    print("📋 Comandos disponíveis: !setup_tickets, !ticket_info, !teste_ticket")
