#!/usr/bin/env python3
"""
BabyAGI Telegram Bot
A Telegram interface for interacting with BabyAGI
Enhanced with Agent Lightning tracing
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Authorized chat ID for security
AUTHORIZED_CHAT_ID = int(TELEGRAM_CHAT_ID) if TELEGRAM_CHAT_ID else None

# Agent Lightning configuration
AGL_ENABLED = os.getenv('AGL_ENABLED', 'true').lower() == 'true'
AGL_STORE_URL = os.getenv('AGL_STORE_URL', 'http://localhost:45993')

# Import BabyAGI
import babyagi
from babyagi.functionz.core.framework import func

# Initialize Agent Lightning if enabled
if AGL_ENABLED:
    try:
        import agentlightning as agl
        logger.info(f"Agent Lightning enabled, store: {AGL_STORE_URL}")
    except ImportError:
        logger.warning("Agent Lightning not installed, tracing disabled")
        AGL_ENABLED = False

# Store chat history per user
chat_histories = {}

def get_available_functions():
    """Get list of available functions from BabyAGI"""
    try:
        functions = func.get_all_functions()
        return [f['name'] for f in functions] if functions else []
    except Exception as e:
        logger.error(f"Error getting functions: {e}")
        return []

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    chat_id = update.effective_chat.id
    
    # Security check
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access. This bot is private.")
        return
    
    welcome_message = """
🤖 *Welcome to BabyAGI Telegram Bot!*

I'm an AI-powered task management system connected to BabyAGI.

*Available Commands:*
/start - Show this welcome message
/help - Show available commands
/functions - List available functions
/clear - Clear chat history
/task <objective> - Create and execute a task
/chat <message> - Chat with BabyAGI

*Example:*
`/task Write a summary of AI trends in 2024`

Just send me a message and I'll help you accomplish your goals!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    help_text = """
📚 *BabyAGI Bot Help*

*General Commands:*
• /start - Initialize the bot
• /help - Show this help message
• /functions - List all available BabyAGI functions
• /clear - Clear your conversation history
• /task <objective> - Execute a task through BabyAGI
• /chat <message> - Have a conversation with BabyAGI

*🤖 Agent Builder Commands:*
• /build <description> - Create a new AI agent
• /agents - List all created agents
• /agent <id> - Get agent details
• /testagent <id> <query> - Test an agent

*💰 Crypto Commands:*
• /crypto - Market summary with top 5 coins
• /price <coin> - Get price (e.g., `/price bitcoin`)
• /top [number] - Top cryptos by market cap
• /trending - Trending coins on CoinGecko
• /gas - Current Ethereum gas prices
• /convert <amount> <from> [to] - Convert crypto
• /search <query> - Search for cryptocurrencies

*⚡ Agent Lightning:*
• /agl - Show Agent Lightning status
• /trace - Toggle tracing mode
• /reward <score> - Send reward signal

*Examples:*
• `/build A crypto price alert agent`
• `/price ethereum`
• `/agents`

