from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import re
import requests
import phonenumbers
import ipaddress
import platform
import socket
import psutil
import os
import time
from phonenumbers import geocoder, carrier, timezone
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8461665900:AAHPBDgVtZ1Pd9-TxTCOBtAgIyU8N_VBfLA")
# Set env: export BOT_TOKEN="your_token"

CHANNEL_USERNAME = "@h4cker_pro"
CHANNEL_LINK = "https://t.me/h4cker_pro"

ADMIN_ID = 8418148020

# Simple in-memory stats (resets on restart; swap for a DB if you need persistence)
BOT_START_TIME = datetime.now()
START_TIME = time.time()
KNOWN_USERS = set()
MESSAGE_COUNT = 0

# ---------------- MENU ----------------
menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🏦 IFSC Lookup")],
        [KeyboardButton("📱 Mobile Validation")],
        [KeyboardButton("🚗 Vehicle Information 2")],
        [KeyboardButton("🛻 Vehicle Info")],  # New Button
        [KeyboardButton("🪪 PAN Validation")],
        [KeyboardButton("🧾 GST Validation")],
        [KeyboardButton("🪪 Aadhaar Validation")],
        [KeyboardButton("💳 UPI Validation")],
        [KeyboardButton("👤 My Info")],
        [KeyboardButton("🌐 IP Lookup")],
        [KeyboardButton("📮 PIN Code Lookup")],
        [KeyboardButton("🇵🇰 Pakistan Number Info")],
        [KeyboardButton("🎮 Free Fire UID")],
        [KeyboardButton("🔍 Full Number Info")],
        [KeyboardButton("📧 Email Info")],
        [KeyboardButton("📱 IMEI Info")],
        [KeyboardButton("🐙 GitHub Info")],
        [KeyboardButton("🌐 Website Info")],
        [KeyboardButton("📸 Instagram Username")],
        [KeyboardButton("🚨 Challan Info")],
    ],
    resize_keyboard=True,
)

# ---------------- VEHICLE DATA - FIXED & MATCHED WITH NEW CODE ----------------
STATES = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "CH": "Chandigarh",
    "DD": "Dadra and Nagar Haveli and Daman and Diu",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JH": "Jharkhand",
    "JK": "Jammu and Kashmir",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "MN": "Manipur",
    "MP": "Madhya Pradesh",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PB": "Punjab",
    "PY": "Puducherry",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TR": "Tripura",
    "TS": "Telangana",
    "UK": "Uttarakhand",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
}
STATE_CODES = STATES  # backward compatibility
VEHICLE_PATTERN = r"^([A-Z]{2})(\d{1,2})([A-Z]{1,3})(\d{1,4})$"

# ---------------- PAN DATA ----------------
PAN_PATTERN = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

PAN_HOLDER_TYPES = {
    "P": "Individual",
    "C": "Company",
    "H": "HUF",
    "F": "Firm",
    "A": "Association of Persons (AOP)",
    "T": "Trust",
    "B": "Body of Individuals (BOI)",
    "L": "Local Authority",
    "J": "Artificial Juridical Person",
    "G": "Government",
}

# ---------------- GST DATA ----------------
GST_PATTERN = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$"

GST_STATE_CODES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "27": "Maharashtra", "29": "Karnataka", "32": "Kerala",
    "33": "Tamil Nadu", "36": "Telangana", "37": "Andhra Pradesh",
}

# ---------------- AADHAAR DATA ----------------
# UIDAI rule: 12 digits, first digit cannot be 0 or 1
AADHAAR_PATTERN = r"^[2-9]\d{11}$"

# ---------------- UPI DATA ----------------
UPI_PATTERN = r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$"

# ---------------- FREE FIRE UID DATA ----------------
UID_PATTERN = r"^\d{8,12}$"

# ---------------- PHONE NUMBER TYPES ----------------
PHONE_TYPES = {
    phonenumbers.PhoneNumberType.MOBILE: "Mobile",
    phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line / Mobile",
    phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
    phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
    phonenumbers.PhoneNumberType.VOIP: "VoIP",
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
    phonenumbers.PhoneNumberType.PAGER: "Pager",
    phonenumbers.PhoneNumberType.UAN: "UAN",
    phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
}

