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
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
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
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
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
        
        # Embed de reabertura
        embed = discord.Embed(
            title="🔄 Ticket Reaberto",
            description=f"Ticket reaberto por {interaction.user.mention}",
            color=discord.Color.blue()
        )
        
        # Remover botões
        self.clear_items()
        await interaction.message.edit(view=self)
        
        await self.ticket_channel.send(embed=embed)
        
       

class TicketStaffView(ui.View):
    """View com TODOS os botões para staff - Fechar, Deletar e Assumir lado a lado"""
    def __init__(self, ticket_owner_id, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id
        self.ticket_channel = ticket_channel
    
    @ui.button(label="✅ Assumir Ticket", style=ButtonStyle.green, emoji="👋", custom_id="assumir_ticket", row=0)
    async def assumir_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # APENAS STAFF pode assumir
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode assumir tickets!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Adicionar staff ao ticket
        overwrite = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            attach_files=True
        )
        await self.ticket_channel.set_permissions(interaction.user, overwrite=overwrite)
        
        # Mudar nome do canal para mostrar quem está atendendo
        novo_nome = f"🎫-{self.ticket_channel.name[2:]}+{interaction.user.name[:5]}"
        await self.ticket_channel.edit(name=novo_nome)
        
        # Embed de confirmação
        embed = discord.Embed(
            title="👑 Ticket Assumido",
            description=f"**{interaction.user.mention}** assumiu este ticket!",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Staff responsável: {interaction.user.name}")
        
        # Remover botão "Assumir" (já foi assumido)
        for child in self.children:
            if child.custom_id == "assumir_ticket":
                self.remove_item(child)
                break
        
        await interaction.message.edit(view=self)
        
        await self.ticket_channel.send(embed=embed)
        
        # DM para o usuário
        try:
            user = await interaction.client.fetch_user(self.ticket_owner_id)
            await user.send(f"👋 **{interaction.user.name}** assumiu seu ticket!")
        except:
            pass
    
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
        
        # CRIAR NOVO PAINEL DE TICKET FECHADO (APENAS STAFF VÊ)
        # Buscar informações do usuário
        try:
            user = await interaction.client.fetch_user(self.ticket_owner_id)
            user_info = f"{user.mention}\nID: `{user.id}`"
        except:
            user_info = f"ID: `{self.ticket_owner_id}`"
        
        # Embed do ticket fechado
        embed_fechado = discord.Embed(
            title="📋 Ticket Fechado",
            description=(
                f"**👤 Usuário:** {user_info}\n"
                f"**👑 Fechado por:** {interaction.user.mention}\n"
                f"**📅 Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                "**Painel de Controle (apenas staff):**"
            ),
            color=discord.Color.orange()
        )
        
        # View com botões de finalizar/reabrir (APENAS STAFF VÊ)
        finalizado_view = TicketFinalizadoView(self.ticket_owner_id, self.ticket_channel)
        
        await self.ticket_channel.send(embed=embed_fechado, view=finalizado_view)
        
        
    
    @ui.button(label="🗑️ Deletar Ticket", style=ButtonStyle.red, emoji="🗑️", custom_id="delete_ticket_staff", row=0)
    async def delete_ticket_staff(self, interaction: discord.Interaction, button: ui.Button):
        # APENAS STAFF pode deletar
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
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
        await interaction.response.defer(ephemeral=True)
        
        try:
            # ENCONTRAR CANAL "𝐓𝐢𝐜𝐤𝐞𝐭-🎟️"
            canal_ticket_base = None
            for channel in interaction.guild.text_channels:
                if "𝐓𝐢𝐜𝐤𝐞𝐭" in channel.name.lower() and "🎟️" in channel.name:
                    canal_ticket_base = channel
                    break
            
            if not canal_ticket_base:
                await interaction.followup.send("❌ Canal '𝐓𝐢𝐜𝐤𝐞𝐭-🎟️' não encontrado!", ephemeral=True)
                return
            
            # Verificar se já tem ticket aberto
            categoria = canal_ticket_base.category
            if categoria:
                for channel in categoria.channels:
                    if str(interaction.user.id) in (channel.topic or ""):
                        await interaction.followup.send(
                            f"❌ Você já tem um ticket aberto: {channel.mention}",
                            ephemeral=True
                        )
                        return
            
            # Usar a MESMA categoria
            if not categoria:
                await interaction.followup.send("❌ Canal não está em uma categoria!", ephemeral=True)
                return
            
            # Encontrar posição para colocar ABAIXO do "𝐓𝐢𝐜𝐤𝐞𝐭-🎟️"
            canais_na_categoria = list(categoria.channels)
            canais_na_categoria.sort(key=lambda x: x.position)
            
            posicao = 0
            for canal in canais_na_categoria:
                if canal.id == canal_ticket_base.id:
                    posicao = canal.position + 1
                    break
            
            # Permissões iniciais
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # Adicionar staff roles para ver botões
            staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
            for role_name in staff_roles:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
            
            # Criar canal
            ticket_channel = await interaction.guild.create_text_channel(
                name=f"🎫-{interaction.user.name}",
                category=categoria,
                overwrites=overwrites,
                topic=f"Ticket de {interaction.user.name} | ID: {interaction.user.id}",
                position=posicao if posicao > 0 else None
            )
            
            # Embed inicial
            embed = discord.Embed(
                title=f"🎫 Ticket de {interaction.user.display_name}",
                description=(
                    f"**Aberto por:** {interaction.user.mention}\n"
                    f"**ID:** `{interaction.user.id}`\n"
                    f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                    "**📝 Descreva seu problema ou dúvida:**\n"
                    "Aguarde um membro da staff assumir seu ticket."
                ),
                color=discord.Color.purple()
            )
            
            # View com TODOS os botões para staff
            staff_view = TicketStaffView(interaction.user.id, ticket_channel)
            
            await ticket_channel.send(
                content=f"{interaction.user.mention} **Ticket criado!**",
                embed=embed,
                view=staff_view
            )
            
            # Confirmação
            msg = await interaction.followup.send(
                f"✅ Ticket criado: {ticket_channel.mention}",
                ephemeral=True
            )
            
            await asyncio.sleep(10)
            try:
                await msg.delete()
            except:
                pass
            
            print(f"🎫 Ticket criado: {ticket_channel.name}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            await interaction.followup.send("❌ Erro ao criar ticket!", ephemeral=True)

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
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1460384061045608680/1460728997800448293/ChatGPT_Image_13_de_jan._de_2026_20_15_27.png")
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