*Tips:*
• Be specific with your requests
• Use /clear to start fresh conversations
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def functions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /functions command"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    functions = get_available_functions()
    
    if functions:
        func_list = "\n".join([f"• `{f}`" for f in functions[:20]])  # Limit to 20
        message = f"🔧 *Available Functions ({len(functions)} total):*\n\n{func_list}"
        if len(functions) > 20:
            message += f"\n\n_...and {len(functions) - 20} more_"
    else:
        message = "No functions available. Make sure BabyAGI is properly initialized."
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def crypto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /crypto command - show crypto market summary"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('get_crypto_market_summary')
        await update.message.reply_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Crypto command error: {e}")
        await update.message.reply_text(f"❌ Error fetching crypto data: {str(e)}")


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /price command - get specific crypto price"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please specify a coin.\n"
            "Example: `/price bitcoin` or `/price ethereum`\n\n"
            "Popular coins: `bitcoin`, `ethereum`, `solana`, `dogecoin`, `cardano`",
            parse_mode='Markdown'
        )
        return
    
    coin_id = context.args[0].lower()
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('get_crypto_price', coin_id)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            change = result.get('24h_change_percent', 0) or 0
            change_emoji = "🟢" if change >= 0 else "🔴"
            message = f"""💰 *{result['coin'].title()}*
            
💵 Price: ${result['price_usd']:,.2f}
📊 Market Cap: ${result['market_cap_usd']:,.0f}
{change_emoji} 24h Change: {change:.2f}%"""
            await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Price command error: {e}")
        await update.message.reply_text(f"❌ Error fetching price: {str(e)}")


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /top command - show top cryptos"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    limit = 10
    if context.args and context.args[0].isdigit():
        limit = min(int(context.args[0]), 20)
    
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('get_top_cryptos', limit)
        
        if isinstance(result, list) and len(result) > 0 and "error" not in result[0]:
            message = f"🏆 *Top {len(result)} Cryptocurrencies*\n\n"
            for coin in result:
                change = coin.get('24h_change_percent', 0) or 0
                change_emoji = "🟢" if change >= 0 else "🔴"
                price = coin.get('price_usd', 0) or 0
                message += f"#{coin['rank']} {coin['name']} ({coin['symbol']}): ${price:,.2f} {change_emoji}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            error_msg = result[0].get('error', 'Unknown error') if result else 'No data'
            await update.message.reply_text(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Top command error: {e}")
        await update.message.reply_text(f"❌ Error fetching top cryptos: {str(e)}")


async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /trending command - show trending cryptos"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('get_trending_cryptos')
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            trending = result.get('trending', [])
            message = "🔥 *Trending on CoinGecko*\n\n"
            for i, coin in enumerate(trending, 1):
                rank = coin.get('market_cap_rank', 'N/A')
                message += f"{i}. {coin['name']} ({coin['symbol']}) - Rank #{rank}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Trending command error: {e}")
        await update.message.reply_text(f"❌ Error fetching trending: {str(e)}")


async def gas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /gas command - show ETH gas prices"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('get_eth_gas_price')
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            message = f"""⛽ *Ethereum Gas Prices*

🐢 Safe: {result.get('safe_gas_price_gwei', 'N/A')} Gwei
🚗 Standard: {result.get('propose_gas_price_gwei', 'N/A')} Gwei
🚀 Fast: {result.get('fast_gas_price_gwei', 'N/A')} Gwei
📊 Base Fee: {result.get('base_fee_gwei', 'N/A')} Gwei"""
            await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Gas command error: {e}")
        await update.message.reply_text(f"❌ Error fetching gas prices: {str(e)}")


