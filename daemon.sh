#!/bin/bash
# BabyAGI Telegram Bot Daemon Service Manager
# Usage: ./daemon.sh [install|uninstall|start|stop|status|logs]

PLIST_NAME="com.babyagi.telegram"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
SOURCE_PLIST="/Users/alexandriajohn/Desktop/babyagi/$PLIST_NAME.plist"
BOT_DIR="/Users/alexandriajohn/Desktop/babyagi"
LOG_FILE="$BOT_DIR/bot.log"
ERROR_LOG="$BOT_DIR/bot_error.log"

case "$1" in
    install)
        echo "Installing BabyAGI Telegram Bot daemon..."
        cp "$SOURCE_PLIST" "$PLIST_PATH"
        launchctl load "$PLIST_PATH"
        echo "✓ Daemon installed and started!"
        echo "Logs: $LOG_FILE"
        ;;
    
    uninstall)
        echo "Uninstalling BabyAGI Telegram Bot daemon..."
        launchctl unload "$PLIST_PATH" 2>/dev/null
        rm -f "$PLIST_PATH"
        echo "✓ Daemon uninstalled!"
        ;;
    
    start)
        echo "Starting BabyAGI Telegram Bot daemon..."
        launchctl load "$PLIST_PATH" 2>/dev/null || launchctl start "$PLIST_NAME"
        echo "✓ Daemon started!"
        ;;
    
    stop)
        echo "Stopping BabyAGI Telegram Bot daemon..."
        launchctl unload "$PLIST_PATH" 2>/dev/null
        echo "✓ Daemon stopped!"
        ;;
    
    restart)
        echo "Restarting BabyAGI Telegram Bot daemon..."
        launchctl unload "$PLIST_PATH" 2>/dev/null
        sleep 2
        launchctl load "$PLIST_PATH"
        echo "✓ Daemon restarted!"
        ;;
    
    status)
        echo "Checking daemon status..."
        if launchctl list | grep -q "$PLIST_NAME"; then
            echo "✓ Daemon is running"
            PID=$(launchctl list | grep "$PLIST_NAME" | awk '{print $2}')
            echo "  PID: $PID"
        else
            echo "✗ Daemon is not running"
        fi
        ;;
    
    logs)
        echo "=== Recent Logs ==="
        if [ -f "$LOG_FILE" ]; then
            tail -50 "$LOG_FILE"
        else
            echo "No log file found at $LOG_FILE"
        fi
        ;;
    
    errors)
        echo "=== Error Logs ==="
        if [ -f "$ERROR_LOG" ]; then
            tail -50 "$ERROR_LOG"
        else
            echo "No error log found at $ERROR_LOG"
        fi
        ;;
    
    *)
        echo "BabyAGI Telegram Bot Daemon Manager"
        echo ""
        echo "Usage: $0 {install|uninstall|start|stop|restart|status|logs|errors}"
        echo ""
        echo "Commands:"
        echo "  install   - Install and start the daemon service"
        echo "  uninstall - Stop and remove the daemon service"
        echo "  start     - Start the daemon"
        echo "  stop      - Stop the daemon"
        echo "  restart   - Restart the daemon"
        echo "  status    - Check if daemon is running"
        echo "  logs      - Show recent logs"
        echo "  errors    - Show error logs"
        ;;
esac