# ---------------- EMAIL DATA ----------------
EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

EMAIL_PROVIDERS = {
    "gmail.com": "Google Gmail",
    "yahoo.com": "Yahoo Mail",
    "outlook.com": "Microsoft Outlook",
    "hotmail.com": "Microsoft Hotmail",
    "live.com": "Microsoft Live",
    "icloud.com": "Apple iCloud",
    "proton.me": "Proton Mail",
    "protonmail.com": "Proton Mail",
    "zoho.com": "Zoho Mail",
}

# ---------------- INSTAGRAM DATA ----------------
INSTAGRAM_USERNAME_PATTERN = r"^[A-Za-z0-9._]{1,30}$"


# ---------------- IMEI HELPERS ----------------
def luhn_check(imei):
    total = 0
    reverse = imei[::-1]

    for i, digit in enumerate(reverse):
        n = int(digit)

        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9

        total += n

    return total % 10 == 0


# ---------------- FORCE SUBSCRIBE ----------------
async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


NOT_JOINED_MSG = f"""⚠️ You must join our channel first.

📢 {CHANNEL_LINK}

After joining, send /start again.
"""


# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    KNOWN_USERS.add(user.id)

    if not await is_joined(context.bot, user.id):
        await update.message.reply_text(NOT_JOINED_MSG)
        return

    context.user_data.clear()
    await update.message.reply_text(
        f"✅ Welcome {user.first_name}!\n\n🤖 Select an option.",
        reply_markup=menu,
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MESSAGE_COUNT
    user = update.effective_user
    text = update.message.text.strip()

    KNOWN_USERS.add(user.id)
    MESSAGE_COUNT += 1

    if not await is_joined(context.bot, user.id):
        await update.message.reply_text(NOT_JOINED_MSG)
        return

    # ---- Menu selections ----
    if text == "🏦 IFSC Lookup":
        context.user_data.clear()
        context.user_data["mode"] = "ifsc"
        await update.message.reply_text("Send IFSC Code\nExample:\nSBIN0000001")
        return

    if text == "📱 Mobile Validation":
        context.user_data.clear()
        context.user_data["mode"] = "mobile"
        await update.message.reply_text("Send Number\nExample:\n+919876543210")
        return

    if text in ["🚗 Vehicle Info", "🚗 Vehicle Information 2"]:
        context.user_data.clear()
        context.user_data["mode"] = "vehicle"
        await update.message.reply_text("Send Vehicle Number\nExample:\nWB24AB1234")
        return

    if text == "🪪 PAN Validation":
        context.user_data.clear()
        context.user_data["mode"] = "pan"
        await update.message.reply_text("Send PAN Number\nExample:\nABCDE1234F")
        return

    if text == "🧾 GST Validation":
        context.user_data.clear()
        context.user_data["mode"] = "gst"
        await update.message.reply_text("Send GSTIN\nExample:\n27ABCDE1234F1Z5")
        return

    if text == "🪪 Aadhaar Validation":
        context.user_data.clear()
        context.user_data["mode"] = "aadhaar"
        await update.message.reply_text("Send 12-digit Aadhaar Number")
        return

    if text == "💳 UPI Validation":
        context.user_data.clear()
        context.user_data["mode"] = "upi"
        await update.message.reply_text("Send UPI ID\nExample:\nusername@upi")
        return

    if text == "👤 My Info":
        context.user_data.clear()

        username = f"@{user.username}" if user.username else "Not Set"

        msg = f"""👤 TELEGRAM INFORMATION

🆔 User ID : {user.id}
👤 First Name : {user.first_name}
👥 Last Name : {user.last_name or 'N/A'}
🔗 Username : {username}
🤖 Is Bot : {user.is_bot}
🌐 Language Code : {user.language_code or 'Unknown'}
💬 Chat ID : {update.effective_chat.id}
📋 Chat Type : {update.effective_chat.type}
"""
        await update.message.reply_text(msg)
        return

    if text == "🌐 IP Lookup":
        context.user_data.clear()
        context.user_data["mode"] = "ip"
        await update.message.reply_text("Send an IPv4 or IPv6 address\nExample:\n8.8.8.8")
        return

    if text == "📮 PIN Code Lookup":
        context.user_data.clear()
        context.user_data["mode"] = "pincode"
        await update.message.reply_text("Send a 6-digit Indian PIN Code\nExample:\n741101")
        return

    if text == "🇵🇰 Pakistan Number Info":
        context.user_data.clear()
        context.user_data["mode"] = "pk_number"
        await update.message.reply_text("Send a Pakistan mobile number\nExample:\n+923001234567")
        return

    if text == "🎮 Free Fire UID":
        context.user_data.clear()
        context.user_data["mode"] = "ff_uid"
        await update.message.reply_text("Send a Free Fire UID\nExample:\n123456789")
        return

    if text == "🔍 Full Number Info":
        context.user_data.clear()
        context.user_data["mode"] = "full_number"
        await update.message.reply_text(
            "Send a phone number with country code\nExample:\n+919876543210"
        )
        return

    if text == "📧 Email Info":
        context.user_data.clear()
        context.user_data["mode"] = "email"
        await update.message.reply_text("Send an email address\nExample:\nexample@gmail.com")
        return

    if text == "📱 IMEI Info":
        context.user_data.clear()
        context.user_data["mode"] = "imei"
        await update.message.reply_text("Send a 15-digit IMEI number\nExample:\n356938035643809")
        return

    if text == "🐙 GitHub Info":
        context.user_data.clear()
        context.user_data["mode"] = "github"
        await update.message.reply_text("Send a GitHub username\nExample:\ntorvalds")
        return

    if text == "🌐 Website Info":
        context.user_data.clear()
        context.user_data["mode"] = "website"
        await update.message.reply_text("Send a website URL\nExample:\nhttps://example.com")
        return

    if text == "📸 Instagram Username":
        context.user_data.clear()
        context.user_data["mode"] = "instagram"
        await update.message.reply_text("Send an Instagram username\nExample:\ninstagram")
        return

    if text == "🚨 Challan Info":
        context.user_data.clear()
        context.user_data["mode"] = "challan"
        await update.message.reply_text("Send your vehicle number\nExample:\nWB24AB1234")
        return

    if text == "💻 Device Info":
        context.user_data.clear()
        if user.id != ADMIN_ID:
            await update.message.reply_text("❌ Access Denied")
            return
        await update.message.reply_text(build_device_info_text())
        return

    if text == "🏓 Ping":
        context.user_data.clear()
        await update.message.reply_text("🏓 Pong! Bot is online.")
        return

    if text == "❌ Close":
        context.user_data.clear()
        await update.message.reply_text("👋 Menu closed. Send /start to open it again.")
        return

    mode = context.user_data.get("mode")

    # ---- IFSC ----
    if mode == "ifsc":
        code = text.upper().replace(" ", "")

        if len(code) != 11:
            await update.message.reply_text("❌ Invalid IFSC (must be 11 characters)")
            return

        try:
            r = requests.get(f"https://ifsc.razorpay.com/{code}", timeout=10)

            if r.status_code != 200:
                await update.message.reply_text("❌ IFSC Not Found")
                context.user_data.clear()
                return

            d = r.json()

            msg = f"""🏦 BANK DETAILS

🏦 Bank : {d.get("BANK")}
🏢 Branch : {d.get("BRANCH")}
🔑 IFSC : {d.get("IFSC")}
🔢 MICR : {d.get("MICR")}
📍 Address : {d.get("ADDRESS")}
🏙 City : {d.get("CITY")}
🗺 District : {d.get("DISTRICT")}
🌍 State : {d.get("STATE")}
☎ Contact : {d.get("CONTACT") or "N/A"}

💸 NEFT : {"Yes" if d.get("NEFT") else "No"}
💳 RTGS : {"Yes" if d.get("RTGS") else "No"}
⚡ IMPS : {"Yes" if d.get("IMPS") else "No"}
"""
            await update.message.reply_text(msg)

        except Exception:
            await update.message.reply_text("❌ Network Error")

        context.user_data.clear()
        return

    # ---- MOBILE ----
    if mode == "mobile":
        try:
            parsed = phonenumbers.parse(text, "IN")

            if not phonenumbers.is_possible_number(parsed):
                await update.message.reply_text("❌ Invalid Number")
                context.user_data.clear()
                return

            phone_type = PHONE_TYPES.get(phonenumbers.number_type(parsed), "Unknown")

            msg = f"""📱 MOBILE INFORMATION

☎ Number : {text}
🌍 Region : {geocoder.description_for_number(parsed, 'en')}
📡 Carrier : {carrier.name_for_number(parsed, 'en') or "Unknown"}
🏷 Number Type : {phone_type}
🔢 Country Code : +{parsed.country_code}
🔢 National Number : {parsed.national_number}

✅ Valid : {phonenumbers.is_valid_number(parsed)}
✅ Possible : {phonenumbers.is_possible_number(parsed)}

🏠 National :
{phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)}

🌐 International :
{phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}

📌 E164 :
{phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)}
"""
            await update.message.reply_text(msg)

        except Exception:
            await update.message.reply_text("❌ Invalid Number")

        context.user_data.clear()
        return

    # ---- VEHICLE - FIXED WITH NEW DESIGN (MATCHED) ----
    if mode == "vehicle":
        code = text.replace(" ", "").upper()
        m = re.match(VEHICLE_PATTERN, code)

        if not m:
            await update.message.reply_text(
                "❌ Invalid Vehicle Number\n\nExample:\nWB93B4060"
            )
            context.user_data.clear()
            return

        state_code, rto, series, number = m.groups()
        state = STATES.get(state_code, "Unknown")
        now = datetime.now()

        msg = f"""
🚗 VEHICLE PLATE FORMAT
━━━━━━━━━━━━━━━━━━━━━━

🚘 Vehicle Number      : {code}
🌍 Country             : India
📌 State               : {state}
🏷 State Code          : {state_code}
🏢 RTO Code            : {state_code}{rto}
🔤 Series              : {series}
🔢 Registration Number : {number}

📋 Format Status       : Valid
🔤 Full Pattern        : {state_code}-{rto}-{series}-{number}

📅 Scan Date           : {now.strftime('%d-%m-%Y')}
⏰ Scan Time           : {now.strftime('%I:%M:%S %p')}
🌏 Time Zone           : Asia/Kolkata
🐍 Python Version      : {platform.python_version()}
━━━━━━━━━━━━━━━━━━━━━━
Note: this only decodes the plate format (state/RTO/series).
It is not connected to any vehicle registry — no ownership,
insurance, or RC data is looked up.
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- PAN ----
    if mode == "pan":
        pan = text.replace(" ", "").upper()

        if not re.fullmatch(PAN_PATTERN, pan):
            await update.message.reply_text(
                "❌ Invalid PAN format.\n\nExample: ABCDE1234F"
            )
            context.user_data.clear()
            return

        holder_type = PAN_HOLDER_TYPES.get(pan[3], "Unknown")

        msg = f"""🪪 PAN INFORMATION

PAN : {pan}
✅ Format : Valid
📄 Holder Type : {holder_type}
🔤 First 5 Characters : {pan[:5]}
🔢 Numeric Part : {pan[5:9]}
🔠 Last Character : {pan[9]}
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- GST ----
    if mode == "gst":
        gst = text.replace(" ", "").upper()

        if not re.fullmatch(GST_PATTERN, gst):
            await update.message.reply_text("❌ Invalid GSTIN format.")
            context.user_data.clear()
            return

        state_code = gst[:2]
        pan = gst[2:12]
        entity = gst[12]
        default_z = gst[13]
        checksum = gst[14]
        state = GST_STATE_CODES.get(state_code, "Unknown")

        msg = f"""🧾 GST INFORMATION

GSTIN : {gst}
✅ Format : Valid
🌍 State : {state}
🏷 State Code : {state_code}
🪪 PAN Part : {pan}
🏢 Entity Code : {entity}
🔤 Default Char : {default_z}
🔑 Checksum : {checksum}
📏 Length : {len(gst)}
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- AADHAAR ----
    if mode == "aadhaar":
        aadhaar = text.replace(" ", "")

        if not re.fullmatch(AADHAAR_PATTERN, aadhaar):
            await update.message.reply_text(
                "❌ Invalid Aadhaar format.\n\n"
                "Aadhaar must be exactly 12 digits and cannot start with 0 or 1."
            )
            context.user_data.clear()
            return

        msg = f"""🪪 AADHAAR VALIDATION

🔢 Digits : 12
📏 Length : {len(aadhaar)}
✅ Format : Valid
🌍 Country : India
🔒 Privacy : No personal data accessed
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- UPI ----
    if mode == "upi":
        upi = text.replace(" ", "")

        if not re.fullmatch(UPI_PATTERN, upi):
            await update.message.reply_text("❌ Invalid UPI ID format.")
            context.user_data.clear()
            return

        username, handle = upi.split("@", 1)

        msg = f"""💳 UPI INFORMATION

🆔 UPI ID : {upi}
👤 Username : {username}
🏦 Handle : {handle}
📏 Length : {len(upi)}
✅ Format : Valid
🔒 Verification : Format Only
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- IP LOOKUP ----
    if mode == "ip":
        ip = text.replace(" ", "")

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            await update.message.reply_text("❌ Invalid IP address.")
            context.user_data.clear()
            return

        try:
            r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            data = r.json()

            if data.get("status") != "success":
                await update.message.reply_text("❌ IP information not found.")
                context.user_data.clear()
                return

            msg = f"""🌐 IP INFORMATION

📌 IP Address : {data.get('query')}
🌍 Country : {data.get('country')}
🏳 Country Code : {data.get('countryCode')}
🗺 Region : {data.get('regionName')}
🏙 City : {data.get('city')}
📮 ZIP Code : {data.get('zip')}
🕒 Time Zone : {data.get('timezone')}
📡 ISP : {data.get('isp')}
🏢 Organization : {data.get('org')}
🔢 ASN : {data.get('as')}
📍 Latitude : {data.get('lat')}
📍 Longitude : {data.get('lon')}
"""
            await update.message.reply_text(msg)

        except requests.RequestException:
            await update.message.reply_text("❌ Network error while fetching IP information.")

        context.user_data.clear()
        return

    # ---- PIN CODE LOOKUP ----
    if mode == "pincode":
        pin = text.replace(" ", "")

        if not (pin.isdigit() and len(pin) == 6):
            await update.message.reply_text("❌ Invalid PIN Code.\nExample: 741101")
            context.user_data.clear()
            return

        try:
            url = f"https://api.postalpincode.in/pincode/{pin}"
            response = requests.get(url, timeout=10).json()

            if response[0]["Status"] != "Success":
                await update.message.reply_text("❌ PIN Code not found.")
                context.user_data.clear()
                return

            office = response[0]["PostOffice"][0]

            msg = f"""📮 PIN CODE INFORMATION

📌 PIN Code : {pin}
🏤 Post Office : {office.get("Name")}
🏙 District : {office.get("District")}
🌍 State : {office.get("State")}
📬 Division : {office.get("Division")}
🏢 Region : {office.get("Region")}
📮 Circle : {office.get("Circle")}
🏷 Branch Type : {office.get("BranchType")}
🚚 Delivery : {office.get("DeliveryStatus")}
🌐 Country : {office.get("Country")}
"""
            await update.message.reply_text(msg)

        except Exception:
            await update.message.reply_text("❌ Unable to fetch PIN code information.")

        context.user_data.clear()
        return

    # ---- PAKISTAN NUMBER INFO ----
    if mode == "pk_number":
        number = text.replace(" ", "")

        try:
            parsed = phonenumbers.parse(number, None)

            if parsed.country_code != 92:
                await update.message.reply_text("❌ Please send a Pakistan (+92) number.")
                context.user_data.clear()
                return

            if not phonenumbers.is_possible_number(parsed):
                await update.message.reply_text(
                    "❌ Invalid Pakistan mobile number.\n\nExample:\n+923001234567"
                )
                context.user_data.clear()
                return

            msg = f"""🇵🇰 PAKISTAN NUMBER INFORMATION

☎ Number : {number}
🌍 Country : Pakistan
📍 Region : {geocoder.description_for_number(parsed, 'en') or 'Unknown'}
📡 Carrier : {carrier.name_for_number(parsed, 'en') or 'Unknown'}

✅ Valid : {phonenumbers.is_valid_number(parsed)}
✅ Possible : {phonenumbers.is_possible_number(parsed)}

🌐 International :
{phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}

📌 E164 :
{phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)}
"""
            await update.message.reply_text(msg)

        except Exception:
            await update.message.reply_text(
                "❌ Invalid Pakistan mobile number.\n\nExample:\n+923001234567"
            )

        context.user_data.clear()
        return

    # ---- FREE FIRE UID ----
    if mode == "ff_uid":
        uid = text.replace(" ", "")

        if not re.fullmatch(UID_PATTERN, uid):
            await update.message.reply_text("❌ Invalid UID format.")
            context.user_data.clear()
            return

        msg = f"""🎮 FREE FIRE UID INFORMATION