async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /convert command - convert crypto amounts"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Please specify amount and coin.\n"
            "Example: `/convert 1 bitcoin` or `/convert 5 ethereum usd`\n"
            "Or: `/convert 1 bitcoin ethereum`",
            parse_mode='Markdown'
        )
        return
    
    try:
        amount = float(context.args[0])
        from_coin = context.args[1].lower()
        to_coin = context.args[2].lower() if len(context.args) > 2 else "usd"
        
        await update.message.chat.send_action('typing')
        
        result = func.executor.execute('convert_crypto', amount, from_coin, to_coin)
        
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
        else:
            if to_coin == "USD":
                message = f"💱 *Conversion*\n\n{amount} {from_coin.title()} = ${result['converted']:,.2f} USD\nRate: ${result['rate']:,.2f}"
            else:
                message = f"💱 *Conversion*\n\n{amount} {from_coin.title()} = {result['converted']:,.8f} {to_coin.title()}\nRate: {result['rate']:,.8f}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please use a number.\nExample: `/convert 1.5 bitcoin`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Convert command error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /search command - search for cryptos"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text("Please specify a search query.\nExample: `/search doge`", parse_mode='Markdown')
        return
    
    query = ' '.join(context.args)
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('search_crypto', query)
        
        if result and "error" not in result[0]:
            message = f"🔍 *Search Results for '{query}'*\n\n"
            for coin in result:
                rank = f"#{coin.get('market_cap_rank', 'N/A')}" if coin.get('market_cap_rank') else "Unranked"
                message += f"• {coin['name']} ({coin['symbol']}) - {rank}\n  ID: `{coin['id']}`\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            error_msg = result[0].get('error', 'No results found') if result else 'No results found'
            await update.message.reply_text(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Search command error: {e}")
        await update.message.reply_text(f"❌ Error searching: {str(e)}")


# ============================================================
# NCA TOOLKIT COMMANDS
# ============================================================

async def nca_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /nca command - show NCA Toolkit help"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    help_text = """
🎬 *NCA Toolkit Commands*

*Media Download:*
• `/download <url>` - Download from YouTube, TikTok, Instagram, etc.
• `/transcribe <url>` - Transcribe audio/video to text (Whisper)
• `/metadata <url>` - Get media file metadata

*Video Processing:*
• `/thumbnail <url> [timestamp]` - Extract thumbnail from video
• `/cut <url> <start> <end>` - Cut video between times
• `/trim <url> <start> <duration>` - Trim video

*Image Tools:*
• `/screenshot <url>` - Take screenshot of webpage

*Utilities:*
• `/convert <url> <format>` - Convert media (mp3, mp4, wav)
• `/python <code>` - Execute Python code

*Examples:*
• `/download https://youtube.com/watch?v=xxx`
• `/transcribe https://example.com/audio.mp3`
• `/screenshot https://example.com`
• `/convert https://example.com/video.mp4 mp3`
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /download command - download media from various platforms"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a URL to download.\n"
            "Example: `/download https://youtube.com/watch?v=xxx`\n\n"
            "Supports: YouTube, TikTok, Instagram, Twitter, and 1000+ sites!",
            parse_mode='Markdown'
        )
        return
    
    media_url = context.args[0]
    audio_only = '--audio' in ' '.join(context.args)
    
    await update.message.chat.send_action('typing')
    await update.message.reply_text("⏳ Downloading media... This may take a moment.")
    
    try:
        result = func.executor.execute('nca_download_media', media_url, audio_only, 'mp3')
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif 'output_url' in result or 'file_url' in result:
            file_url = result.get('output_url') or result.get('file_url')
            title = result.get('title', 'Media')
            await update.message.reply_text(
                f"✅ *Download Complete!*\n\n"
                f"Title: {title}\n"
                f"URL: {file_url}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"📥 Result: `{result}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Download command error: {e}")
        await update.message.reply_text(f"❌ Error downloading: {str(e)}")


async def transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /transcribe command - transcribe audio/video to text"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a media URL to transcribe.\n"
            "Example: `/transcribe https://example.com/audio.mp3`",
            parse_mode='Markdown'
        )
        return
    
    media_url = context.args[0]
    language = context.args[1] if len(context.args) > 1 else 'en'
    
    await update.message.chat.send_action('typing')
    await update.message.reply_text("⏳ Transcribing... This may take a moment for long files.")
    
    try:
        result = func.executor.execute('nca_transcribe_media', media_url, language)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif 'text' in result or 'transcript' in result:
            transcript = result.get('text') or result.get('transcript', '')
            # Truncate if too long
            if len(transcript) > 4000:
                transcript = transcript[:4000] + "...\n\n_(truncated)_"
            await update.message.reply_text(f"📝 *Transcript:*\n\n{transcript}", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"📝 Result: `{result}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Transcribe command error: {e}")
        await update.message.reply_text(f"❌ Error transcribing: {str(e)}")


async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /screenshot command - take webpage screenshot"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a URL to screenshot.\n"
            "Example: `/screenshot https://example.com`",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    full_page = '--full' not in ' '.join(context.args)
    
    await update.message.chat.send_action('typing')
    await update.message.reply_text("⏳ Taking screenshot...")
    
    try:
        result = func.executor.execute('nca_webpage_screenshot', url, full_page)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif 'screenshot_url' in result or 'image_url' in result or 'url' in result:
            image_url = result.get('screenshot_url') or result.get('image_url') or result.get('url')
            await update.message.reply_text(f"📸 Screenshot: {image_url}")
        else:
            await update.message.reply_text(f"📸 Result: `{result}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Screenshot command error: {e}")
        await update.message.reply_text(f"❌ Error taking screenshot: {str(e)}")


async def thumbnail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /thumbnail command - extract video thumbnail"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a video URL.\n"
            "Example: `/thumbnail https://example.com/video.mp4 00:00:05`",
            parse_mode='Markdown'
        )
        return
    
    video_url = context.args[0]
    timestamp = context.args[1] if len(context.args) > 1 else '00:00:00'
    
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('nca_extract_video_thumbnail', video_url, timestamp)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif 'thumbnail_url' in result or 'image_url' in result or 'url' in result:
            image_url = result.get('thumbnail_url') or result.get('image_url') or result.get('url')
            await update.message.reply_text(f"🖼️ Thumbnail: {image_url}")
        else:
            await update.message.reply_text(f"🖼️ Result: `{result}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Thumbnail command error: {e}")
        await update.message.reply_text(f"❌ Error extracting thumbnail: {str(e)}")


