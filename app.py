import os
import random
import base64
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import httpx
import asyncio
from typing import Dict, Any, Optional, List, Tuple

# ==================== গোপন কনফিগারেশন ====================
class HiddenConfig:
    """সব সেনসিটিভ ডাটা লুকানো আছে"""
    
    @staticmethod
    def _char_code_generator(codes: List[int]) -> str:
        """ক্যারেক্টার কোড থেকে স্ট্রিং জেনারেট"""
        return ''.join(chr(code) for code in codes)
    
    @classmethod
    def get_api_url(cls) -> str:
        """টার্গেট API URL রিটার্ন করে - সম্পূর্ণ লুকানো"""
        # FF LIKE
        encoded = "aHR0cHM6Ly9pbmZvLWFwaS1tZzI0LXByby52ZXJjZWwuYXBw"
        decoded = base64.b64decode(encoded).decode()
        return f"{decoded}/get?uid={{}}"
    
    @classmethod
    def get_credit(cls) -> str:
        """ক্রেডিট সোর্স রিটার্ন করে - NURROSUL"""
        return cls._char_code_generator([78, 85, 82, 82, 79, 83, 85, 76])
    
    @classmethod
    def get_like_values(cls) -> List[int]:
        """লাইক ভ্যালু রিটার্ন করে - [193, 194, 195, 200]"""
        base = 190
        return [base + 3, base + 4, base + 5, base + 10]

# ==================== কনফিগ ইনিশিয়ালাইজ ====================
HIDDEN_API_URL = HiddenConfig.get_api_url()
HIDDEN_CREDIT = HiddenConfig.get_credit()
HIDDEN_LIKE_VALUES = HiddenConfig.get_like_values()

# ==================== ডাটা মডেল ====================
class PlayerData:
    """প্লেয়ার ডাটা মডেল"""
    def __init__(self, uid: str, server: str, nickname: str, likes_before: int, likes_given: int):
        self.uid = uid
        self.server = server  # ইউজার যেটা দিবে সেটাই থাকবে
        self.nickname = nickname
        self.likes_before = likes_before
        self.likes_given = likes_given
        self.likes_after = likes_before + likes_given
    
    def to_dict(self) -> Dict[str, Any]:
        """শুধু প্রয়োজনীয় ফিল্ড রিটার্ন করে"""
        return {
            "LikesGivenByAPI": self.likes_given,
            "LikesafterCommand": self.likes_after,
            "LikesbeforeCommand": self.likes_before,
            "PlayerNickname": self.nickname,
            "UID": self.uid,
            "server": self.server,  # ইউজারের দেওয়া server প্যারামিটার
            "source": HIDDEN_CREDIT,
            "status": 1
        }

class ErrorResponse:
    """এরর রেসপন্স মডেল"""
    @staticmethod
    def create(message: str, status_code: int = 400) -> Dict[str, Any]:
        return {
            "status": 0,
            "error": message,
            "source": HIDDEN_CREDIT,
            "code": status_code
        }

# ==================== API ফাংশন ====================
class LikeAPI:
    """মেইন API ক্লাস"""
    
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
    
    async def fetch_player_data(self, uid: str) -> Optional[Dict[str, Any]]:
        """প্লেয়ার ডাটা ফেচ করে"""
        try:
            target_url = https://shiv-m-elite-info-bot-all-server.vercel.app.format(uid)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(target_url)
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            return {"error": "timeout"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "not_found"}
            return {"error": "http_error"}
        except Exception:
            return {"error": "unknown"}
    
    def extract_player_info(self, data: Dict[str, Any]) -> Tuple[str, int]:
        """প্লেয়ার ইনফো এক্সট্র্যাক্ট করে"""
        account_info = data.get("AccountInfo", {})
        nickname = account_info.get("AccountName", "Unknown Player")
        likes = account_info.get("AccountLikes", 0)
        return nickname, likes
    
    def generate_likes(self) -> int:
        """র্যান্ডম লাইক জেনারেট করে"""
        return random.choice(HIDDEN_LIKE_VALUES)
    
    def validate_uid(self, uid: str) -> bool:
        """UID ভ্যালিডেশন"""
        if not uid:
            return False
        if len(uid) > 20:
            return False
        if not uid.isdigit():
            return False
        return True
    
    async def process_request(self, uid: str, server: str) -> Dict[str, Any]:
        """রিকোয়েস্ট প্রসেস করে"""
        self.request_count += 1
        
        # UID ভ্যালিডেশন
        if not self.validate_uid(uid):
            self.error_count += 1
            return ErrorResponse.create("Invalid UID format", 400)
        
        # প্লেয়ার ডাটা ফেচ
        player_data = await self.fetch_player_data(uid)
        
        if not player_data:
            self.error_count += 1
            return ErrorResponse.create("Player not found", 404)
        
        if isinstance(player_data, dict) and "error" in player_data:
            self.error_count += 1
            error_msg = {
                "timeout": "Service timeout",
                "not_found": "Player not found",
                "http_error": "Service unavailable",
                "unknown": "Unknown error"
            }.get(player_data["error"], "Unknown error")
            
            status_code = 503 if player_data["error"] == "timeout" else 404
            return ErrorResponse.create(error_msg, status_code)
        
        # ইনফো এক্সট্র্যাক্ট
        nickname, likes_before = self.extract_player_info(player_data)
        
        # লাইক জেনারেট
        likes_given = self.generate_likes()
        
        # প্লেয়ার ডাটা তৈরি (শুধু প্রয়োজনীয় ফিল্ড)
        player = PlayerData(uid, server, nickname, likes_before, likes_given)
        
        self.success_count += 1
        return player.to_dict()
    
    def get_stats(self) -> Dict[str, Any]:
        """API স্ট্যাটাস রিটার্ন করে"""
        total = max(self.request_count, 1)
        return {
            "total_requests": self.request_count,
            "successful": self.success_count,
            "failed": self.error_count,
            "success_rate": f"{(self.success_count / total) * 100:.1f}%",
            "source": HIDDEN_CREDIT
        }

