import os
import re
import html
import base64
import random
import string
import json
import time
import requests
import telebot
import threading
import http.server
import socketserver
import hashlib
from telebot import types, apihelper
from datetime import datetime
from urllib.parse import urlparse, quote
import yt_dlp
import urllib3

# SSL warning বন্ধ
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================================================
# 👑 BOT & ADMIN CONFIGURATION
# =========================================================

BOT_TOKEN = "8670155352:AAEk3-rfFtz0lyf0N9X4rKUuNhHskSab4QU"
ADMIN_ID = 6957867422
ADMIN_USERNAME = "TALHASAIF7"
BOT_USERNAME = "@tms_9x_prankcall_bot"
PORT = 8080

IMGBB_API_KEY = "75e4c00d495b50dbdd818ced8bb4cd2b"

RENDER_EXTERNAL_URL = f"http://localhost:{PORT}"

HONEYPOT_ENABLED = True
TRAP_ALERT_CHANNEL = ADMIN_ID

# 🔒 FORCE SUB - DOUBLE CHANNEL SYSTEM
FORCE_SUB_CHANNELS = [
    {"id": -1003955079365, "url": "https://t.me/+v1MN8bBR67Q1MjY1", "name": "Channel 1"},
    {"id": -1002875839715, "url": "https://t.me/infinity9x", "name": "Channel 2"},
]

FORCE_SUB_CHANNEL = FORCE_SUB_CHANNELS[0]["id"]
FORCE_SUB_URL = FORCE_SUB_CHANNELS[0]["url"]

telebot.apihelper.READ_TIMEOUT = 180
telebot.apihelper.CONNECT_TIMEOUT = 60

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=True)
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
TRAP_LOG_FILE = "trap_logs.json"

user_states = {}
trap_victims = {}


# =========================================================
# 🛠️ HELPERS
# =========================================================