async def cut_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /cut command - cut video"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "Please provide video URL, start time, and end time.\n"
            "Example: `/cut https://example.com/video.mp4 00:00:10 00:00:30`",
            parse_mode='Markdown'
        )
        return
    
    video_url = context.args[0]
    start_time = context.args[1]
    end_time = context.args[2]
    
    await update.message.chat.send_action('typing')
    await update.message.reply_text("⏳ Cutting video...")
    
    try:
        result = func.executor.execute('nca_cut_video', video_url, start_time, end_time)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif 'output_url' in result or 'video_url' in result or 'url' in result:
            output_url = result.get('output_url') or result.get('video_url') or result.get('url')
            await update.message.reply_text(f"✅ Video cut complete: {output_url}")
        else:
            await update.message.reply_text(f"🎬 Result: `{result}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Cut video command error: {e}")
        await update.message.reply_text(f"❌ Error cutting video: {str(e)}")


async def convert_media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /convert command - convert media format"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide media URL and output format.\n"
            "Example: `/convert https://example.com/video.mp4 mp3`\n\n"
            "Supported formats: mp3, mp4, wav, webm",
            parse_mode='Markdown'
        )
        return
    
    media_url = context.args[0]
    output_format = context.args[1].lower()
    
    await update.message.chat.send_action('typing')
    await update.message.reply_text("⏳ Converting media...")
    
    try:
        result = func.executor.execute('nca_convert_media', media_url, output_format)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif 'output_url' in result or 'file_url' in result or 'url' in result:
            output_url = result.get('output_url') or result.get('file_url') or result.get('url')
            await update.message.reply_text(f"✅ Conversion complete: {output_url}")
        else:
            await update.message.reply_text(f"🔄 Result: `{result}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Convert command error: {e}")
        await update.message.reply_text(f"❌ Error converting: {str(e)}")


async def metadata_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /metadata command - get media metadata"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a media URL.\n"
            "Example: `/metadata https://example.com/video.mp4`",
            parse_mode='Markdown'
        )
        return
    
    media_url = context.args[0]
    
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('nca_get_media_metadata', media_url)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            # Format metadata nicely
            message = "📊 *Media Metadata*\n\n"
            for key, value in result.items():
                if key not in ['error', 'raw_response']:
                    message += f"• {key}: `{value}`\n"
            await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Metadata command error: {e}")
        await update.message.reply_text(f"❌ Error getting metadata: {str(e)}")


async def python_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /python command - execute Python code"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide Python code to execute.\n"
            "Example: `/python print(2 + 2)`\n\n"
            "Note: Code runs in a sandboxed environment.",
            parse_mode='Markdown'
        )
        return
    
    code = ' '.join(context.args)
    
    await update.message.chat.send_action('typing')
    
    try:
        result = func.executor.execute('nca_execute_python', code, 30)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown error')}")
        elif 'output' in result or 'result' in result:
            output = result.get('output') or result.get('result', '')
            await update.message.reply_text(f"🐍 *Output:*\n\n```\n{output}\n```", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"🐍 Result: `{result}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Python command error: {e}")
        await update.message.reply_text(f"❌ Error executing code: {str(e)}")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /clear command"""
    chat_id = update.effective_chat.id
    
    if chat_id in chat_histories:
        del chat_histories[chat_id]
    
    await update.message.reply_text("🗑️ Chat history cleared!")

# ============================================================
# AGENT LIGHTNING COMMANDS
# ============================================================

async def agl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /agl command - show Agent Lightning status"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    status = "✅ Enabled" if AGL_ENABLED else "❌ Disabled"
    message = f"""⚡ *Agent Lightning Status*

Status: {status}
Store URL: `{AGL_STORE_URL}`

*Commands:*
• `/agl` - Show this status
• `/trace` - Toggle tracing mode
• `/reward <score>` - Send reward signal

Agent Lightning traces AI interactions
and collects data for training.
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def trace_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /trace command - toggle tracing"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    global AGL_ENABLED
    AGL_ENABLED = not AGL_ENABLED
    status = "enabled" if AGL_ENABLED else "disabled"
    await update.message.reply_text(f"⚡ Agent Lightning tracing {status}")