🆔 UID : {uid}
📏 Length : {len(uid)}
🔢 Digits Only : Yes
✅ Format : Valid
🎯 Game : Free Fire
🔒 Lookup : Not Performed
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- FULL NUMBER INFO ----
    if mode == "full_number":
        number = text.replace(" ", "")

        try:
            parsed = phonenumbers.parse(number, None)

            region = geocoder.description_for_number(parsed, "en") or "Unknown"
            network = carrier.name_for_number(parsed, "en") or "Unknown"

            valid = phonenumbers.is_valid_number(parsed)
            possible = phonenumbers.is_possible_number(parsed)

            phone_type = PHONE_TYPES.get(phonenumbers.number_type(parsed), "Unknown")

            national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            international = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            rfc3966 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.RFC3966)

            tz = ", ".join(timezone.time_zones_for_number(parsed)) or "Unknown"
            geographical = "Yes" if phonenumbers.is_number_geographical(parsed) else "No"

            msg = f"""📱 NUMBER INFORMATION

☎ Input Number : {number}
🌍 Country Code : +{parsed.country_code}
📍 Region : {region}
📡 Carrier : {network}
📱 Number Type : {phone_type}

🔢 National Number : {parsed.national_number}
📏 Number Length : {len(str(parsed.national_number))}

✅ Valid Number : {valid}
✅ Possible Number : {possible}
🗺 Geographical : {geographical}

🌐 International : {international}
📌 National Format : {national}
📌 E164 Format : {e164}
🔗 RFC3966 Format : {rfc3966}

🕒 Time Zone : {tz}
📅 Scan Time : {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
🤖 Status : Success
"""
            await update.message.reply_text(msg)

        except Exception:
            await update.message.reply_text(
                "❌ Invalid phone number.\n\nExample:\n+919876543210"
            )

        context.user_data.clear()
        return

    # ---- EMAIL INFO ----
    if mode == "email":
        email = text.strip().lower()

        if not re.fullmatch(EMAIL_REGEX, email):
            await update.message.reply_text("❌ Invalid email address.")
            context.user_data.clear()
            return

        username, domain = email.split("@", 1)
        provider = EMAIL_PROVIDERS.get(domain, "Unknown / Custom Domain")

        parts = domain.split(".")
        tld = parts[-1]
        root_domain = ".".join(parts[-2:]) if len(parts) >= 2 else domain
        subdomain = ".".join(parts[:-2]) if len(parts) > 2 else "None"

        letters = sum(c.isalpha() for c in username)
        digits = sum(c.isdigit() for c in username)

        msg = f"""📧 EMAIL INFORMATION

📧 Email : {email}
👤 Username : {username}
🌐 Domain : {domain}
🏢 Provider : {provider}

🌍 Root Domain : {root_domain}
🌐 Subdomain : {subdomain}
🔖 TLD : .{tld}

📏 Email Length : {len(email)}
👤 Username Length : {len(username)}
🌐 Domain Length : {len(domain)}

🔠 Username Letters : {letters}
🔢 Username Digits : {digits}

✅ Format Valid : Yes
📅 Scan Time : {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
🤖 Status : Success
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- IMEI INFO ----
    if mode == "imei":
        imei = text.replace(" ", "")

        if not imei.isdigit() or len(imei) != 15:
            await update.message.reply_text(
                "❌ Invalid IMEI.\n\nExample:\n356938035643809"
            )
            context.user_data.clear()
            return

        valid = luhn_check(imei)

        tac = imei[:8]
        serial = imei[8:14]
        check_digit = imei[14]

        msg = f"""📱 IMEI INFORMATION

