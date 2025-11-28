from app.services.client import PanelClient

class InternalSquadsService:
    def __init__(self):
        self.client = PanelClient()

    async def get_internal_squads(self):
        """
        Получает список внутренних сквадов панели.
        """
        
        return await self.client.request("GET", "/api/internal-squads")