async def reward_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /reward command - send reward signal"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not AGL_ENABLED:
        await update.message.reply_text("⚠️ Agent Lightning is disabled. Use /trace to enable.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a reward score (0-1).\nExample: `/reward 0.8`", parse_mode='Markdown')
        return
    
    try:
        score = float(context.args[0])
        if not 0 <= score <= 1:
            raise ValueError("Score must be between 0 and 1")
        
        # Send reward to Agent Lightning store
        import requests
        response = requests.post(
            f"{AGL_STORE_URL}/reward",
            json={"score": score, "source": "telegram"}
        )
        
        if response.status_code == 200:
            await update.message.reply_text(f"🏆 Reward sent: {score}")
        else:
            await update.message.reply_text(f"❌ Failed to send reward: {response.text}")
    except ValueError as e:
        await update.message.reply_text(f"❌ Invalid score: {e}")
    except Exception as e:
        logger.error(f"Reward command error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ============================================================
# AGENT BUILDER COMMANDS
# ============================================================

async def build_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /build command - create a new AI agent"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🤖 *Agent Builder*\n\n"
            "Please describe the agent you want to create.\n\n"
            "Example: `/build A crypto price alert agent that monitors Bitcoin and Ethereum`\n\n"
            "The agent will be created with appropriate tools and tested automatically.",
            parse_mode='Markdown'
        )
        return
    
    description = ' '.join(context.args)
    
    await update.message.reply_text(
        f"🔨 *Building Agent...*\n\n"
        f"Description: {description}\n\n"
        f"⏳ Generating test queries and initializing...",
        parse_mode='Markdown'
    )
    
    try:
        # Import and call create_agent
        from babyagi.functionz.packs.default.agent_builder import create_agent
        
        result = create_agent(description)
        
        if result.get("status") == "active":
            success_rate = result.get("successful_queries", 0) / max(result.get("queries_processed", 1), 1) * 100
            
            message = f"""✅ *Agent Created Successfully!*

🆔 Agent ID: `{result['agent_id']}`
📝 Description: {description[:100]}
🔧 Tools: {', '.join(result.get('tools', []))}

📊 *Test Results:*
• Queries Generated: {result.get('queries_processed', 0)}
• Successful: {result.get('successful_queries', 0)}
• Failed: {result.get('failed_queries', 0)}
• Success Rate: {success_rate:.1f}%

⚡ Agent Lightning: {'✅ Registered' if result.get('agl_registered') else '❌ Not registered'}

Use `/agents` to list all agents.
Use `/testagent {result['agent_id']} <query>` to test."""
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                f"❌ *Agent Creation Failed*\n\n"
                f"Error: {result.get('error', 'Unknown error')}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Build command error: {e}")
        await update.message.reply_text(f"❌ Error building agent: {str(e)}")


async def agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /agents command - list all created agents"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    try:
        from babyagi.functionz.packs.default.agent_builder import list_agents
        
        agents = list_agents()
        
        if not agents:
            await update.message.reply_text(
                "📋 *No Agents Created Yet*\n\n"
                "Use `/build <description>` to create a new agent.",
                parse_mode='Markdown'
            )
            return
        
        message = f"📋 *Created Agents ({len(agents)})*\n\n"
        for agent in agents:
            status_emoji = "✅" if agent.get('status') == 'active' else "❌"
            message += f"""{status_emoji} *{agent['agent_id']}*
   {agent.get('description', 'No description')[:50]}...
   Queries: {agent.get('queries_processed', 0)} | Success: {agent.get('success_rate', 0):.1f}%
   
"""
        
        message += "Use `/agent <id>` for details.\nUse `/testagent <id> <query>` to test."
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Agents command error: {e}")
        await update.message.reply_text(f"❌ Error listing agents: {str(e)}")