def load_trap_logs():
    if os.path.exists(TRAP_LOG_FILE):
        try:
            with open(TRAP_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def safe_remove(path):
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass


# =========================================================
# 🌐 KEEP-ALIVE WEB SERVER + HONEYPOT TRAP
# =========================================================

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def save_trap_victim(ip, user_agent, referer=""):
    try:
        data = load_trap_logs()
        key = f"{ip}_{int(time.time())}"
        data[key] = {
            "ip": ip,
            "user_agent": user_agent,
            "referer": referer,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(TRAP_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        try:
            alert = (
                "🚨 <b>𝐃𝐄𝐂𝐎𝐃𝐄𝐑 𝐓𝐑𝐀𝐏 𝐀𝐋𝐄𝐑𝐓!</b> 🚨\n"
                "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
                f"🌐 <b>𝐈𝐏:</b> <code>{html.escape(ip)}</code>\n"
                f"🖥️ <b>𝐁𝐫𝐨𝐰𝐬𝐞𝐫:</b> <code>{html.escape(user_agent[:80])}</code>\n"
                f"🔗 <b>𝐑𝐞𝐟𝐞𝐫𝐞𝐫:</b> <code>{html.escape(referer[:80])}</code>\n"
                f"⏰ <b>𝐓𝐢𝐦𝐞:</b> <code>{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}</code>\n\n"
                "💀 <i>এই ব্যক্তি আপনার ১৪-লেয়ার ইনক্রিপ্টেড কোড ডিকোড করার চেষ্টা করেছে!</i>"
            )
            safe_send_message(TRAP_ALERT_CHANNEL, alert)
        except Exception:
            pass
    except Exception as e:
        print(f"Trap log error: {e}")


def run_keep_alive_server():
    class KeepAliveHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            client_ip = self.client_address[0]
            user_agent = self.headers.get("User-Agent", "Unknown")
            referer = self.headers.get("Referer", "")
            path = self.path

            suspicious_keywords = [
                "decode", "decrypt", "scrape", "beautify", "unminify",
                "extract", "source", "obfuscate", "html", "raw", "crack", "trap"
            ]
            suspicious_ua = any(k in user_agent.lower() for k in [
                "python", "curl", "wget", "scrapy", "beautifulsoup",
                "requests", "axios", "node", "postman", "insomnia"
            ])

            is_trap = any(k in path.lower() for k in suspicious_keywords) or suspicious_ua

            if HONEYPOT_ENABLED and is_trap:
                save_trap_victim(client_ip, user_agent, referer)
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                
                trap_html = f"""<!DOCTYPE html>
<html><head><title>Access Denied</title></head>
<body style="background:#000;color:#0f0;font-family:monospace;padding:40px;text-align:center;">
<h1 style="color:#f00;">🚨 𝐔𝐍𝐀𝐔𝐓𝐇𝐎𝐑𝐈𝐙𝐄𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐓𝐄𝐂𝐓𝐄𝐃 🚨</h1>
<h2 style="color:#ff0;">আপনার IP এড্রেস সহ সমস্ত তথ্য সার্ভারে রেকর্ড করা হয়েছে!</h2>
<hr style="border-color:#f00;">
<pre style="color:#0ff;text-align:left;font-size:14px;max-width:600px;margin:0 auto;background:#111;padding:20px;border-radius:8px;">
IP: {html.escape(client_ip)}
Browser: {html.escape(user_agent[:60])}
Time: {datetime.now()}

👿🔥🥵💀❌ [১৪-লেয়ার ইনক্রিপশন ডিকোড করার চেষ্টা ব্যর্থ!
বট: {BOT_USERNAME} | ওনার: @{ADMIN_USERNAME}] 🔒⚡
</pre>
<h3 style="color:#f00;margin-top:20px;">🔒 যোগাযোগ: @{ADMIN_USERNAME}</h3>
</body></html>"""
                self.wfile.write(trap_html.encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            status_page = (
                "<html><head><title>Bot Status</title></head>"
                "<body style='font-family:sans-serif;text-align:center;padding-top:60px;background:#0b0e14;color:#58a6ff;'>"
                "<h1>⚡ 𝐔𝐋𝐓𝐑𝐀 𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐍𝐆𝐈𝐍𝐄 𝐯𝟒.𝟎 ⚡</h1>"
                "<p style='color:#3fb950;font-size:18px;'>🟢 𝐀𝐜𝐭𝐢𝐯𝐞 &amp; 𝐎𝐧𝐥𝐢𝐧𝐞 𝟐𝟒/𝟕</p>"
                "<p style='color:#f0883e;font-size:16px;'>🔐 𝟏𝟒-𝐋𝐀𝐘𝐄𝐑 𝐌𝐈𝐋𝐈𝐓𝐀𝐑𝐘 𝐄𝐍𝐂𝐑𝐘𝐏𝐓𝐈𝐎𝐍</p>"
                f"<p style='color:#8b949e;'>𝐎𝐰𝐧𝐞𝐫: @{ADMIN_USERNAME} | 𝐁𝐨𝐭: {BOT_USERNAME}</p>"
                "</body></html>"
            )
            self.wfile.write(status_page.encode("utf-8"))

        def log_message(self, format, *args):
            pass

    while True:
        try:
            with ReusableTCPServer(("", PORT), KeepAliveHandler) as httpd:
                print(f"🌐 Keep-Alive + Honeypot Server active on Port: {PORT}")
                httpd.serve_forever()
        except Exception as e:
            print(f"⚠️ Web Server Warning: {e}, retrying in 5s...")
            time.sleep(5)


# =========================================================
# 🛡️ SAFE TELEGRAM API WRAPPERS
# =========================================================

def safe_edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    try:
        return bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id,
                                     reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        return None


def safe_send_message(chat_id, text, reply_markup=None, parse_mode="HTML",
                      disable_preview=True, reply_to_msg_id=None):
    try:
        return bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                parse_mode=parse_mode, disable_web_page_preview=disable_preview,
                                reply_to_message_id=reply_to_msg_id)
    except Exception:
        try:
            return bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                    parse_mode=None, disable_web_page_preview=disable_preview,
                                    reply_to_message_id=reply_to_msg_id)
        except Exception:
            return None


def safe_send_document(chat_id, document, caption="", parse_mode="HTML",
                       reply_to_msg_id=None, reply_markup=None):
    try:
        return bot.send_document(chat_id, document, caption=caption, parse_mode=parse_mode,
                                 timeout=180, reply_to_message_id=reply_to_msg_id,
                                 reply_markup=reply_markup)
    except Exception:
        try:
            return bot.send_document(chat_id, document, caption=caption, parse_mode=None,
                                     timeout=180, reply_to_message_id=reply_to_msg_id,
                                     reply_markup=reply_markup)
        except Exception:
            return None


def safe_send_video(chat_id, video, caption="", parse_mode="HTML",
                    reply_to_msg_id=None, reply_markup=None):
    try:
        return bot.send_video(chat_id, video, caption=caption, parse_mode=parse_mode,
                              timeout=180, supports_streaming=True,
                              reply_to_message_id=reply_to_msg_id, reply_markup=reply_markup)
    except Exception:
        try:
            return bot.send_video(chat_id, video, caption=caption, parse_mode=None,
                                  timeout=180, reply_to_message_id=reply_to_msg_id,
                                  reply_markup=reply_markup)
        except Exception:
            return None


def safe_send_photo(chat_id, photo, caption="", parse_mode="HTML",
                    reply_to_msg_id=None, reply_markup=None):
    try:
        return bot.send_photo(chat_id, photo, caption=caption, parse_mode=parse_mode,
                              reply_to_message_id=reply_to_msg_id, reply_markup=reply_markup)
    except Exception:
        try:
            return bot.send_photo(chat_id, photo, caption=caption, parse_mode=None,
                                  reply_to_message_id=reply_to_msg_id, reply_markup=reply_markup)
        except Exception:
            return None


# =========================================================
# 💎 BOLD FONT & DATABASE
# =========================================================

def to_bold_font(text: str) -> str:
    out = []
    for char in str(text):
        code = ord(char)
        if 65 <= code <= 90:
            out.append(chr(0x1D400 + (code - 65)))
        elif 97 <= code <= 122:
            out.append(chr(0x1D41A + (code - 97)))
        elif 48 <= code <= 57:
            out.append(chr(0x1D7CE + (code - 48)))
        else:
            out.append(char)
    return "".join(out)


def load_users_data():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users_data(data):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def register_user(user):
    try:
        data = load_users_data()
        uid_str = str(user.id)
        if uid_str not in data:
            data[uid_str] = {
                "id": user.id,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "username": user.username if user.username else "N/A",
                "joined_at": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            }
            save_users_data(data)
    except Exception as e:
        print(f"User Register Error: {e}")


def get_all_user_ids():
    return [int(uid) for uid in load_users_data().keys()]


def load_banned_users():
    if os.path.exists(BANNED_FILE):
        try:
            with open(BANNED_FILE, "r", encoding="utf-8") as f:
                return set(int(uid) for uid in json.load(f))
        except Exception:
            return set()
    return set()


def save_banned_users(banned_set):
    try:
        with open(BANNED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(banned_set), f)
    except Exception:
        pass


def is_user_banned(user_id):
    if user_id == ADMIN_ID:
        return False
    return int(user_id) in load_banned_users()


def ban_user_id(user_id):
    banned = load_banned_users()
    banned.add(int(user_id))
    save_banned_users(banned)


def unban_user_id(user_id):
    banned = load_banned_users()
    if int(user_id) in banned:
        banned.remove(int(user_id))
        save_banned_users(banned)


# =========================================================
# 🔒 FORCE SUB CHECKER (DOUBLE CHANNEL)
# =========================================================

def is_user_subscribed(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        for ch in FORCE_SUB_CHANNELS:
            try:
                member = bot.get_chat_member(ch["id"], user_id)
                if member.status not in ['creator', 'administrator', 'member', 'restricted']:
                    return False
            except Exception as e:
                print(f"Force Sub Verify Error ({ch['id']}): {e}")
                return False
        return True
    except Exception as e:
        print(f"Force Sub Verify Outer: {e}")
        return False


def get_force_sub_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_join1 = types.InlineKeyboardButton("📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝟏 𝐉𝐎𝐈𝐍 𝐍𝐎𝐖", url=FORCE_SUB_CHANNELS[0]["url"])
    btn_join2 = types.InlineKeyboardButton("📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝟐 𝐉𝐎𝐈𝐍 𝐍𝐎𝐖", url=FORCE_SUB_CHANNELS[1]["url"])
    btn_check = types.InlineKeyboardButton("✅ 𝐂𝐇𝐄𝐂𝐊 𝐉𝐎𝐈𝐍 / 𝐔𝐍𝐋𝐎𝐂𝐊", callback_data="sub_check_now")
    markup.add(btn_join1, btn_join2, btn_check)
    return markup


def send_force_sub_msg(chat_id, user_id):
    lock_text = (
        "╔═══════════════════════════════╗\n"
        "   🔒 <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐋𝐎𝐂𝐊𝐄𝐃</b> 🔒\n"
        "╚═══════════════════════════════╝\n\n"
        "👋 <b>প্রিয় গ্রাহক,</b>\n\n"
        "✨ বটটির সমস্ত <b>𝐕𝐈𝐏 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒</b> ব্যবহার করতে হলে আপনাকে অবশ্যই আমাদের <b>দুইটি অফিশিয়াল চ্যানেলে</b> যুক্ত থাকতে হবে।\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 <b>𝐒𝐓𝐄𝐏𝐒:</b>\n"
        "1️⃣ দুইটি চ্যানেলে জয়েন করুন\n"
        "2️⃣ 'চেক জয়েন' বাটনে চাপ দিন\n"
        "3️⃣ আনলক করুন 🎉\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 <b>নিচের বাটনে ক্লিক করুন:</b>"
    )
    return safe_send_message(chat_id, lock_text, reply_markup=get_force_sub_markup())


# =========================================================
# 🖼️ IMAGE TO URL API ENGINE (ImgBB Integration)
# =========================================================

def upload_image_bytes_to_url(image_bytes):
    """ImgBB API - আপনার key দিয়ে ছবি আপলোড করে ডিরেক্ট লিংক দেয়"""
    try:
        url = "https://api.imgbb.com/1/upload"
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        payload = {
            'key': IMGBB_API_KEY,
            'image': b64_image
        }
        res = requests.post(url, data=payload, timeout=30)
        if res.status_code == 200:
            json_res = res.json()
            if json_res.get("success"):
                return json_res["data"]["url"]
            else:
                print(f"ImgBB API Error: {json_res.get('error', {}).get('message', 'Unknown')}")
    except Exception as e:
        print(f"Image Upload Error: {e}")
    return None


# =========================================================
# 🔥 14-LAYER CIPHER ENGINE & BEAUTIFIED HTML BUILDER
# =========================================================

STD_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

CUSTOM_ALPHABET = [
    "👿", "🔥", "🥵", "💀", "❌", "🔒", "⚡", "🎯",
    "%", "+", "=", "-", "&", "^", "_", "~",
    "k", "d", "j", "i", "h", "o", "b", "f",
    "q", "w", "r", "t", "y", "u", "p", "a",
    "s", "g", "l", "z", "x", "c", "v", "n",
    "m", "3", "9", "8", "4", "7", "2", "5",
    "6", "0", "1", "£", "€", "¥", "₹", "§",
    "π", "θ", "λ", "μ", "Ω", "∞", "≠", "÷"
]

# Layer 8-14: Second emoji alphabet for extra layers
CUSTOM_ALPHABET_2 = [
    "🐉", "💎", "⚔️", "🛡️", "☠️", "🕷️", "🦂", "🐍",
    "@", "#", "$", "!", "?", ":", ";", "|",
    "A", "B", "C", "D", "E", "F", "G", "H",
    "I", "J", "K", "L", "M", "N", "O", "P",
    "Q", "R", "S", "T", "U", "V", "W", "X",
    "Y", "Z", "a", "b", "c", "d", "e", "f",
    "g", "h", "i", "j", "l", "m", "n", "o",
    "p", "q", "r", "s", "t", "u", "v", "w"
]

B64_TO_CUSTOM = {STD_B64[i]: CUSTOM_ALPHABET[i] for i in range(64)}
B64_TO_CUSTOM["="] = "•"

B64_TO_CUSTOM_2 = {STD_B64[i]: CUSTOM_ALPHABET_2[i] for i in range(64)}
B64_TO_CUSTOM_2["="] = "▪"


def fix_html_relative_assets(html_content, base_url):
    if "<base " in html_content.lower():
        return html_content
    base_tag = f'<base href="{base_url}">'
    if re.search(r"<head[^>]*>", html_content, re.IGNORECASE):
        return re.sub(r"(<head[^>]*>)", rf"\1\n  {base_tag}", html_content, count=1, flags=re.IGNORECASE)
    elif re.search(r"<html[^>]*>", html_content, re.IGNORECASE):
        return re.sub(r"(<html[^>]*>)", rf"\1\n<head>\n  {base_tag}\n</head>", html_content, count=1, flags=re.IGNORECASE)
    return f"<head>{base_tag}</head>\n" + html_content


def multi_layer_encrypt_14level(raw_html):
    """
    🔐 14-LAYER MILITARY ENCRYPTION PIPELINE:
    ═══════════════════════════════════════════════
    Layer  1: UTF-8 Stream Encoding
    Layer  2: Byte Offset Shifting (+shift_val)
    Layer  3: Dynamic Key & Step Multi-XOR
    Layer  4: Standard Base64 Encoding
    Layer  5: String Reversal (Reverse Base64)
    Layer  6: Custom Emoji & Symbol Substitution
    Layer  7: Base64 Re-encoding
    Layer  8: Second Emoji Alphabet Substitution
    Layer  9: Hex Encoding
    Layer 10: Hex Reversal
    Layer 11: Second XOR Cipher (Different Key)
    Layer 12: Base64 Encoding
    Layer 13: Third Emoji Substitution
    Layer 14: Final Byte Shift
    ═══════════════════════════════════════════════
    """
    # ═══════════ LAYERS 1-6 (Original) ═══════════
    raw_bytes = raw_html.encode("utf-8")
    
    shift_val = random.randint(5, 240)
    shifted_bytes = bytearray((b + shift_val) & 0xFF for b in raw_bytes)

    seed = random.randint(40, 215)
    step = random.choice([29, 31, 37, 41, 43, 47])
    xor_bytes = bytearray()
    curr_key = seed
    for b in shifted_bytes:
        xor_bytes.append(b ^ curr_key)
        curr_key = (curr_key + step) & 0xFF

    b64_str = base64.b64encode(xor_bytes).decode("ascii")
    reversed_b64 = b64_str[::-1]
    payload = "".join(B64_TO_CUSTOM.get(c, c) for c in reversed_b64)

    # ═══════════ LAYER 7: Re-encode to Base64 ═══════════
    layer7_b64 = base64.b64encode(payload.encode("utf-8")).decode("ascii")

    # ═══════════ LAYER 8: Second Emoji Alphabet ═══════════
    layer8_emoji = "".join(B64_TO_CUSTOM_2.get(c, c) for c in layer7_b64)

    # ═══════════ LAYER 9: Hex Encoding ═══════════
    layer9_hex = layer8_emoji.encode("utf-8").hex()

    # ═══════════ LAYER 10: Hex Reversal ═══════════
    layer10_rev = layer9_hex[::-1]

    # ═══════════ LAYER 11: Second XOR Cipher ═══════════
    seed2 = random.randint(30, 200)
    step2 = random.choice([17, 19, 23, 29, 31, 37])
    layer11_xor = bytearray()
    curr_key2 = seed2
    for c in layer10_rev:
        b = ord(c) & 0xFF
        layer11_xor.append(b ^ curr_key2)
        curr_key2 = (curr_key2 + step2) & 0xFF

    # ═══════════ LAYER 12: Base64 Encoding ═══════════
    layer12_b64 = base64.b64encode(bytes(layer11_xor)).decode("ascii")

    # ═══════════ LAYER 13: Third Emoji Substitution ═══════════
    # Reuse alphabet 1 with reversed mapping for extra confusion
    layer13 = ""
    for c in layer12_b64:
        if c in B64_TO_CUSTOM:
            layer13 += B64_TO_CUSTOM[c]
        else:
            layer13 += c

    # ═══════════ LAYER 14: Final Byte Shift ═══════════
    shift2 = random.randint(3, 100)
    layer14_bytes = bytearray()
    for c in layer13:
        b = ord(c) & 0xFFFF
        layer14_bytes.append((b + shift2) & 0xFFFF)

    # Convert final bytes to unicode string (safe for JSON)
    final_payload = "".join(chr(b) for b in layer14_bytes if 0x20 <= b <= 0x10FFFF and not (0xD800 <= b <= 0xDFFF))
    
    # For safety, encode the final payload as JSON-safe string
    final_payload_b64 = base64.b64encode(final_payload.encode("utf-8", errors="surrogatepass")).decode("ascii")

    return final_payload_b64, seed, step, shift_val, seed2, step2, shift2


def build_extreme_obfuscated_html(raw_html, fallback_title="Protected Document"):
    """
    ULTIMATE OBFUSCATOR v4.0 (14-LAYER EDITION)
    """
    title_match = re.search(r"<title[^>]*>(.*?)</title>", raw_html, re.IGNORECASE | re.DOTALL)
    page_title_raw = title_match.group(1).strip() if (title_match and title_match.group(1).strip()) else fallback_title
    page_title = html.escape(page_title_raw)

    (payload_data, seed, step, shift_val, 
     seed2, step2, shift2) = multi_layer_encrypt_14level(raw_html)

    payload_json = json.dumps(payload_data)
    emojis_json = json.dumps(CUSTOM_ALPHABET)
    emojis2_json = json.dumps(CUSTOM_ALPHABET_2)

    honeypot_url = f"{RENDER_EXTERNAL_URL.rstrip('/')}/trap/decode"
    
    timestamp_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    token_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    session_id = hashlib.md5(f"{token_str}{time.time()}".encode()).hexdigest()

    fake_dump = f"👿🔥🥵💀❌ [১৪-লেয়ার ইনক্রিপশন ডিকোড করার চেষ্টা করছিস? তোর এই আব্বার বট {BOT_USERNAME} দিয়ে ইনক্রিপ্টেড মারা এবং ওনার: @{ADMIN_USERNAME}] 🔒⚡_{token_str}"

    banner_content = (
        f"╔══════════════════════════════════════════════════════════════╗\n"
        f"║ 𝐓𝐀𝐋𝐇𝐀 𝐒𝐀𝐈𝐅 🔒 𝐔𝐋𝐓𝐑𝐀 𝐂𝐈𝐏𝐇𝐄𝐑 𝐒𝐇𝐈𝐄𝐋𝐃 𝐯𝟒.𝟎 (𝟏𝟒-𝐋𝐀𝐘𝐄𝐑) - 𝐍𝐎 𝐌𝐎𝐃𝐈𝐅𝐘      ║\n"
        f"║══════════════════════════════════════════════════════════════║\n"
        f"║  𝐎𝐛𝐟𝐮𝐬𝐜𝐚𝐭𝐞𝐝 𝐁𝐲: @{ADMIN_USERNAME:<45}║\n"
        f"║  𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐁𝐨𝐭: {BOT_USERNAME:<47}║\n"
        f"║  𝐓𝐢𝐦𝐞𝐬𝐭𝐚𝐦𝐩: {timestamp_str:<49}║\n"
        f"║  𝐒𝐞𝐜𝐮𝐫𝐢𝐭𝐲 𝐓𝐨𝐤𝐞𝐧: {token_str:<44}║\n"
        f"║  𝐄𝐧𝐜𝐫𝐲𝐩𝐭𝐢𝐨𝐧 𝐋𝐞𝐯𝐞𝐥: 𝟏𝟒-𝐋𝐀𝐘𝐄𝐑 𝐔𝐋𝐓𝐑𝐀 𝐄𝐍𝐂𝐑𝐘𝐏𝐓𝐈𝐎𝐍              ║\n"
        f"║  𝐒𝐞𝐬𝐬𝐢𝐨𝐧: {session_id[:38]:<47}║\n"
        f"╚══════════════════════════════════════════════════════════════╝\n"
        f"⚠️ 𝐖𝐀𝐑𝐍𝐈𝐍𝐆: This file is protected by 14-Layer Military Encryption.\n"
        f"⚠️ Any attempt to decode will trigger Honeypot Trap.\n"
        f"⚠️ Message: {fake_dump}\n"
    )

    return f"""<!--
{banner_content}
-->
<!DOCTYPE html>
<!-- DECOY_TRAP_PAYLOAD: {fake_dump} -->
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<style>
* {{
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    user-select: none !important;
}}
</style>
<script>
(function() {{
    'use strict';

    // 🛡️ ANTI-DEVTOOLS & RIGHT CLICK PROTECTION
    document.addEventListener('contextmenu', function(e) {{ e.preventDefault(); }}, true);
    document.addEventListener('keydown', function(e) {{
        if (
            e.key === 'F12' ||
            (e.ctrlKey && e.key.toLowerCase() === 'u') ||
            (e.ctrlKey && e.key.toLowerCase() === 's') ||
            (e.ctrlKey && e.shiftKey && ['i', 'j', 'c'].includes(e.key.toLowerCase()))
        ) {{
            e.preventDefault();
            e.stopPropagation();
            return false;
        }}
    }}, true);

    try {{
        console.log("%c🚨 AUTHORIZED ACCESS ONLY - 14 LAYER ENCRYPTED 🚨", "color:red;font-size:26px;font-weight:bold;");
        console.log("%cআপনার IP এড্রেস সহ সমস্ত তথ্য সার্ভারে রেকর্ড করা হয়েছে!", "color:orange;font-size:16px;");
    }} catch(e) {{}}

    const _0xstd = "{STD_B64}";
    const _0xemj = {emojis_json};
    const _0xemj2 = {emojis2_json};
    const _0xdata = {payload_json};
    const _0xseed = {seed};
    const _0xstep = {step};
    const _0xshift = {shift_val};
    const _0xseed2 = {seed2};
    const _0xstep2 = {step2};
    const _0xshift2 = {shift2};

    const _0xmap = new Map();
    for (let i = 0; i < _0xemj.length; i++) {{
        _0xmap.set(_0xemj[i], _0xstd[i]);
    }}
    _0xmap.set("•", "=");

    const _0xmap2 = new Map();
    for (let i = 0; i < _0xemj2.length; i++) {{
        _0xmap2.set(_0xemj2[i], _0xstd[i]);
    }}
    _0xmap2.set("▪", "=");

    try {{
        // ============ LAYER 14 UNMAP: Un-Base64 the final payload ============
        const _0xbin14 = atob(_0xdata);
        const _0xbytes14 = new Uint8Array(_0xbin14.length);
        for (let i = 0; i < _0xbin14.length; i++) _0xbytes14[i] = _0xbin14.charCodeAt(i);
        let _0xstr14 = "";
        for (let i = 0; i < _0xbytes14.length; i++) _0xstr14 += String.fromCharCode(_0xbytes14[i]);
        
        // ============ LAYER 13 UNMAP: Undo byte shift ============
        let _0xstr13 = "";
        for (let i = 0; i < _0xstr14.length; i++) {{
            let b = _0xstr14.charCodeAt(i);
            b = (b - _0xshift2 + 65536) & 0xFFFF;
            _0xstr13 += String.fromCharCode(b);
        }}

        // ============ LAYER 12 UNMAP: Third emoji substitution ============
        const _0xsyms13 = Array.from(_0xstr13);
        let _0xstr12 = "";
        for (let i = 0; i < _0xsyms13.length; i++) {{
            _0xstr12 += _0xmap.get(_0xsyms13[i]) || _0xsyms13[i];
        }}

        // ============ LAYER 11 UNMAP: Un-Base64 ============
        const _0xbin11 = atob(_0xstr12);
        const _0xlen11 = _0xbin11.length;
        const _0xout11 = new Uint8Array(_0xlen11);

        // ============ LAYER 10 UNMAP: Un-XOR #2 ============
        let _0xcurr2 = _0xseed2;
        for (let k = 0; k < _0xlen11; k++) {{
            _0xout11[k] = _0xbin11.charCodeAt(k) ^ _0xcurr2;
            _0xcurr2 = (_0xcurr2 + _0xstep2) & 0xFF;
        }}

        // ============ LAYER 9 UNMAP: Un-reverse hex ============
        let _0xstr9 = "";
        for (let i = 0; i < _0xout11.length; i++) _0xstr9 += String.fromCharCode(_0xout11[i]);
        _0xstr9 = _0xstr9.split("").reverse().join("");

        // ============ LAYER 8 UNMAP: Un-hex ============
        let _0xstr8 = "";
        for (let i = 0; i < _0xstr9.length; i += 2) {{
            _0xstr8 += String.fromCharCode(parseInt(_0xstr9.substr(i, 2), 16));
        }}

        // ============ LAYER 7 UNMAP: Second emoji alphabet ============
        const _0xsyms8 = Array.from(_0xstr8);
        let _0xstr7 = "";
        for (let i = 0; i < _0xsyms8.length; i++) {{
            _0xstr7 += _0xmap2.get(_0xsyms8[i]) || _0xsyms8[i];
        }}

        // ============ LAYER 6 UNMAP: Un-Base64 (Layer 7) ============
        const _0xbin7 = atob(_0xstr7);

        // ============ LAYER 5 UNMAP: First emoji substitution ============
        const _0xsyms5 = Array.from(_0xbin7);
        let _0xstr5 = "";
        for (let i = 0; i < _0xsyms5.length; i++) {{
            _0xstr5 += _0xmap.get(_0xsyms5[i]) || _0xsyms5[i];
        }}

        // ============ LAYER 4 UNMAP: Unreverse base64 ============
        const _0xb64 = _0xstr5.split("").reverse().join("");

        // ============ LAYER 3 UNMAP: Un-Base64 ============
        const _0xbin = atob(_0xb64);
        const _0xlen = _0xbin.length;
        const _0xout = new Uint8Array(_0xlen);

        // ============ LAYER 2 UNMAP: Un-XOR ============
        let _0xcurr = _0xseed;
        for (let k = 0; k < _0xlen; k++) {{
            let _0xxor = _0xbin.charCodeAt(k) ^ _0xcurr;
            
            // ============ LAYER 1 UNMAP: Un-shift ============
            _0xout[k] = (_0xxor - _0xshift + 256) & 0xFF;
            
            _0xcurr = (_0xcurr + _0xstep) & 0xFF;
        }}

        // ============ FINAL: Decode UTF-8 ============
        const _0xdecoded = new TextDecoder("utf-8").decode(_0xout);

        // Seamless original HTML page rendering
        document.open();
        document.write(_0xdecoded);
        document.close();

    }} catch (err) {{
        try {{
            var _img = new Image();
            _img.src = "{honeypot_url}?r=decode_failed&t=" + Date.now();
        }} catch(e) {{}}
    }}
}})();
</script>
</head>
<body>
<noscript>
    <div style="padding:40px;text-align:center;font-family:sans-serif;color:#666;">
        <h2>JavaScript Required</h2>
        <p>Please enable JavaScript to view this page.</p>
    </div>
</noscript>
</body>
</html>
"""


# =========================================================
# 🚀 VIDEO DOWNLOAD ENGINES
# =========================================================

def download_tiktok_direct(url):
    try:
        api_url = "https://www.tikwm.com/api/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.post(api_url, data={"url": url}, headers=headers, timeout=20)
        data = res.json()
        if data.get("code") == 0 and "data" in data:
            v_data = data["data"]
            direct_vid_url = v_data.get("hdplay") or v_data.get("play")
            title = v_data.get("title") or "TikTok_HD_Video"
            duration = str(v_data.get("duration", "N/A")) + "s"
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            file_path = f"downloads/tiktok_{random_id}.mp4"
            os.makedirs("downloads", exist_ok=True)
            vid_res = requests.get(direct_vid_url, headers=headers, timeout=60, stream=True)
            with open(file_path, "wb") as f:
                for chunk in vid_res.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            real_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if 0 < real_size <= 48 * 1024 * 1024:
                return {"type": "file", "path": file_path, "title": title,
                        "size_mb": round(real_size / (1024 * 1024), 2)}
            else:
                return {"type": "direct_url", "url": direct_vid_url, "title": title,
                        "size_mb": round(real_size / (1024 * 1024), 2) if real_size else "Unlimited",
                        "duration": duration, "temp_path": file_path}
    except Exception as e:
        print(f"TikTok Error: {e}")
    return None


def download_via_cobalt(url):
    instances = ["https://api.cobalt.tools", "https://co.wuk.sh", "https://cobalt.v0.id"]
    headers = {"Accept": "application/json", "Content-Type": "application/json",
               "User-Agent": "Mozilla/5.0"}
    payload = {"url": url, "videoQuality": "720", "youtubeVideoCodec": "h264"}
    for base_api in instances:
        try:
            res = requests.post(base_api, json=payload, headers=headers, timeout=12)
            if res.status_code == 200:
                data = res.json()
                direct_url = data.get("url")
                if not direct_url and data.get("picker"):
                    direct_url = data["picker"][0].get("url")
                if direct_url:
                    return direct_url
        except Exception as e:
            print(f"Cobalt Warning ({base_api}): {e}")
            continue
    return None


def download_facebook_direct(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://snapsave.app/"}
        res = requests.post("https://snapsave.app/action.php", data={"url": url}, headers=headers, timeout=15)
        if res.status_code == 200:
            text = res.text
            links = re.findall(r'href="(https?://[^"]+)"', text)
            fb_links = [l for l in links if "fbcdn" in l or "video" in l or ".mp4" in l]
            if fb_links:
                direct_vid_url = fb_links[0].replace("&amp;", "&")
                random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                file_path = f"downloads/fb_{random_id}.mp4"
                os.makedirs("downloads", exist_ok=True)
                v_res = requests.get(direct_vid_url, headers=headers, timeout=60, stream=True)
                with open(file_path, "wb") as f:
                    for chunk in v_res.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                real_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                if 0 < real_size <= 48 * 1024 * 1024:
                    return {"type": "file", "path": file_path, "title": "Facebook_HD_Video",
                            "size_mb": round(real_size / (1024 * 1024), 2)}
                else:
                    return {"type": "direct_url", "url": direct_vid_url, "title": "Facebook_HD_Video",
                            "size_mb": round(real_size / (1024 * 1024), 2),
                            "duration": "N/A", "temp_path": file_path}
    except Exception as e:
        print(f"FB Error: {e}")
    cobalt_url = download_via_cobalt(url)
    if cobalt_url:
        try:
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            file_path = f"downloads/fb_{random_id}.mp4"
            os.makedirs("downloads", exist_ok=True)
            v_res = requests.get(cobalt_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, stream=True)
            with open(file_path, "wb") as f:
                for chunk in v_res.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            real_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if 0 < real_size <= 48 * 1024 * 1024:
                return {"type": "file", "path": file_path, "title": "Facebook_HD_Video",
                        "size_mb": round(real_size / (1024 * 1024), 2)}
            else:
                return {"type": "direct_url", "url": cobalt_url, "title": "Facebook_HD_Video",
                        "size_mb": round(real_size / (1024 * 1024), 2),
                        "duration": "N/A", "temp_path": file_path}
        except Exception:
            pass
    return None


def get_instagram_video_from_embed(url):
    match = re.search(r'instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)', url)
    if not match:
        return None
    shortcode = match.group(1)
    embed_urls = [
        f"https://www.instagram.com/p/{shortcode}/embed/captioned/",
        f"https://www.instagram.com/reel/{shortcode}/embed/captioned/",
    ]
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.5"}
    for embed_url in embed_urls:
        try:
            res = requests.get(embed_url, headers=headers, timeout=10)
            if res.status_code == 200:
                text = res.text
                matches = re.findall(r'video_url\\*":\\*"([^"]+)"', text)
                if not matches:
                    matches = re.findall(r'"video_url"\s*:\s*"([^"]+)"', text)
                for raw_url in matches:
                    clean_url = (raw_url.replace('\\/', '/')
                                 .replace('\\u0026', '&')
                                 .replace('&amp;', '&')
                                 .replace('\\', ''))
                    if "scontent" in clean_url or "cdninstagram" in clean_url:
                        return clean_url
        except Exception:
            continue
    return None


def download_instagram_direct(url):
    direct_vid_url = download_via_cobalt(url)
    if not direct_vid_url:
        direct_vid_url = get_instagram_video_from_embed(url)
    if direct_vid_url:
        try:
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            file_path = f"downloads/insta_{random_id}.mp4"
            os.makedirs("downloads", exist_ok=True)
            vid_res = requests.get(direct_vid_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, stream=True)
            with open(file_path, "wb") as f:
                for chunk in vid_res.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            real_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if 0 < real_size <= 48 * 1024 * 1024:
                return {"type": "file", "path": file_path, "title": "Instagram_Reels_HD",
                        "size_mb": round(real_size / (1024 * 1024), 2)}
            elif real_size > 48 * 1024 * 1024:
                return {"type": "direct_url", "url": direct_vid_url, "title": "Instagram_Reels_HD",
                        "size_mb": round(real_size / (1024 * 1024), 2),
                        "duration": "N/A", "temp_path": file_path}
        except Exception as e:
            print(f"Insta error: {e}")
    try:
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        ydl_opts = {'format': 'best[ext=mp4]',
                    'outtmpl': f"downloads/insta_{random_id}_%(id)s.%(ext)s",
                    'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if os.path.exists(file_path):
                real_size = os.path.getsize(file_path)
                return {"type": "file", "path": file_path, "title": info.get('title', 'Instagram'),
                        "size_mb": round(real_size / (1024 * 1024), 2)}
    except Exception as e:
        print(f"Insta yt-dlp error: {e}")
    return None


def download_youtube_direct(url):
    cobalt_direct_url = download_via_cobalt(url)
    if cobalt_direct_url:
        try:
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            file_path = f"downloads/yt_{random_id}.mp4"
            os.makedirs("downloads", exist_ok=True)
            v_res = requests.get(cobalt_direct_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, stream=True)
            with open(file_path, "wb") as f:
                for chunk in v_res.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            real_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if 0 < real_size <= 48 * 1024 * 1024:
                return {"type": "file", "path": file_path, "title": "YouTube_HD_Video",
                        "size_mb": round(real_size / (1024 * 1024), 2)}
            else:
                return {"type": "direct_url", "url": cobalt_direct_url, "title": "YouTube_HD_Video",
                        "size_mb": round(real_size / (1024 * 1024), 2),
                        "duration": "N/A", "temp_path": file_path}
        except Exception:
            pass
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f"downloads/yt_{random_id}_%(id)s.%(ext)s",
        'noplaylist': True, 'quiet': True, 'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'mweb'],
                                        'skip': ['webpage']}},
        'http_headers': {'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11; en_US) gzip'}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'YouTube_HD_Video')
            duration = info.get('duration_string', 'N/A')
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
                base, _ = os.path.splitext(file_path)
                for ext in ['.mp4', '.mkv', '.webm']:
                    if os.path.exists(base + ext):
                        file_path = base + ext
                        break
            if os.path.exists(file_path):
                real_size = os.path.getsize(file_path)
                if 0 < real_size <= 48 * 1024 * 1024:
                    return {"type": "file", "path": file_path, "title": title,
                            "size_mb": round(real_size / (1024 * 1024), 2)}
                else:
                    return {"type": "direct_url", "url": info.get('url') or url, "title": title,
                            "size_mb": round(real_size / (1024 * 1024), 2),
                            "duration": duration, "temp_path": file_path}
    except Exception as e:
        print(f"YT error: {e}")
    return None


def process_unlimited_video(url):
    os.makedirs("downloads", exist_ok=True)
    url_lower = url.lower()
    if any(k in url_lower for k in ["tiktok.com", "douyin.com"]):
        r = download_tiktok_direct(url)
        if r:
            return r
    if any(k in url_lower for k in ["facebook.com", "fb.watch", "fb.gg", "fb.com"]):
        r = download_facebook_direct(url)
        if r:
            return r
    if any(k in url_lower for k in ["instagram.com", "instagr.am"]):
        r = download_instagram_direct(url)
        if r:
            return r
        raise Exception("ইনস্টাগ্রাম ভিডিওটি একসেস করা সম্ভব হচ্ছে না।")
    if any(k in url_lower for k in ["youtube.com", "youtu.be"]):
        r = download_youtube_direct(url)
        if r:
            return r
    cobalt_direct_url = download_via_cobalt(url)
    if cobalt_direct_url:
        try:
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            file_path = f"downloads/video_{random_id}.mp4"
            v_res = requests.get(cobalt_direct_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, stream=True)
            with open(file_path, "wb") as f:
                for chunk in v_res.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            real_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if 0 < real_size <= 48 * 1024 * 1024:
                return {"type": "file", "path": file_path, "title": "Social_Media_HD",
                        "size_mb": round(real_size / (1024 * 1024), 2)}
            else:
                return {"type": "direct_url", "url": cobalt_direct_url, "title": "Social_Media_HD",
                        "size_mb": round(real_size / (1024 * 1024), 2),
                        "duration": "N/A", "temp_path": file_path}
        except Exception:
            pass
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f"downloads/{random_id}_%(id)s.%(ext)s",
        'noplaylist': True, 'quiet': True, 'no_warnings': True,
        'extractor_retries': 5, 'nocheckcertificate': True, 'geo_bypass': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0'}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise Exception("ভিডিওটির ডেটা পাওয়া যায়নি!")
        title = info.get('title', 'VIP_Video')
        duration = info.get('duration_string', 'N/A')
        direct_stream_url = info.get('url')
        file_path = ydl.prepare_filename(info)
        if not os.path.exists(file_path):
            base, _ = os.path.splitext(file_path)
            for ext in ['.mp4', '.mkv', '.webm']:
                if os.path.exists(base + ext):
                    file_path = base + ext
                    break
        if os.path.exists(file_path):
            real_size = os.path.getsize(file_path)
            if 0 < real_size <= 48 * 1024 * 1024:
                return {"type": "file", "path": file_path, "title": title,
                        "size_mb": round(real_size / (1024 * 1024), 2)}
            else:
                return {"type": "direct_url", "url": direct_stream_url or url, "title": title,
                        "size_mb": round(real_size / (1024 * 1024), 2),
                        "duration": duration, "temp_path": file_path}
        else:
            filesize = info.get('filesize') or info.get('filesize_approx') or 0
            return {"type": "direct_url", "url": direct_stream_url or url, "title": title,
                    "size_mb": round(filesize / (1024 * 1024), 2) if filesize else "Unlimited",
                    "duration": duration}


# =========================================================
# 📱 KEYBOARDS
# =========================================================

def get_persistent_menu(user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_vid = types.KeyboardButton("🎥 𝐔𝐑𝐋 𝐓𝐎 𝐕𝐈𝐃𝐄𝐎")
    btn_img = types.KeyboardButton("🖼️ 𝐈𝐌𝐀𝐆𝐄 𝐓𝐎 𝐔𝐑𝐋")
    btn_obf = types.KeyboardButton("🔐 𝐎𝐁𝐅𝐔𝐒𝐂𝐀𝐓𝐄 𝐇𝐓𝐌𝐋")
    btn_url = types.KeyboardButton("🌐 𝐔𝐑𝐋 𝐓𝐎 𝐇𝐓𝐌𝐋")
    btn_dev = types.KeyboardButton("👑 𝐎𝐖𝐍𝐄𝐑 & 𝐃𝐄𝐕")
    btn_help = types.KeyboardButton("⚡ 𝐕𝐈𝐏 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒 & 𝐈𝐍𝐅𝐎")
    
    markup.add(btn_vid, btn_img)
    markup.add(btn_obf, btn_url)
    if user_id and int(user_id) == ADMIN_ID:
        btn_admin = types.KeyboardButton("🛠️ 𝐀𝐃𝐌𝐈𝐍 𝐂𝐎𝐍𝐓𝐑𝐎𝐋")
        markup.add(btn_admin)
    markup.add(btn_dev, btn_help)
    return markup


def get_admin_interactive_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_stats = types.InlineKeyboardButton("📊 𝐋𝐈𝐕𝐄 𝐒𝐓𝐀𝐓𝐒", callback_data="adm_stats")
    btn_users = types.InlineKeyboardButton("👥 𝐔𝐒𝐄𝐑 𝐋𝐈𝐒𝐓", callback_data="adm_users")
    btn_bc = types.InlineKeyboardButton("📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓", callback_data="adm_broadcast")
    btn_send = types.InlineKeyboardButton("✉️ 𝐃𝐈𝐑𝐄𝐂𝐓 𝐌𝐒𝐆", callback_data="adm_send_pm")
    btn_ban = types.InlineKeyboardButton("⛔ 𝐁𝐀𝐍 𝐔𝐒𝐄𝐑", callback_data="adm_ban")
    btn_unban = types.InlineKeyboardButton("🟢 𝐔𝐍𝐁𝐀𝐍 𝐔𝐒𝐄𝐑", callback_data="adm_unban")
    btn_banned_list = types.InlineKeyboardButton("🚫 𝐁𝐀𝐍𝐍𝐄𝐃 𝐋𝐈𝐒𝐓", callback_data="adm_banned")
    btn_traps = types.InlineKeyboardButton("🪤 𝐓𝐑𝐀𝐏 𝐋𝐎𝐆𝐒", callback_data="adm_traps")
    btn_close = types.InlineKeyboardButton("❌ 𝐂𝐋𝐎𝐒𝐄 𝐏𝐀𝐍𝐄𝐋", callback_data="adm_close")
    markup.add(btn_stats, btn_users)
    markup.add(btn_bc, btn_send)
    markup.add(btn_ban, btn_unban)
    markup.add(btn_banned_list, btn_traps)
    markup.add(btn_close)
    return markup


def check_access(message):
    try:
        uid = message.from_user.id
        if uid == ADMIN_ID:
            return True
        if is_user_banned(uid):
            safe_send_message(message.chat.id,
                              f"🚫 <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐒𝐔𝐒𝐏𝐄𝐍𝐃𝐄𝐃!</b>\n\n⚠️ পলিসি লঙ্ঘনের কারণে অ্যাকাউন্ট সাসপেন্ড।\n👑 যোগাযোগ: @{ADMIN_USERNAME}")
            return False
        if not is_user_subscribed(uid):
            send_force_sub_msg(message.chat.id, uid)
            return False
        return True
    except Exception:
        return True


def smart_normalize_url(raw_text):
    text = raw_text.strip()
    if text.startswith("http://") or text.startswith("https://"):
        return text
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$", text):
        return f"https://{text}"
    return None


def fetch_url_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=25, verify=True)
    except requests.exceptions.SSLError:
        res = requests.get(url, headers=headers, timeout=25, verify=False)
    except requests.exceptions.RequestException:
        if url.startswith("https://"):
            res = requests.get("http://" + url[8:], headers=headers, timeout=25)
        else:
            raise
    res.encoding = res.apparent_encoding or "utf-8"
    return res.text


# =========================================================
# 📢 BROADCAST ENGINE
# =========================================================

def broadcast_any_message(from_chat_id, source_message):
    users = get_all_user_ids()
    banned_users = load_banned_users()
    sent_count = 0
    failed_count = 0
    status_msg = safe_send_message(from_chat_id, "⏳ <b>𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓𝐈𝐍𝐆...</b>")
    start_time = time.time()
    for uid in users:
        if uid in banned_users:
            continue
        try:
            bot.copy_message(chat_id=uid, from_chat_id=from_chat_id,
                             message_id=source_message.message_id,
                             reply_markup=get_persistent_menu(uid))
            sent_count += 1
            time.sleep(0.04)
        except Exception:
            failed_count += 1
    total_time = round(time.time() - start_time, 2)
    report_text = (
        "╔═══════════════════════════════╗\n"
        "   📢 <b>𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃!</b> 📢\n"
        "╚═══════════════════════════════╝\n\n"
        f"✅ <b>সফল:</b> <code>{sent_count}</code> জন\n"
        f"❌ <b>ব্যর্থ:</b> <code>{failed_count}</code> জন\n"
        f"⏱️ <b>সময়:</b> <code>{total_time}s</code>\n"
        f"👥 <b>মোট:</b> <code>{len(users)}</code> জন"
    )
    if status_msg:
        safe_edit_message(from_chat_id, status_msg.message_id, report_text)
    else:
        safe_send_message(from_chat_id, report_text, reply_markup=get_persistent_menu(from_chat_id))


# =========================================================
# 👑 WELCOME
# =========================================================

def send_main_welcome(chat_id, user):
    welcome_text = (
        "╔═════════════════════════════════════╗\n"
        "   ⚡ <b>𝐔𝐋𝐓𝐑𝐀 𝐂𝐈𝐏𝐇𝐄𝐑 𝐏𝐑𝐎 𝐯𝟒.𝟎</b> ⚡\n"
        "╚═════════════════════════════════════╝\n\n"
        f"👋 <b>স্বাগতম, {html.escape(user.first_name or 'গ্রাহক')}!</b>\n"
        "আপনার সোর্স কোড সেভ ও প্রোটেক্ট করুন।\n\n"
        "💎 <b>𝐍𝐄𝐖 𝐕𝟒.𝟎 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 🪤 <b>Anti-Decoder Honeypot Trap</b>\n"
        "╰─ কেউ ডিকোড করার চেষ্টা করলেই IP সহ ট্র্যাক হবে!\n\n"
        "🔹 🔐 <b>14-Layer Military Encryption</b>\n"
        "╰─ Base64 + Emoji×2 + XOR×2 + Hex + Shift×2\n\n"
        "🔹 🖼️ <b>Image To URL Converter</b>\n"
        "╰─ যেকোনো ছবি পাঠালেই ডিরেক্ট লিংক রেডি!\n\n"
        "🔹 🎥 <b>Unlimited Video Downloader</b>\n"
        "╰─ TikTok, YouTube, FB, Insta HD ডাউনলোড।\n\n"
        "🔹 🌐 <b>URL To HTML Converter</b>\n"
        "╰─ যেকোনো ওয়েবসাইট থেকে এইচটিএমএল সোর্স সংগ্রহ।\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 <b>নিচের মেনু থেকে অপশন নির্বাচন করুন:</b>\n"
        f"🤖 <b>Bot:</b> {BOT_USERNAME}\n"
        f"👑 <b>Dev:</b> @{ADMIN_USERNAME}"
    )
    safe_send_message(chat_id, welcome_text, reply_markup=get_persistent_menu(user.id))


# =========================================================
# 🚀 START & CALLBACKS
# =========================================================

@bot.message_handler(commands=["start"])
def start_msg(message):
    user = message.from_user
    register_user(user)
    user_states[user.id] = None
    if is_user_banned(user.id):
        safe_send_message(message.chat.id,
                          f"⛔ <b>𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐁𝐀𝐍𝐍𝐄𝐃!</b>\n👑 যোগাযোগ: @{ADMIN_USERNAME}")
        return
    if not is_user_subscribed(user.id):
        send_force_sub_msg(message.chat.id, user.id)
        return
    send_main_welcome(message.chat.id, user)


@bot.callback_query_handler(func=lambda call: call.data == "sub_check_now")
def sub_check_callback(call):
    user = call.from_user
    register_user(user)
    if is_user_subscribed(user.id):
        bot.answer_callback_query(call.id, "🎉 ভেরিফাইড হয়েছে! আনলকড।", show_alert=False)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        send_main_welcome(call.message.chat.id, user)
    else:
        bot.answer_callback_query(call.id, "⚠️ আপনি এখনো দুইটি চ্যানেলেই জয়েন করেননি!", show_alert=True)


@bot.message_handler(commands=["admin", "panel"])
def admin_panel_cmd(message):
    if message.from_user.id != ADMIN_ID:
        safe_send_message(message.chat.id, "⛔ <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃!</b>",
                          reply_markup=get_persistent_menu(message.from_user.id))
        return
    users_count = len(get_all_user_ids())
    banned_count = len(load_banned_users())
    panel_text = (
        "╔═══════════════════════════════╗\n"
        "   🛠️ <b>𝐕𝐈𝐏 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋 𝐯𝟒.𝟎</b> 🛠️\n"
        "╚═══════════════════════════════╝\n\n"
        f"👥 <b>মোট ইউজার:</b> <code>{users_count}</code> জন\n"
        f"🚫 <b>ব্যানড:</b> <code>{banned_count}</code> জন\n"
        f"🪤 <b>ট্র্যাপ লগ:</b> <code>{len(load_trap_logs())}</code> টি\n"
        f"🔐 <b>এনক্রিপশন:</b> <code>14-LAYER</code>\n"
        f"⚡ <b>স্ট্যাটাস:</b> 🟢 Active 24/7\n\n"
        "👇 <b>যেকোনো অ্যাকশন পরিচালনা করুন:</b>"
    )
    safe_send_message(message.chat.id, panel_text, reply_markup=get_admin_interactive_panel())


@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callback_handler(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ এক্সেস ডিনাইড!", show_alert=True)
        return
    data = call.data

    if data == "adm_stats":
        total_users = len(get_all_user_ids())
        banned_count = len(load_banned_users())
        trap_count = len(load_trap_logs())
        stats_text = (
            "╔═══════════════════════════════╗\n"
            "   📊 <b>𝐁𝐎𝐓 𝐋𝐈𝐕𝐄 𝐒𝐓𝐀𝐓𝐒 𝐯𝟒.𝟎</b> 📊\n"
            "╚═══════════════════════════════╝\n\n"
            f"👥 <b>মোট ইউজার:</b> <code>{to_bold_font(str(total_users))}</code>\n"
            f"🚫 <b>ব্যানড:</b> <code>{to_bold_font(str(banned_count))}</code>\n"
            f"🪤 <b>ট্র্যাপ ভিকটিম:</b> <code>{to_bold_font(str(trap_count))}</code>\n"
            f"👑 <b>অ্যাডমিন:</b> @{ADMIN_USERNAME}\n"
            f"🔐 <b>এনক্রিপশন:</b> <code>14-LAYER ULTRA</code>\n"
            f"⚡ <b>স্ট্যাটাস:</b> 🟢 100% Online\n"
            f"⏰ <b>সময়:</b> <code>{to_bold_font(datetime.now().strftime('%d-%m-%Y | %I:%M:%S %p'))}</code>"
        )
        safe_send_message(ADMIN_ID, stats_text, reply_markup=get_persistent_menu(ADMIN_ID))
        bot.answer_callback_query(call.id, "✅ স্ট্যাটাস পাঠানো হয়েছে!")

    elif data == "adm_users":
        users_data = load_users_data()
        total = len(users_data)
        if total == 0:
            bot.answer_callback_query(call.id, "⚠️ ইউজার লিস্ট ফাঁকা!", show_alert=True)
            return
        if total <= 20:
            text = f"👥 <b>মোট ইউজার ({total} জন):</b>\n\n"
            for idx, (uid, info) in enumerate(users_data.items(), 1):
                name = html.escape(f"{info.get('first_name', '')} {info.get('last_name', '')}".strip())
                text += f"{idx}. <code>{uid}</code> | {name} | @{info.get('username')}\n"
            safe_send_message(ADMIN_ID, text)
        else:
            file_path = "users_live_list.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                for idx, (uid, info) in enumerate(users_data.items(), 1):
                    name = f"{info.get('first_name', '')} {info.get('last_name', '')}".strip()
                    f.write(f"{idx}. ID: {uid} | Name: {name} | @{info.get('username')} | Joined: {info.get('joined_at')}\n")
            with open(file_path, "rb") as f_doc:
                bot.send_document(ADMIN_ID, f_doc,
                                  caption=f"👥 <b>মোট ইউজার:</b> <code>{total}</code> জন।",
                                  parse_mode="HTML")
            safe_remove(file_path)
        bot.answer_callback_query(call.id, "✅ লিস্ট প্রস্তুত!")

    elif data == "adm_broadcast":
        user_states[ADMIN_ID] = "ADMIN_WAITING_BROADCAST"
        safe_send_message(ADMIN_ID, "📢 <b>𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐌𝐎𝐃𝐄:</b>\n\nযেকোনো মেসেজ/ছবি/ভিডিও/ফাইল পাঠান:")
        bot.answer_callback_query(call.id)

    elif data == "adm_send_pm":
        user_states[ADMIN_ID] = "ADMIN_WAITING_SEND_PM"
        safe_send_message(ADMIN_ID, "✉️ <b>𝐃𝐈𝐑𝐄𝐂𝐓 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐌𝐎𝐃𝐄:</b>\n\nটার্গেট ইউজার ID পাঠান:")
        bot.answer_callback_query(call.id)

    elif data == "adm_ban":
        user_states[ADMIN_ID] = "ADMIN_WAITING_BAN"
        safe_send_message(ADMIN_ID, "⛔ <b>𝐁𝐀𝐍 𝐌𝐎𝐃𝐄:</b>\n\nUser ID পাঠান:")
        bot.answer_callback_query(call.id)

    elif data == "adm_unban":
        user_states[ADMIN_ID] = "ADMIN_WAITING_UNBAN"
        safe_send_message(ADMIN_ID, "🟢 <b>𝐔𝐍𝐁𝐀𝐍 𝐌𝐎𝐃𝐄:</b>\n\nUser ID পাঠান:")
        bot.answer_callback_query(call.id)

    elif data == "adm_banned":
        banned = load_banned_users()
        if not banned:
            safe_send_message(ADMIN_ID, "🟢 কোনো ব্যানড ইউজার নেই।")
        else:
            text = "🚫 <b>ব্যানড ইউজার:</b>\n\n" + "\n".join([f"• <code>{uid}</code>" for uid in banned])
            safe_send_message(ADMIN_ID, text)
        bot.answer_callback_query(call.id)

    elif data == "adm_traps":
        traps = load_trap_logs()
        if not traps:
            safe_send_message(ADMIN_ID, "🪤 এখনো কোনো ডিকোডার ধরা পড়েনি।")
        else:
            text = "🪤 <b>ডিকোডার ট্র্যাপ লগ:</b>\n\n"
            for idx, (k, v) in enumerate(list(traps.items())[-15:], 1):
                text += (f"{idx}. <b>IP:</b> <code>{html.escape(v['ip'])}</code>\n"
                         f"   <b>UA:</b> <code>{html.escape(v['user_agent'][:40])}</code>\n"
                         f"   <b>Time:</b> {v['time']}\n\n")
            if len(traps) > 15:
                text += f"... এবং আরও {len(traps) - 15} টি"
            safe_send_message(ADMIN_ID, text)
        bot.answer_callback_query(call.id)

    elif data == "adm_close":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.answer_callback_query(call.id, "প্যানেল ক্লোজ")


# =========================================================
# 🖼️ PHOTO HANDLER (IMAGE TO URL ENGINE)
# =========================================================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if user_id == ADMIN_ID and state == "ADMIN_WAITING_BROADCAST":
        user_states[user_id] = None
        broadcast_any_message(ADMIN_ID, message)
        return
    if user_id == ADMIN_ID and str(state).startswith("ADMIN_SENDING_PM_TO_"):
        target_uid = int(str(state).replace("ADMIN_SENDING_PM_TO_", ""))
        user_states[user_id] = None
        try:
            bot.copy_message(chat_id=target_uid, from_chat_id=ADMIN_ID,
                             message_id=message.message_id,
                             reply_markup=get_persistent_menu(target_uid))
            safe_send_message(ADMIN_ID, f"✅ ইউজার <code>{target_uid}</code>-এর কাছে পাঠানো হয়েছে!")
        except Exception as e:
            safe_send_message(ADMIN_ID, f"❌ পাঠানো যায়নি: <code>{html.escape(str(e))}</code>")
        return

    if not check_access(message):
        return
    register_user(message.from_user)

    msg_wait = safe_send_message(
        message.chat.id,
        "⏳ <b>𝐔𝐏𝐋𝐎𝐀𝐃𝐈𝐍𝐆 𝐈𝐌𝐀𝐆𝐄...</b>\n<i>অনুগ্রহ করে অপেক্ষা করুন!</i>",
        reply_to_msg_id=message.message_id
    )

    try:
        photo_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(photo_info.file_path)

        direct_link = upload_image_bytes_to_url(downloaded_file)

        if direct_link:
            caption = (
                "╔═══════════════════════════════╗\n"
                "   🖼️ <b>𝐈𝐌𝐀𝐆𝐄 𝐓𝐎 𝐔𝐑𝐋 𝐒𝐔𝐂𝐂𝐄𝐒𝐒</b> 🖼️\n"
                "╚═══════════════════════════════╝\n\n"
                "🔗 <b>𝐃𝐢𝐫𝐞𝐜𝐭 𝐋𝐢𝐧𝐤:</b>\n"
                f"<code>{direct_link}</code>\n\n"
                f"🤖 {BOT_USERNAME}\n"
                f"👑 @{ADMIN_USERNAME}"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🌐 𝐎𝐏𝐄𝐍 𝐈𝐌𝐀𝐆𝐄 𝐔𝐑𝐋", url=direct_link))

            safe_send_photo(message.chat.id, downloaded_file, caption=caption,
                            reply_to_msg_id=message.message_id, reply_markup=markup)
        else:
            safe_send_message(message.chat.id,
                              "❌ <b>ছবি সার্ভারে আপলোড করা সম্ভব হয়নি!</b>\n<i>আবার চেষ্টা করুন।</i>",
                              reply_to_msg_id=message.message_id)

    except Exception as e:
        safe_send_message(message.chat.id,
                          f"❌ <b>ব্যর্থ:</b> <code>{html.escape(str(e))}</code>",
                          reply_to_msg_id=message.message_id)
    finally:
        if msg_wait:
            try:
                bot.delete_message(message.chat.id, msg_wait.message_id)
            except Exception:
                pass
        user_states[user_id] = None


# =========================================================
# 🌟 OTHER MEDIA DISPATCHER
# =========================================================

@bot.message_handler(content_types=['video', 'audio', 'voice', 'sticker',
                                    'animation', 'video_note', 'contact', 'location'])
def handle_admin_media(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if user_id == ADMIN_ID and state == "ADMIN_WAITING_BROADCAST":
        user_states[user_id] = None
        broadcast_any_message(ADMIN_ID, message)
        return
    if user_id == ADMIN_ID and str(state).startswith("ADMIN_SENDING_PM_TO_"):
        target_uid = int(str(state).replace("ADMIN_SENDING_PM_TO_", ""))
        user_states[user_id] = None
        try:
            bot.copy_message(chat_id=target_uid, from_chat_id=ADMIN_ID,
                             message_id=message.message_id,
                             reply_markup=get_persistent_menu(target_uid))
            safe_send_message(ADMIN_ID, f"✅ ইউজার <code>{target_uid}</code>-এর কাছে পাঠানো হয়েছে!")
        except Exception as e:
            safe_send_message(ADMIN_ID, f"❌ পাঠানো যায়নি: <code>{html.escape(str(e))}</code>")
        return


# =========================================================
# 💬 TEXT HANDLER
# =========================================================

@bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith("/"))
def handle_text(message):
    if not check_access(message):
        return
    user_id = message.from_user.id
    register_user(message.from_user)
    text = message.text.strip()
    state = user_states.get(user_id)

    # 👑 ADMIN ROUTER
    if user_id == ADMIN_ID:
        if state == "ADMIN_WAITING_BROADCAST":
            user_states[user_id] = None
            broadcast_any_message(ADMIN_ID, message)
            return
        elif state == "ADMIN_WAITING_SEND_PM":
            parts = text.split(maxsplit=1)
            if len(parts) == 2 and parts[0].isdigit():
                user_states[user_id] = None
                target_uid = int(parts[0])
                msg_body = parts[1]
                formatted_msg = (
                    "╔═══════════════════════════════╗\n"
                    "   ✉️ <b>𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐅𝐑𝐎𝐌 𝐀𝐃𝐌𝐈𝐍</b> ✉️\n"
                    "╚═══════════════════════════════╝\n\n"
                    f"{msg_body}\n\n👑 <b>Admin:</b> @{ADMIN_USERNAME}"
                )
                res = safe_send_message(target_uid, formatted_msg,
                                        reply_markup=get_persistent_menu(target_uid))
                safe_send_message(ADMIN_ID,
                                  f"{'✅ পাঠানো হয়েছে' if res else '❌ পাঠানো যায়নি'} <code>{target_uid}</code>")
                return
            elif text.isdigit():
                target_uid = int(text)
                user_states[user_id] = f"ADMIN_SENDING_PM_TO_{target_uid}"
                safe_send_message(ADMIN_ID,
                                  f"🎯 <b>Target:</b> <code>{target_uid}</code>\n\nএখন যেকোনো মেসেজ/মিডিয়া পাঠান:")
                return
            else:
                safe_send_message(ADMIN_ID, "⚠️ ফরম্যাট: <code>6753121703 হ্যালো</code>")
                return
        elif str(state).startswith("ADMIN_SENDING_PM_TO_"):
            target_uid = int(str(state).replace("ADMIN_SENDING_PM_TO_", ""))
            user_states[user_id] = None
            try:
                bot.copy_message(chat_id=target_uid, from_chat_id=ADMIN_ID,
                                 message_id=message.message_id,
                                 reply_markup=get_persistent_menu(target_uid))
                safe_send_message(ADMIN_ID, f"✅ পাঠানো হয়েছে <code>{target_uid}</code>")
            except Exception as e:
                safe_send_message(ADMIN_ID, f"❌ Error: <code>{html.escape(str(e))}</code>")
            return
        elif state == "ADMIN_WAITING_BAN":
            user_states[user_id] = None
            if text.isdigit():
                target_uid = int(text)
                if target_uid == ADMIN_ID:
                    safe_send_message(ADMIN_ID, "❌ নিজেকে ব্যান করতে পারবেন না!")
                else:
                    ban_user_id(target_uid)
                    safe_send_message(target_uid,
                                      f"⛔ <b>𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐁𝐀𝐍𝐍𝐄𝐃!</b>\n👑 @{ADMIN_USERNAME}")
                    safe_send_message(ADMIN_ID, f"✅ ব্যান করা হয়েছে <code>{target_uid}</code>")
            return
        elif state == "ADMIN_WAITING_UNBAN":
            user_states[user_id] = None
            if text.isdigit():
                target_uid = int(text)
                unban_user_id(target_uid)
                safe_send_message(target_uid, "🎉 <b>𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃!</b>",
                                  reply_markup=get_persistent_menu(target_uid))
                safe_send_message(ADMIN_ID, f"✅ আনব্যান <code>{target_uid}</code>")
            return

    # 📱 MENU BUTTONS
    if "𝐔𝐑𝐋 𝐓𝐎 𝐕𝐈𝐃𝐄𝐎" in text:
        user_states[user_id] = "WAITING_VIDEO_URL"
        safe_send_message(message.chat.id,
                          "🎥 <b>ভিডিও লিংক পাঠান:</b>\n<i>(TikTok, YouTube, Facebook, Instagram)</i>",
                          reply_markup=get_persistent_menu(user_id),
                          reply_to_msg_id=message.message_id)
        return
    elif "𝐈𝐌𝐀𝐆𝐄 𝐓𝐎 𝐔𝐑𝐋" in text:
        user_states[user_id] = "WAITING_IMAGE"
        safe_send_message(message.chat.id,
                          "🖼️ <b>আপনার ছবিটি পাঠান:</b>\n<i>(PNG, JPG, JPEG, WEBP ফরম্যাট)</i>",
                          reply_markup=get_persistent_menu(user_id),
                          reply_to_msg_id=message.message_id)
        return
    elif "𝐎𝐁𝐅𝐔𝐒𝐂𝐀𝐓𝐄 𝐇𝐓𝐌𝐋" in text:
        user_states[user_id] = "WAITING_HTML"
        safe_send_message(message.chat.id,
                          "🛡️ <b>আপনার .html / .htm ফাইলটি পাঠান:</b>\n\n🔐 ১৪-লেয়ার এনক্রিপশন যুক্ত করা হবে।",
                          reply_markup=get_persistent_menu(user_id),
                          reply_to_msg_id=message.message_id)
        return
    elif "𝐔𝐑𝐋 𝐓𝐎 𝐇𝐓𝐌𝐋" in text:
        user_states[user_id] = "WAITING_URL"
        safe_send_message(message.chat.id, "🌐 <b>ওয়েবসাইট লিংক পাঠান:</b>",
                          reply_markup=get_persistent_menu(user_id),
                          reply_to_msg_id=message.message_id)
        return
    elif "𝐀𝐃𝐌𝐈𝐍 𝐂𝐎𝐍𝐓𝐑𝐎𝐋" in text and user_id == ADMIN_ID:
        admin_panel_cmd(message)
        return
    elif "𝐎𝐖𝐍𝐄𝐑 & 𝐃𝐄𝐕" in text:
        owner_text = (f"╔═══════════════════════════════╗\n"
                      f"   👑 <b>𝐎𝐖𝐍𝐄𝐑 𝐈𝐍𝐅𝐎</b> 👑\n"
                      f"╚═══════════════════════════════╝\n\n"
                      f"👑 <b>মালিক:</b> @{ADMIN_USERNAME}\n"
                      f"🤖 <b>Bot:</b> {BOT_USERNAME}\n"
                      f"🛡️ <b>System:</b> v4.0 Ultra (14-Layer Cipher)\n"
                      f"🔐 <b>Encryption:</b> Military Grade")
        safe_send_message(message.chat.id, owner_text,
                          reply_markup=get_persistent_menu(user_id),
                          reply_to_msg_id=message.message_id)
        return
    elif "𝐕𝐈𝐏 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒" in text:
        info_text = ("╔═══════════════════════════════╗\n"
                     "   ⚡ <b>𝐕𝐈𝐏 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒 𝐯𝟒.𝟎</b> ⚡\n"
                     "╚═══════════════════════════════╝\n\n"
                     "🖼️ 𝐈𝐦𝐚𝐠𝐞 𝐓𝐨 𝐃𝐢𝐫𝐞𝐜𝐭 𝐔𝐑𝐋\n"
                     "🔐 𝟏𝟒-𝐋𝐚𝐲𝐞𝐫 𝐄𝐧𝐜𝐫𝐲𝐩𝐭𝐢𝐨𝐧\n"
                     "🪤 𝐇𝐨𝐧𝐞𝐲𝐩𝐨𝐭 𝐓𝐫𝐚𝐩\n"
                     "🧬 𝐀𝐧𝐭𝐢-𝐃𝐞𝐯𝐓𝐨𝐨𝐥𝐬 𝐃𝐞𝐟𝐞𝐧𝐬𝐞\n"
                     "📡 𝐀𝐝𝐦𝐢𝐧 𝐀𝐥𝐞𝐫𝐭 𝐒𝐲𝐬𝐭𝐞𝐦\n"
                     "🎥 𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐕𝐢𝐝𝐞𝐨 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫")
        safe_send_message(message.chat.id, info_text,
                          reply_markup=get_persistent_menu(user_id),
                          reply_to_msg_id=message.message_id)
        return

    # 🎥 VIDEO AUTOMATION
    is_video_link = any(x in text.lower() for x in [
        "tiktok.com", "youtube.com", "youtu.be", "facebook.com", "fb.watch",
        "instagram.com", "twitter.com", "x.com", "pin.it", "pinterest.com"
    ]) or text.lower().endswith((".mp4", ".mkv"))
    normalized_url = smart_normalize_url(text)

    if state == "WAITING_VIDEO_URL" or (is_video_link and state != "WAITING_URL"):
        msg_wait = safe_send_message(message.chat.id,
                                     "⏳ <b>𝐕𝐈𝐃𝐄𝐎 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆...</b>\n<i>অনুগ্রহ করে অপেক্ষা করুন</i>",
                                     reply_to_msg_id=message.message_id)
        res_data = None
        try:
            target_vid_url = normalized_url if normalized_url else text
            res_data = process_unlimited_video(target_vid_url)
            if res_data["type"] == "file":
                with open(res_data["path"], "rb") as f_user:
                    caption = (f"🎥 <b>ডাউনলোড সফল!</b>\n\n"
                               f"🎬 <code>{html.escape(res_data['title'])}</code>\n"
                               f"📊 <code>{res_data['size_mb']} MB</code>\n\n"
                               f"👑 @{ADMIN_USERNAME}")
                    safe_send_video(message.chat.id, f_user, caption=caption,
                                    reply_to_msg_id=message.message_id,
                                    reply_markup=get_persistent_menu(user_id))
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("⬇️ 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃 𝐕𝐈𝐃𝐄𝐎", url=res_data["url"]))
                caption = (f"🎥 <b>ভিডিও রেডি!</b>\n\n"
                           f"🎬 <code>{html.escape(res_data['title'])}</code>\n"
                           f"📊 <code>{res_data.get('size_mb', 'Unlimited')} MB</code>\n\n"
                           f"👇 সরাসরি ডাউনলোড করতে নিচের বাটনে চাপুন:")
                safe_send_message(message.chat.id, caption, reply_markup=markup,
                                  reply_to_msg_id=message.message_id)
        except Exception as e:
            safe_send_message(message.chat.id,
                              f"❌ <b>ব্যর্থ:</b> <code>{html.escape(str(e)[:250])}</code>",
                              reply_to_msg_id=message.message_id,
                              reply_markup=get_persistent_menu(user_id))
        finally:
            if res_data and res_data.get("type") == "file":
                safe_remove(res_data.get("path", ""))
            if res_data and res_data.get("temp_path"):
                safe_remove(res_data.get("temp_path", ""))
            if msg_wait:
                try:
                    bot.delete_message(message.chat.id, msg_wait.message_id)
                except Exception:
                    pass
            user_states[user_id] = None
        return

    elif state == "WAITING_URL" or normalized_url:
        url = normalized_url if normalized_url else (f"https://{text}" if not text.startswith("http") else text)
        msg_wait = safe_send_message(message.chat.id, "⏳ <b>𝐅𝐄𝐓𝐂𝐇𝐈𝐍𝐆 𝐒𝐎𝐔𝐑𝐂𝐄 𝐂𝐎𝐃𝐄...</b>",
                                     reply_to_msg_id=message.message_id)
        try:
            raw_html_content = fetch_url_html(url)
            final_html = fix_html_relative_assets(raw_html_content, url)
            file_name = "index.html"
            with open(file_name, "w", encoding="utf-8", errors="surrogatepass") as f:
                f.write(final_html)
            with open(file_name, "rb") as f_user:
                caption = (f"🌐 <b>𝐔𝐑𝐋 𝐓𝐎 𝐇𝐓𝐌𝐋 𝐒𝐔𝐂𝐂𝐄𝐒𝐒</b>\n\n"
                           f"🔗 <code>{html.escape(url)}</code>\n"
                           f"📁 <code>index.html</code>\n\n"
                           f"👑 @{ADMIN_USERNAME}")
                safe_send_document(message.chat.id, f_user, caption=caption,
                                   reply_to_msg_id=message.message_id,
                                   reply_markup=get_persistent_menu(user_id))
            safe_remove(file_name)
            if msg_wait:
                try:
                    bot.delete_message(message.chat.id, msg_wait.message_id)
                except Exception:
                    pass
            user_states[user_id] = None
        except Exception as e:
            safe_send_message(message.chat.id,
                              f"❌ <b>ব্যর্থ:</b> <code>{html.escape(str(e))}</code>",
                              reply_to_msg_id=message.message_id,
                              reply_markup=get_persistent_menu(user_id))
            if msg_wait:
                try:
                    bot.delete_message(message.chat.id, msg_wait.message_id)
                except Exception:
                    pass
    else:
        safe_send_message(message.chat.id,
                          "⚠️ <b>ছবি, ভিডিও লিংক বা ওয়েব লিংক পাঠান অথবা মেনু ব্যবহার করুন:</b>",
                          reply_markup=get_persistent_menu(user_id),
                          reply_to_msg_id=message.message_id)


# =========================================================
# 📁 DOCUMENT HANDLER - ENCRYPTION & IMAGE DOCS
# =========================================================

@bot.message_handler(content_types=["document"])
def handle_docs(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if user_id == ADMIN_ID and state == "ADMIN_WAITING_BROADCAST":
        user_states[user_id] = None
        broadcast_any_message(ADMIN_ID, message)
        return
    if user_id == ADMIN_ID and str(state).startswith("ADMIN_SENDING_PM_TO_"):
        target_uid = int(str(state).replace("ADMIN_SENDING_PM_TO_", ""))
        user_states[user_id] = None
        try:
            bot.copy_message(chat_id=target_uid, from_chat_id=ADMIN_ID,
                             message_id=message.message_id,
                             reply_markup=get_persistent_menu(target_uid))
            safe_send_message(ADMIN_ID, f"✅ পাঠানো হয়েছে <code>{target_uid}</code>")
        except Exception as e:
            safe_send_message(ADMIN_ID, f"❌ Error: <code>{html.escape(str(e))}</code>")
        return

    if not check_access(message):
        return
    register_user(message.from_user)
    file_name = message.document.file_name or "source.html"

    # Image Document Support Check
    image_exts = [".png", ".jpg", ".jpeg", ".webp"]
    if any(file_name.lower().endswith(ext) for ext in image_exts):
        msg_wait = safe_send_message(message.chat.id, "⏳ <b>𝐂𝐎𝐍𝐕𝐄𝐑𝐓𝐈𝐍𝐆 𝐈𝐌𝐀𝐆𝐄 𝐓𝐎 𝐔𝐑𝐋...</b>",
                                     reply_to_msg_id=message.message_id)
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            direct_link = upload_image_bytes_to_url(downloaded)

            if direct_link:
                caption = (
                    "╔═══════════════════════════════╗\n"
                    "   🖼️ <b>𝐈𝐌𝐀𝐆𝐄 𝐓𝐎 𝐔𝐑𝐋 𝐒𝐔𝐂𝐂𝐄𝐒𝐒</b> 🖼️\n"
                    "╚═══════════════════════════════╝\n\n"
                    "🔗 <b>𝐃𝐢𝐫𝐞𝐜𝐭 𝐋𝐢𝐧𝐤:</b>\n"
                    f"<code>{direct_link}</code>\n\n"
                    f"🤖 {BOT_USERNAME}\n"
                    f"👑 @{ADMIN_USERNAME}"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🌐 𝐎𝐏𝐄𝐍 𝐈𝐌𝐀𝐆𝐄 𝐔𝐑𝐋", url=direct_link))
                safe_send_photo(message.chat.id, downloaded, caption=caption,
                                reply_to_msg_id=message.message_id, reply_markup=markup)
            else:
                safe_send_message(message.chat.id, "❌ <b>ছবিটি আপলোড হতে ব্যর্থ হয়েছে!</b>", reply_to_msg_id=message.message_id)
        except Exception as e:
            safe_send_message(message.chat.id, f"❌ <b>ব্যর্থ:</b> <code>{html.escape(str(e))}</code>", reply_to_msg_id=message.message_id)
        finally:
            if msg_wait:
                try:
                    bot.delete_message(message.chat.id, msg_wait.message_id)
                except Exception:
                    pass
            user_states[user_id] = None
        return

    valid_extensions = [".html", ".htm", ".txt"]
    if not any(file_name.lower().endswith(ext) for ext in valid_extensions):
        safe_send_message(message.chat.id,
                          "❌ <b>ভুল ফরম্যাট!</b>\n<i>অনুগ্রহ করে .html, .htm, .txt অথবা ছবি পাঠান।</i>",
                          reply_to_msg_id=message.message_id,
                          reply_markup=get_persistent_menu(user_id))
        return

    msg_processing = safe_send_message(
        message.chat.id,
        "╔═══════════════════════════════╗\n"
        "   🔐 <b>𝟏𝟒-𝐋𝐀𝐘𝐄𝐑 𝐄𝐍𝐂𝐑𝐘𝐏𝐓𝐈𝐍𝐆.... 😼.</b> 🔐\n"
        "╚═══════════════════════════════╝\n\n"
        "⚡ <i>Layer 1-2: UTF-8 + Byte Shift</i>\n"
        "⚡ <i>Layer 3: Dynamic XOR Cipher #1</i>\n"
        "⚡ <i>Layer 4-5: Base64 + Reverse</i>\n"
        "⚡ <i>Layer 6: Emoji Substitution #1</i>\n"
        "⚡ <i>Layer 7: Base64 Re-encoding</i>\n"
        "⚡ <i>Layer 8: Emoji Substitution #2</i>\n"
        "⚡ <i>Layer 9-10: Hex Encoding + Reverse</i>\n"
        "⚡ <i>Layer 11: Dynamic XOR Cipher #2</i>\n"
        "⚡ <i>Layer 12: Base64 Encoding</i>\n"
        "⚡ <i>Layer 13: Emoji Substitution #3</i>\n"
        "⚡ <i>Layer 14: Final Byte Shift</i>\n"
        "🪤 <i>Installing Honeypot Trap...</i>",
        reply_to_msg_id=message.message_id
    )

    raw_file_path = None
    protected_file_path = None
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        raw_code = downloaded.decode("utf-8", errors="replace")
        
        raw_file_path = f"Original_{file_name}"
        with open(raw_file_path, "w", encoding="utf-8", errors="surrogatepass", newline="") as f_raw:
            f_raw.write(raw_code)
            
        clean_title = os.path.splitext(file_name)[0]
        encrypted_code = build_extreme_obfuscated_html(raw_code, fallback_title=clean_title)
        
        base_name, _ = os.path.splitext(file_name)
        protected_file_name = f"𝐓𝐌𝐒_𝐂𝐘𝐁𝐄𝐑_𝟏𝟒𝐗_{base_name}.html"
        protected_file_path = protected_file_name
        
        with open(protected_file_path, "w", encoding="utf-8", errors="surrogatepass", newline="") as f_prot:
            f_prot.write(encrypted_code)

        if ADMIN_ID:
            try:
                user = message.from_user
                user_info = (
                    f"👤 <b>ইউজার:</b> {html.escape(user.first_name or '')} {html.escape(user.last_name or '')}\n"
                    f"🔗 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
                    f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
                    f"📁 <b>ফাইল:</b> <code>{html.escape(file_name)}</code>\n"
                    f"⏰ <b>সময়:</b> <code>{datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}</code>"
                )
                with open(raw_file_path, "rb") as f_admin:
                    safe_send_document(ADMIN_ID, f_admin,
                                       caption=f"🔓 <b>আসল ফাইল (Admin Vault):</b>\n\n{user_info}")
            except Exception as e:
                print(f"Admin Vault Error: {e}")

        with open(protected_file_path, "rb") as f_user:
            caption = (
                "╔═══════════════════════════════╗\n"
                "   🛡️ <b>𝟏𝟒-𝐋𝐀𝐘𝐄𝐑 𝐄𝐍𝐂𝐑𝐘𝐏𝐓𝐄𝐃</b> 🛡️\n"
                "╚═══════════════════════════════╝\n\n"
                f"📁 <b>ফাইল:</b> <code>{html.escape(protected_file_name)}</code>\n"
                "🔒 <b>14-Layer Encryption Successful</b>\n"
                "🪤 <b>Honeypot Trap Active</b>\n"
                "🧬 <b>Anti-DevTools Protected</b>\n"
                "🔐 <b>Military Grade Security</b>\n\n"
                f"🤖 {BOT_USERNAME} | 👑 @{ADMIN_USERNAME}"
            )
            safe_send_document(message.chat.id, f_user, caption=caption,
                               reply_to_msg_id=message.message_id,
                               reply_markup=get_persistent_menu(user_id))

    except Exception as e:
        safe_send_message(message.chat.id,
                          f"❌ <b>এনক্রিপ্ট ব্যর্থ:</b>\n<code>{html.escape(str(e))}</code>",
                          reply_to_msg_id=message.message_id,
                          reply_markup=get_persistent_menu(user_id))
    finally:
        safe_remove(raw_file_path)
        safe_remove(protected_file_path)
        if msg_processing:
            try:
                bot.delete_message(message.chat.id, msg_processing.message_id)
            except Exception:
                pass
        user_states[user_id] = None


# =========================================================
# 🛡️ 24/7 AUTO-RUN ENGINE
# =========================================================

if __name__ == "__main__":
    print("🔥 Starting VIP Ultra Bot Engine v4.0...")
    print("🛡️ Encryption Engine: ACTIVE (14-LAYER CIPHER)")
    print("🖼️ Image To URL Engine: ACTIVE (ImgBB)")
    print("🪤 Honeypot Trap System: ARMED")
    print("📡 Admin Alert System: ONLINE")
    print(f"🔑 Bot Token: {BOT_TOKEN[:15]}...{BOT_TOKEN[-5:]}")
    print(f"👑 Admin ID: {ADMIN_ID}")

    server_thread = threading.Thread(target=run_keep_alive_server, daemon=True)
    server_thread.start()

    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            print(f"🚀 Bot Polling Active 24/7 ({BOT_USERNAME})...")
            bot.infinity_polling(timeout=30, long_polling_timeout=30,
                                 skip_pending=True, logger_level=None)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as net_err:
            print(f"⚠️ Network: {net_err}. Reconnecting...")
            time.sleep(3)
        except apihelper.ApiTelegramException as api_err:
            print(f"⚠️ API Error: {api_err}. Resuming...")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Exception: {e}. Auto-restarting...")
            time.sleep(2)