# ==================== গ্লোবাল API ইনস্ট্যান্স ====================
like_api = LikeAPI()

# ==================== Vercel হ্যান্ডলার ====================
class handler(BaseHTTPRequestHandler):
    """Vercel হ্যান্ডলার"""
    
    def do_GET(self):
        """GET রিকোয়েস্ট হ্যান্ডল করে"""
        
        # URL পার্স
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # CORS হেডার
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # রুট এন্ডপয়েন্ট
        if path == "/" or path == "":
            response = {
                "message": "Like API is running",
                "endpoints": {
                    "/like": "GET with ?uid={uid}&server={server}",
                    "/stats": "GET - API statistics"
                },
                "source": HIDDEN_CREDIT,
                "status": "active"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
        # স্ট্যাটাস এন্ডপয়েন্ট
        if path == "/stats":
            response = like_api.get_stats()
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
        # লাইক এন্ডপয়েন্ট
        if path == "/like":
            uid = query_params.get('uid', [''])[0]
            server = query_params.get('server', [''])[0]
            
            if not uid or not server:
                error_response = ErrorResponse.create("Missing uid or server parameter", 400)
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # অ্যাসিঙ্ক রান
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(like_api.process_request(uid, server))
            loop.close()
            
            self.wfile.write(json.dumps(result, indent=2).encode())
            return
        
        # 404 - নট ফাউন্ড
        self.send_response(404)
        error_response = ErrorResponse.create("Endpoint not found", 404)
        self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """OPTIONS রিকোয়েস্ট হ্যান্ডল করে"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def log_message(self, format, *args):
        """লগিং ডিসেবল"""
        return

# ==================== লোকাল টেস্টিং ====================
def run_local_server(port=8000):
    """লোকাল সার্ভার চালানোর জন্য"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, handler)
    print(f"🚀 লোকাল সার্ভার চলছে http://localhost:{port}/ এ")
    print(f"📝 টেস্ট করুন: http://localhost:{port}/like?uid=1967182359&server=BD")
    print(f"📝 টেস্ট করুন: http://localhost:{port}/like?uid=1967182359&server=IN")
    print(f"📝 টেস্ট করুন: http://localhost:{port}/like?uid=1967182359&server=US")
    print("⏹️ বন্ধ করতে Ctrl+C প্রেস করুন")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 সার্ভার বন্ধ করা হচ্ছে...")
        httpd.shutdown()

# ==================== মেইন ফাংশন ====================
if __name__ == "__main__":
    """এই ফাইল সরাসরি রান করলে লোকাল সার্ভার চালু হবে"""
    print("=" * 50)
    print("🤖 Like API - লোকাল টেস্টিং মোড")
    print("=" * 50)
    print(f"🔑 ক্রেডিট: {HIDDEN_CREDIT}")
    print(f"📊 লাইক ভ্যালু: {HIDDEN_LIKE_VALUES}")
    print("=" * 50)
    
    # পোর্ট 8000 এ লোকাল সার্ভার চালু করুন
    run_local_server(8000)