1️⃣ IMEI Number : {imei}
2️⃣ TAC Code : {tac}
3️⃣ Serial Number : {serial}
4️⃣ Check Digit : {check_digit}
5️⃣ IMEI Length : {len(imei)}
6️⃣ Digits Only : Yes
7️⃣ Luhn Check : {"Passed ✅" if valid else "Failed ❌"}
8️⃣ Identifier Type : IMEI (15 Digit)
9️⃣ First 4 Digits : {imei[:4]}
🔟 Last 4 Digits : {imei[-4:]}
1️⃣1️⃣ Scan Time : {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
1️⃣2️⃣ Validation : {"Valid ✅" if valid else "Invalid ❌"}
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- GITHUB INFO ----
    if mode == "github":
        username = text.replace(" ", "")

        try:
            url = f"https://api.github.com/users/{username}"
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                await update.message.reply_text("❌ GitHub user not found.")
                context.user_data.clear()
                return

            data = r.json()

            msg = f"""🐙 GITHUB INFORMATION

1️⃣ Username : {data.get("login")}
2️⃣ Name : {data.get("name") or "Not Available"}
3️⃣ User ID : {data.get("id")}
4️⃣ Profile URL : {data.get("html_url")}
5️⃣ Account Type : {data.get("type")}
6️⃣ Bio : {data.get("bio") or "Not Available"}
7️⃣ Company : {data.get("company") or "Not Available"}
8️⃣ Location : {data.get("location") or "Not Available"}
9️⃣ Public Repos : {data.get("public_repos")}
🔟 Public Gists : {data.get("public_gists")}
1️⃣1️⃣ Followers : {data.get("followers")}
1️⃣2️⃣ Following : {data.get("following")}
1️⃣3️⃣ Created At : {data.get("created_at")}
1️⃣4️⃣ Last Updated : {data.get("updated_at")}
1️⃣5️⃣ Profile Image : {data.get("avatar_url")}
"""
            await update.message.reply_text(msg)

        except requests.RequestException:
            await update.message.reply_text("❌ Network error.")

        context.user_data.clear()
        return

    # ---- WEBSITE INFO ----
    if mode == "website":
        url = text.replace(" ", "")

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            parsed = urlparse(url)

            title = soup.title.string.strip() if soup.title and soup.title.string else "N/A"

            description = "N/A"
            meta = soup.find("meta", attrs={"name": "description"})
            if meta:
                description = meta.get("content", "N/A")

            keywords = "N/A"
            meta = soup.find("meta", attrs={"name": "keywords"})
            if meta:
                keywords = meta.get("content", "N/A")

            msg = f"""🌐 WEBSITE INFORMATION

1️⃣ Website URL : {url}
2️⃣ Domain : {parsed.netloc}
3️⃣ Scheme : {parsed.scheme}
4️⃣ Title : {title}
5️⃣ Description : {description}
6️⃣ Keywords : {keywords}
7️⃣ HTTP Status : {response.status_code}
8️⃣ Server : {response.headers.get('Server', 'Unknown')}
9️⃣ Content Type : {response.headers.get('Content-Type', 'Unknown')}
🔟 Content Length : {response.headers.get('Content-Length', 'Unknown')}
1️⃣1️⃣ Encoding : {response.encoding}
1️⃣2️⃣ Final URL : {response.url}
1️⃣3️⃣ Secure HTTPS : {"Yes" if parsed.scheme == "https" else "No"}
1️⃣4️⃣ Redirected : {"Yes" if response.history else "No"}
1️⃣5️⃣ Status : Success
"""
            await update.message.reply_text(msg)

        except Exception:
            await update.message.reply_text("❌ Unable to fetch website information.")

        context.user_data.clear()
        return

    # ---- INSTAGRAM USERNAME ----
    if mode == "instagram":
        username = text.strip().lstrip("@")

        if not re.fullmatch(INSTAGRAM_USERNAME_PATTERN, username):
            await update.message.reply_text("❌ Invalid Instagram username.")
            context.user_data.clear()
            return

        profile_url = f"https://instagram.com/{username}"

        msg = f"""📸 INSTAGRAM INFORMATION

👤 Username : {username}
🔗 Profile URL : {profile_url}
📏 Username Length : {len(username)}
🔤 Letters : {sum(c.isalpha() for c in username)}
🔢 Digits : {sum(c.isdigit() for c in username)}
➖ Underscores : {username.count("_")}
🔸 Dots : {username.count(".")}
✅ Format Valid : Yes
🌐 Platform : Instagram
🤖 Status : Success
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- CHALLAN INFO ----
    if mode == "challan":
        vehicle = text.replace(" ", "").upper()

        if not re.match(VEHICLE_PATTERN, vehicle):
            await update.message.reply_text("❌ Invalid vehicle number.")
            context.user_data.clear()
            return

        msg = f"""🚨 CHALLAN INFORMATION

🚗 Vehicle Number : {vehicle}
✅ Format Valid : Yes

To check official challan status, visit:
https://echallan.parivahan.gov.in/

Choose:
• Check Challan Status
• Enter Vehicle Number
"""
        await update.message.reply_text(msg)
        context.user_data.clear()
        return

    # ---- No mode selected ----
    await update.message.reply_text(
        "Please select an option from the menu below 👇",
        reply_markup=menu,
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied")
        return

    delta = datetime.now() - BOT_START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes = remainder // 60
    uptime = f"{hours} Hours {minutes} Minutes"

    msg = f"""👑 ADMIN PANEL

🆔 Admin ID : {ADMIN_ID}
🤖 Bot Status : 🟢 Online
👥 Known Users (this session) : {len(KNOWN_USERS)}
📨 Messages Handled (this session) : {MESSAGE_COUNT}
⏱ Uptime : {uptime}

Available:
/admin
/ping
/device (admin only)

Note: user/message counts are in-memory for this run only
(reset on restart) — hook up a database if you need
persistent stats. /broadcast, /ban, /unban, /stats, /users,
/system, /maintenance are not implemented yet; let me know
if you want any of them built out.
"""
    await update.message.reply_text(msg)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is online.")


def build_device_info_text():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return f"""💻 DEVICE INFORMATION

🖥 System : {platform.system()}
📦 Release : {platform.release()}
🔖 Version : {platform.version()}
⚙ Machine : {platform.machine()}
🧠 Processor : {platform.processor() or "Unknown"}

🏷 Hostname : {socket.gethostname()}

🧮 CPU Cores : {psutil.cpu_count(logical=True)}
📊 CPU Usage : {psutil.cpu_percent(interval=1)}%

💾 Total RAM : {round(mem.total/1024/1024/1024,2)} GB
📈 Used RAM : {round(mem.used/1024/1024/1024,2)} GB
📉 Free RAM : {round(mem.available/1024/1024/1024,2)} GB

💽 Disk Total : {round(disk.total/1024/1024/1024,2)} GB
📂 Disk Used : {round(disk.used/1024/1024/1024,2)} GB
📁 Disk Free : {round(disk.free/1024/1024/1024,2)} GB

⏱ Uptime : {int(time.time()-START_TIME)} sec
"""


async def device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied")
        return

    await update.message.reply_text(build_device_info_text())


def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN" or "AAFbM4H6" in BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN sahi se set nahi hai. Environment variable use karo.")
        return
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("device", device))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()