async def agent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /agent command - get agent details"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide an agent ID.\n"
            "Example: `/agent abc123`\n\n"
            "Use `/agents` to list all agents.",
            parse_mode='Markdown'
        )
        return
    
    agent_id = context.args[0]
    
    try:
        from babyagi.functionz.packs.default.agent_builder import get_agent
        
        agent = get_agent(agent_id)
        
        if not agent:
            await update.message.reply_text(f"❌ Agent `{agent_id}` not found.", parse_mode='Markdown')
            return
        
        status_emoji = "✅" if agent.get('status') == 'active' else "❌"
        success_rate = agent.get('successful_queries', 0) / max(agent.get('queries_processed', 1), 1) * 100
        
        message = f"""🤖 *Agent Details*

🆔 ID: `{agent.get('agent_id')}`
📝 Description: {agent.get('description', 'N/A')}
📊 Status: {status_emoji} {agent.get('status', 'unknown')}
📅 Created: {agent.get('created_at', 'N/A')}

🔧 *Configuration:*
• Model: {agent.get('config', {}).get('model', 'N/A')}
• Tools: {', '.join(agent.get('tools', []))}

📈 *Statistics:*
• Queries Processed: {agent.get('queries_processed', 0)}
• Successful: {agent.get('successful_queries', 0)}
• Failed: {agent.get('failed_queries', 0)}
• Success Rate: {success_rate:.1f}%
• Total Reward: {agent.get('total_reward', 0):.2f}

⚡ Agent Lightning: {'✅ Registered' if agent.get('agl_registered') else '❌ Not registered'}

Use `/testagent {agent_id} <query>` to test."""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Agent command error: {e}")
        await update.message.reply_text(f"❌ Error getting agent: {str(e)}")


