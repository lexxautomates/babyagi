#!/usr/bin/env python3
"""
BabyAGI Telegram Bot
A Telegram interface for interacting with BabyAGI
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

# Import BabyAGI
import babyagi
from babyagi.functionz.core.framework import func

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

*Commands:*
• /start - Initialize the bot
• /help - Show this help message
• /functions - List all available BabyAGI functions
• /clear - Clear your conversation history
• /task <objective> - Execute a task through BabyAGI
• /chat <message> - Have a conversation with BabyAGI

*How to use:*
1. Send any message to interact with BabyAGI
2. Use /task followed by your objective for task execution
3. Use /chat for conversational interactions

*Tips:*
• Be specific with your requests
• Break down complex tasks into smaller ones
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

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /clear command"""
    chat_id = update.effective_chat.id
    
    if chat_id in chat_histories:
        del chat_histories[chat_id]
    
    await update.message.reply_text("🗑️ Chat history cleared!")

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
    """Get a response from BabyAGI"""
    try:
        # Try to use chat_with_functions if available
        functions = get_available_functions()
        
        if 'chat_with_functions' in functions:
            # Use the chat_with_functions capability
            history = chat_histories.get(chat_id, [])
            result = func.executor.execute('chat_with_functions', history, functions)
            return result if result else "I processed your request but got no response."
        else:
            # Fallback to simple AI response
            return await simple_ai_response(message, chat_id)
            
    except Exception as e:
        logger.error(f"BabyAGI response error: {e}")
        return f"I encountered an error: {str(e)}. Please make sure OpenAI API key is configured."

async def simple_ai_response(message: str, chat_id: int) -> str:
    """Simple AI response using local Ollama server via LiteLLM"""
    try:
        import litellm
        
        # Get Ollama configuration from environment
        ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://31.220.20.251:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        history = chat_histories.get(chat_id, [])
        messages = [{"role": "system", "content": "You are BabyAGI, a helpful AI assistant connected to Telegram. Be concise and helpful."}]
        
        for h in history[-10:]:  # Keep last 10 messages for context
            messages.append({"role": h["role"], "content": h["message"]})
        
        # Use Ollama via LiteLLM
        response = litellm.completion(
            model=f"ollama/{ollama_model}",
            messages=messages,
            api_base=ollama_base_url,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot is running! Send a message to your Telegram bot.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()