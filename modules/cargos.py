import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import asyncio
from datetime import datetime

# ========== CARREGAR OS CARGO ==========

class CargoSelectView(ui.View):
    """View com dropdown para selecionar cargo"""
    def __init__(self, target_member, action="add"):
        super().__init__(timeout=60)
        self.target_member = target_member
        self.action = action  # "add" ou "remove"
        self.add_item(CargoSelectDropdown(target_member, action))

class CargoSelectDropdown(ui.Select):
    def __init__(self, target_member, action="add"):
        self.target_member = target_member
        self.action = action
        
        # Definir cargos disponíveis
        options = [
            discord.SelectOption(label="𝐀𝐯𝐢𝐚̃𝐨𝐳𝐢𝐧𝐡𝐨", description="Cargo inicial", emoji="🛬"),
            discord.SelectOption(label="𝐌𝐞𝐦𝐛𝐫𝐨", description="Membro do servidor", emoji="👤"),
            discord.SelectOption(label="𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", description="Recrutador", emoji="📢"),
            discord.SelectOption(label="𝐀𝐃𝐌", description="Administrador", emoji="👑"),
            discord.SelectOption(label="𝐆𝐞𝐫𝐞𝐧𝐭𝐞", description="Gerente", emoji="💼"),
            discord.SelectOption(label="00 🐐", description="Dono", emoji="🐐"),
        ]
        
        super().__init__(
            placeholder="Selecione um cargo...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="cargo_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.followup.send("❌ Apenas staff pode gerenciar cargos!", ephemeral=True)
            return
        
        cargo_nome = self.values[0]
        cargo = discord.utils.get(interaction.guild.roles, name=cargo_nome)
        
        if not cargo:
            await interaction.followup.send(f"❌ Cargo `{cargo_nome}` não encontrado!", ephemeral=True)
            return
        
        try:
            if self.action == "add":
                await self.target_member.add_roles(cargo)
                mensagem = f"✅ Cargo `{cargo.name}` adicionado para {self.target_member.mention}!"
                cor = discord.Color.green()
            else:
                await self.target_member.remove_roles(cargo)
                mensagem = f"✅ Cargo `{cargo.name}` removido de {self.target_member.mention}!"
                cor = discord.Color.orange()
            
            # Embed de confirmação
            embed = discord.Embed(
                title=f"⚙️ Cargo {'Adicionado' if self.action == 'add' else 'Removido'}",
                description=mensagem,
                color=cor
            )
            embed.add_field(name="👤 Usuário", value=self.target_member.mention, inline=True)
            embed.add_field(name="🎯 Cargo", value=cargo.mention, inline=True)
            embed.add_field(name="👑 Staff", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            # Enviar no canal
            await interaction.channel.send(embed=embed)
            
            # Confirmação privada
            await interaction.followup.send(f"✅ Operação realizada!", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ Não tenho permissão para gerenciar cargos!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

# ========== PAINEL PRINCIPAL ==========

class CargoPanelView(ui.View):
    """View principal do painel de cargos"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="➕ Adicionar Cargo", style=ButtonStyle.green, emoji="➕", custom_id="add_cargo")
    async def add_cargo(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode adicionar cargos!", ephemeral=True)
            return
        
        # Modal para digitar nome do usuário
        modal = AddCargoModal()
        await interaction.response.send_modal(modal)
    
    @ui.button(label="➖ Remover Cargo", style=ButtonStyle.red, emoji="➖", custom_id="remove_cargo")
    async def remove_cargo(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode remover cargos!", ephemeral=True)
            return
        
        modal = RemoveCargoModal()
        await interaction.response.send_modal(modal)
    
    @ui.button(label="📋 Ver Cargos", style=ButtonStyle.blurple, emoji="📋", custom_id="view_cargos")
    async def view_cargos(self, interaction: discord.Interaction, button: ui.Button):
        staff_roles = ["00 🐐", "𝐆𝐞𝐫𝐞𝐧𝐭𝐞", "𝐀𝐃𝐌", "𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫", "Dono", "Owner"]
        if not any(role.name in staff_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Apenas staff pode ver cargos!", ephemeral=True)
            return
        
        modal = ViewCargosModal()
        await interaction.response.send_modal(modal)

class AddCargoModal(ui.Modal, title="➕ Adicionar Cargo"):
    """Modal para adicionar cargo"""
    
    usuario = ui.TextInput(
        label="Nome ou ID do usuário:",
        placeholder="Ex: @Gabzimm ou 123456789012345678",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Tentar encontrar usuário
            member = None
            
            # Se for mencionação
            if "<@" in self.usuario.value:
                user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                member = interaction.guild.get_member(int(user_id))
            
            # Se for ID numérico
            elif self.usuario.value.isdigit():
                member = interaction.guild.get_member(int(self.usuario.value))
            
            # Se for nome
            else:
                # Buscar por nome
                for guild_member in interaction.guild.members:
                    if self.usuario.value.lower() in guild_member.name.lower():
                        member = guild_member
                        break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            # Mostrar dropdown para selecionar cargo
            view = CargoSelectView(member, action="add")
            
            embed = discord.Embed(
                title="🎯 Selecione o Cargo",
                description=f"Usuário: {member.mention}\nAção: **Adicionar Cargo**",
                color=discord.Color.blue()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

class RemoveCargoModal(ui.Modal, title="➖ Remover Cargo"):
    """Modal para remover cargo"""
    
    usuario = ui.TextInput(
        label="Nome ou ID do usuário:",
        placeholder="Ex: @Gabzimm ou 123456789012345678",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Tentar encontrar usuário
            member = None
            
            if "<@" in self.usuario.value:
                user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                member = interaction.guild.get_member(int(user_id))
            elif self.usuario.value.isdigit():
                member = interaction.guild.get_member(int(self.usuario.value))
            else:
                for guild_member in interaction.guild.members:
                    if self.usuario.value.lower() in guild_member.name.lower():
                        member = guild_member
                        break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            # Mostrar dropdown para remover cargo
            view = CargoSelectView(member, action="remove")
            
            embed = discord.Embed(
                title="🎯 Selecione o Cargo",
                description=f"Usuário: {member.mention}\nAção: **Remover Cargo**",
                color=discord.Color.orange()
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

class ViewCargosModal(ui.Modal, title="📋 Ver Cargos do Usuário"):
    """Modal para ver cargos de um usuário"""
    
    usuario = ui.TextInput(
        label="Nome ou ID do usuário:",
        placeholder="Ex: @Gabzimm ou 123456789012345678",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Tentar encontrar usuário
            member = None
            
            if "<@" in self.usuario.value:
                user_id = self.usuario.value.replace("<@", "").replace(">", "").replace("!", "")
                member = interaction.guild.get_member(int(user_id))
            elif self.usuario.value.isdigit():
                member = interaction.guild.get_member(int(self.usuario.value))
            else:
                for guild_member in interaction.guild.members:
                    if self.usuario.value.lower() in guild_member.name.lower():
                        member = guild_member
                        break
            
            if not member:
                await interaction.followup.send(f"❌ Usuário `{self.usuario.value}` não encontrado!", ephemeral=True)
                return
            
            # Criar embed com cargos
            cargos = [role.mention for role in member.roles if role.name != "@everyone"]
            
            embed = discord.Embed(
                title=f"📋 Cargos de {member.name}",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            
            if cargos:
                embed.description = "\n".join(cargos)
                embed.add_field(name="Total de Cargos", value=str(len(cargos)), inline=True)
            else:
                embed.description = "Nenhum cargo além do @everyone"
            
            embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
            embed.add_field(name="📅 Entrou em", value=member.joined_at.strftime('%d/%m/%Y'), inline=True)
            embed.set_footer(text=f"Solicitado por: {interaction.user.name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

# ========== COMANDOS ==========

class CargosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Módulo de Cargos carregado!")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_cargos(self, ctx):
        """Configura o painel de gerenciamento de cargos"""
        
        embed = discord.Embed(
            title="⚙️ **PAINEL DE GERENCIAMENTO DE CARGOS**",
            description=(
                "**Funcionalidades disponíveis:**\n\n"
                "➕ **Adicionar Cargo** - Adiciona um cargo a um usuário\n"
                "➖ **Remover Cargo** - Remove um cargo de um usuário\n"
                "📋 **Ver Cargos** - Mostra todos os cargos de um usuário\n\n"
                "**📌 Como usar:**\n"
                "1. Clique em uma das opções acima\n"
                "2. Digite o nome/ID do usuário\n"
                "3. Selecione o cargo desejado\n"
                "✅ Pronto! O cargo será atribuído automaticamente"
            ),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="⚠️ Apenas Staff",
            value="Este painel é restrito para:\n• 00 🐐\n• 𝐆𝐞𝐫𝐞𝐧𝐭𝐞\n• 𝐀𝐃𝐌\n• 𝐑𝐞𝐜𝐫𝐮𝐭𝐚𝐝𝐨𝐫\n• Dono\n• Owner",
            inline=False
        )
        
        embed.set_footer(text="Sistema automático de cargos • Clique nos botões acima")
        
        view = CargoPanelView()
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_cargo(self, ctx, member: discord.Member, *, cargo_nome: str):
        """Adiciona um cargo a um usuário via comando"""
        cargo = discord.utils.get(ctx.guild.roles, name=cargo_nome)
        
        if not cargo:
            await ctx.send(f"❌ Cargo `{cargo_nome}` não encontrado!")
            return
        
        try:
            await member.add_roles(cargo)
            embed = discord.Embed(
                title="✅ Cargo Adicionado",
                description=f"Cargo `{cargo.name}` adicionado para {member.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_cargo(self, ctx, member: discord.Member, *, cargo_nome: str):
        """Remove um cargo de um usuário via comando"""
        cargo = discord.utils.get(ctx.guild.roles, name=cargo_nome)
        
        if not cargo:
            await ctx.send(f"❌ Cargo `{cargo_nome}` não encontrado!")
            return
        
        try:
            await member.remove_roles(cargo)
            embed = discord.Embed(
                title="✅ Cargo Removido",
                description=f"Cargo `{cargo.name}` removido de {member.mention}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

async def setup(bot):
    await bot.add_cog(CargosCog(bot))
    print("✅ Sistema de Cargos configurado!")