async def testagent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /testagent command - test an agent with a query"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide agent ID and test query.\n"
            "Example: `/testagent abc123 What is the price of Bitcoin?`",
            parse_mode='Markdown'
        )
        return
    
    agent_id = context.args[0]
    query = ' '.join(context.args[1:])
    
    await update.message.chat.send_action('typing')
    await update.message.reply_text(
        f"🧪 *Testing Agent*\n\n"
        f"Agent: `{agent_id}`\n"
        f"Query: {query}\n\n"
        f"⏳ Processing...",
        parse_mode='Markdown'
    )
    
    try:
        from babyagi.functionz.packs.default.agent_builder import test_agent
        
        result = test_agent(agent_id, query)
        
        if result.get('status') == 'success':
            message = f"""✅ *Test Successful*

🆔 Agent: `{agent_id}`
❓ Query: {query}

📤 *Response:*
{result.get('result', 'No output')[:3000]}

⏱️ Time: {result.get('elapsed_time', 0):.2f}s"""
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                f"❌ *Test Failed*\n\n"
                f"Error: {result.get('error', 'Unknown error')}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Test agent command error: {e}")
        await update.message.reply_text(f"❌ Error testing agent: {str(e)}")


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /task command"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a task objective.\nExample: `/task Analyze market trends`", parse_mode='Markdown')
        return
    
    objective = ' '.join(context.args)
    await update.message.reply_text(f"🎯 Processing task: *{objective}*", parse_mode='Markdown')
    
    try:
        # Execute task through BabyAGI
        result = await execute_babyagi_task(objective, chat_id)
        await send_long_message(update, result)
    except Exception as e:
        logger.error(f"Task execution error: {e}")
        await update.message.reply_text(f"❌ Error executing task: {str(e)}")

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /chat command"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a message.\nExample: `/chat Hello, how can you help?`", parse_mode='Markdown')
        return
    
    message = ' '.join(context.args)
    await process_message(update, message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    chat_id = update.effective_chat.id
    
    if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("⚠️ Unauthorized access. This bot is private.")
        return
    
    message = update.message.text
    await process_message(update, message)

async def process_message(update: Update, message: str):
    """Process a message through BabyAGI"""
    chat_id = update.effective_chat.id
    
    # Initialize chat history if needed
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    # Add user message to history
    chat_histories[chat_id].append({"role": "user", "message": message})
    
    try:
        # Show typing indicator
        await update.message.chat.send_action('typing')
        
        # Get response from BabyAGI
        response = await get_babyagi_response(message, chat_id)
        
        # Add assistant response to history
        chat_histories[chat_id].append({"role": "assistant", "message": response})
        
        # Send response
        await send_long_message(update, response)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def get_babyagi_response(message: str, chat_id: int) -> str:
    """Get a response from BabyAGI using Ollama"""
    try:
        # Use simple AI response with Ollama directly
        return await simple_ai_response(message, chat_id)
            
    except Exception as e:
        logger.error(f"BabyAGI response error: {e}")
        return f"I encountered an error: {str(e)}. Please check if Ollama is running on the VPS."

async def simple_ai_response(message: str, chat_id: int) -> str:
    """Simple AI response using local Ollama server via LiteLLM with Agent Lightning tracing"""
    try:
        import litellm
        
        # Get Ollama configuration from environment
        ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://31.220.20.251:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        history = chat_histories.get(chat_id, [])
        messages = [{"role": "system", "content": "You are BabyAGI, a helpful AI assistant connected to Telegram. Be concise and helpful."}]
        
        for h in history[-10:]:  # Keep last 10 messages for context
            messages.append({"role": h["role"], "content": h["message"]})
        
        # Agent Lightning tracing
        trace_id = None
        if AGL_ENABLED:
            try:
                import requests
                # Start trace
                trace_resp = requests.post(
                    f"{AGL_STORE_URL}/trace/start",
                    json={
                        "input": message,
                        "metadata": {"chat_id": chat_id, "model": ollama_model}
                    }
                )
                if trace_resp.status_code == 200:
                    trace_id = trace_resp.json().get("trace_id")
                    logger.info(f"AGL trace started: {trace_id}")
            except Exception as e:
                logger.warning(f"AGL trace start failed: {e}")
        
        # Use Ollama via LiteLLM
        response = litellm.completion(
            model=f"ollama/{ollama_model}",
            messages=messages,
            api_base=ollama_base_url,
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        
        # End Agent Lightning trace
        if AGL_ENABLED and trace_id:
            try:
                import requests
                requests.post(
                    f"{AGL_STORE_URL}/trace/end",
                    json={"trace_id": trace_id, "output": result}
                )
                logger.info(f"AGL trace ended: {trace_id}")
            except Exception as e:
                logger.warning(f"AGL trace end failed: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Simple AI response error: {e}")
        return f"I received your message: '{message}'. Error connecting to Ollama server: {str(e)}"

async def execute_babyagi_task(objective: str, chat_id: int) -> str:
    """Execute a task through BabyAGI"""
    try:
        # Try to execute through BabyAGI's function system
        functions = get_available_functions()
        
        # Look for task execution function
        if 'execute_task' in functions:
            result = func.executor.execute('execute_task', objective)
            return result if result else "Task completed with no output."
        else:
            # Use chat interface as fallback
            return await get_babyagi_response(f"Please help me with this task: {objective}", chat_id)
            
    except Exception as e:
        logger.error(f"Task execution error: {e}")
        return f"Error executing task: {str(e)}"

async def send_long_message(update: Update, text: str):
    """Send a message, splitting if it's too long"""
    max_length = 4096  # Telegram's message limit
    
    if len(text) <= max_length:
        await update.message.reply_text(text)
        return
    
    # Split into chunks
    chunks = []
    while len(text) > max_length:
        # Find a good break point
        break_point = text[:max_length].rfind('\n')
        if break_point == -1:
            break_point = max_length
        
        chunks.append(text[:break_point])
        text = text[break_point:].strip()
    
    chunks.append(text)
    
    for chunk in chunks:
        await update.message.reply_text(chunk)
        await asyncio.sleep(0.5)  # Avoid rate limiting

def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    logger.info("Starting BabyAGI Telegram Bot...")
    logger.info(f"Authorized Chat ID: {AUTHORIZED_CHAT_ID}")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("functions", functions_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("task", task_command))
    application.add_handler(CommandHandler("chat", chat_command))
    
    # Crypto commands
    application.add_handler(CommandHandler("crypto", crypto_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("trending", trending_command))
    application.add_handler(CommandHandler("gas", gas_command))
    application.add_handler(CommandHandler("convert", convert_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # NCA Toolkit commands
    application.add_handler(CommandHandler("nca", nca_command))
    application.add_handler(CommandHandler("download", download_command))
    application.add_handler(CommandHandler("transcribe", transcribe_command))
    application.add_handler(CommandHandler("screenshot", screenshot_command))
    application.add_handler(CommandHandler("thumbnail", thumbnail_command))
    application.add_handler(CommandHandler("cut", cut_video_command))
    application.add_handler(CommandHandler("metadata", metadata_command))
    application.add_handler(CommandHandler("python", python_command))
    
    # Agent Lightning commands
    application.add_handler(CommandHandler("agl", agl_command))
    application.add_handler(CommandHandler("trace", trace_command))
    application.add_handler(CommandHandler("reward", reward_command))
    
    # Agent Builder commands
    application.add_handler(CommandHandler("build", build_command))
    application.add_handler(CommandHandler("agents", agents_command))
    application.add_handler(CommandHandler("agent", agent_command))
    application.add_handler(CommandHandler("testagent", testagent_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot is running! Send a message to your Telegram bot.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()