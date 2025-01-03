from typing import List

from discord import app_commands
import discord

from models.enums import Gender, Languages
from database.dto.psql_services import Services_Database


async def services_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice]:
    dto = Services_Database()
    tags = await dto.get_all_active_tags()
    response = [
        app_commands.Choice(name=tag, value=tag)
        for tag in tags if current.lower() in tag.lower()
    ]
    response.insert(0, app_commands.Choice(name="All", value="ALL"))
    return response


async def servers_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice]:
    server_choices = {
        "league of legends": [
            "All Servers", "EUW (Europe West)", "Eune (Europe Nordic & East)","NA (North America)", "CN (China)", "BR (Brazil)", 
            "LAN (Latin America North)", "LAS (Latin America South)", "OCE (Oceania)", "RU (Russia)", "TR (Turkey)", "JP (Japan)", 
            "KR (Republic of Korea)", "PH (The Philippines)", "SG (Singapore, Malaysia, & Indonesia)", "TW (Taiwan, Hong Kong, and Macao)",
            "TH (Thailand)", "VN (Vietnam)"
        ],
        "naraka: bladepoint": ["All Servers", "EU", "NA", "SEA", "CN(China)"],
        "cs:go": ["All Servers", "EU West", "EU East", "China", "Australia", "US North West", "US North East", "US North Central", "US South West", "US South East", "Brazil", "Chile", "Peru", "Poland", "Spain", "Japan", "India", "Mexico", "Argentine", "Colombia"],
        "apex legends": ["All Servers", "Europe", "North America", "South America", "Asia", "China", "Oceania", "MEA", "Korea", "SEA", "Japan"],
        "valorant": ["All Servers", "Europe", "Canada", "United States", "Turkey", "Russia", "OCE", "LAS", "BR", "LAN"],
        "overwatch2": ["All Servers", "EU", "NA", "KR", "CN", "ASIA"],
        "pubg": ["All Servers", "EU", "NA", "KR", "CN", "ASIA"],
        "fortnite": ["All Servers", "EU", "NA", "KR", "CN", "ASIA"],
        "teamfight tactic": ["All Servers", "EU", "NA", "KR", "CN", "ASIA"],
        "dota2": ["All Servers", "EU", "NA", "KR", "CN", "ASIA"],
        "world of tanks": ["All Servers", "EU", "NA", "KR", "CN", "ASIA"]
    }
    selected_service = interaction.namespace.choices
    available_servers = server_choices.get(
        selected_service.lower(),
        ["No available servers"]
    )
    return [
        app_commands.Choice(name=server, value=server)
        for server in available_servers if current.lower() in server.lower()
    ]

gender_options = [
    app_commands.Choice(name="Unimportant", value=Gender.UNIMPORTANT.value),
    app_commands.Choice(name="Female", value=Gender.FEMALE.value),
    app_commands.Choice(name="Male", value=Gender.MALE.value),
]

language_options = [
    app_commands.Choice(name="Unimportant", value=Languages.UNIMPORTANT.value),
    app_commands.Choice(name="Russian", value=Languages.RU.value),
    app_commands.Choice(name="English", value=Languages.EN.value),
    app_commands.Choice(name="Spanish", value=Languages.ES.value),
    app_commands.Choice(name="French", value=Languages.FR.value),
    app_commands.Choice(name="German", value=Languages.DE.value),
    app_commands.Choice(name="Italian", value=Languages.IT.value),
    app_commands.Choice(name="Portuguese", value=Languages.PT.value),
    app_commands.Choice(name="Chinese", value=Languages.ZH.value),
    app_commands.Choice(name="Japanese", value=Languages.JA.value),
    app_commands.Choice(name="Korean", value=Languages.KO.value),
    app_commands.Choice(name="Arabic", value=Languages.AR.value),
    app_commands.Choice(name="Hindi", value=Languages.HI.value),
    app_commands.Choice(name="Turkish", value=Languages.TR.value),
    app_commands.Choice(name="Persian", value=Languages.FA.value),
]
