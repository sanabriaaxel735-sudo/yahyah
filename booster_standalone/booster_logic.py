import httpx
import asyncio
import json
import re
from concurrent.futures import ThreadPoolExecutor

class DiscordBooster:
    BASE_URL = "https://discord.com/api/v9"

    def __init__(self, token: str, proxy: str = None):
        self.token = token
        self.proxy = proxy
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def get_user_info(self):
        async with httpx.AsyncClient(proxies=self.proxy) as client:
            try:
                response = await client.get(f"{self.BASE_URL}/users/@me", headers=self.headers)
                if response.status_code == 200:
                    return response.json()
            except: pass
            return None

    async def watermark(self, username=None, bio=None):
        """Update profile settings (Watermarking)"""
        async with httpx.AsyncClient(proxies=self.proxy) as client:
            payload = {}
            if username: payload["username"] = username
            if bio: payload["bio"] = bio
            
            response = await client.patch(f"{self.BASE_URL}/users/@me", headers=self.headers, json=payload)
            return response.status_code == 200

    async def join_server(self, invite_code: str):
        invite_code = invite_code.split("/")[-1]
        async with httpx.AsyncClient(proxies=self.proxy) as client:
            try:
                response = await client.post(f"{self.BASE_URL}/invites/{invite_code}", headers=self.headers, json={})
                if response.status_code in [200, 201]:
                    return response.json()
            except: pass
            return None

    async def get_boost_slots(self):
        async with httpx.AsyncClient(proxies=self.proxy) as client:
            try:
                response = await client.get(f"{self.BASE_URL}/users/@me/guild-boosts", headers=self.headers)
                if response.status_code == 200:
                    return response.json()
            except: pass
            return []

    async def apply_boosts(self, guild_id: str, slot_ids: list):
        async with httpx.AsyncClient(proxies=self.proxy) as client:
            payload = {
                "user_premium_guild_subscription_slot_ids": slot_ids,
                "disable_powerup_auto_apply": False
            }
            try:
                response = await client.put(
                    f"{self.BASE_URL}/guilds/{guild_id}/premium/subscriptions",
                    headers=self.headers,
                    json=payload
                )
                return response.status_code in [200, 201, 204], response.text
            except Exception as e:
                return False, str(e)

async def boost_with_token(token, invite_code, watermark_bio=None):
    booster = DiscordBooster(token)
    
    user = await booster.get_user_info()
    if not user:
        return {"success": False, "message": "Invalid token"}

    # Optional Watermark
    if watermark_bio:
        await booster.watermark(bio=watermark_bio)

    join_res = await booster.join_server(invite_code)
    if not join_res:
        return {"success": False, "message": f"Failed to join server with {user['username']}"}
    
    guild_id = join_res['guild']['id']

    slots = await booster.get_boost_slots()
    available_slots = [s['id'] for s in slots if not s.get('premium_guild_subscription')]
    
    if not available_slots:
        return {"success": False, "message": f"No available boosts on {user['username']}"}

    success, detail = await booster.apply_boosts(guild_id, available_slots)
    if success:
        return {"success": True, "message": f"Successfully boosted with {user['username']}! ({len(available_slots)} boosts)"}
    else:
        return {"success": False, "message": f"Failed to boost with {user['username']}: {detail}"}

async def multi_boost(tokens, invite_code, watermark_bio=None):
    """Boost with multiple tokens in parallel"""
    tasks = [boost_with_token(token, invite_code, watermark_bio) for token in tokens]
    return await asyncio.gather(*tasks)
