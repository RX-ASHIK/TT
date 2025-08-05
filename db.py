# -*- coding: utf-8 -*-
"""
💰 EARNING MASTER BOT - Professional Notification System
🔔 Version: 4.0 | Codename: "Active Earner"
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# Configuration
BOT_TOKEN = "7641873839:AAHt4JsRYUMQDHrrEHdOB-No3ZrtJQeDxXc"
TIMEZONE = pytz.timezone("Asia/Dhaka")
NOTIFICATION_INTERVAL_MINUTES = 60  # 1 hour interval

class NotificationSystem:
    def __init__(self):
        self.db = sqlite3.connect('earning_master.db')
        self.scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        self.setup_scheduler()
        
    def setup_scheduler(self):
        """শিডিউলার সেটআপ করুন"""
        self.scheduler.add_job(
            self.send_hourly_notifications,
            'interval',
            minutes=NOTIFICATION_INTERVAL_MINUTES,
            next_run_time=datetime.now(TIMEZONE) + timedelta(minutes=1)
        )
    
    async def send_hourly_notifications(self):
        """সকল ইউজারকে নোটিফিকেশন পাঠান"""
        cursor = self.db.cursor()
        cursor.execute("SELECT user_id FROM users WHERE has_joined_channel = TRUE")
        active_users = cursor.fetchall()
        
        for user in active_users:
            user_id = user[0]
            try:
                await self.send_notification(user_id)
            except Exception as e:
                logging.error(f"Failed to send notification to {user_id}: {str(e)}")
    
    async def send_notification(self, user_id: int):
        """ইউজারকে আকর্ষণীয় নোটিফিকেশন পাঠান"""
        notification_text = (
            "🌟 <b>আপনার আয়ের সুযোগ অপেক্ষা করছে!</b> 🌟\n\n"
            "🕒 এটি আপনার ঘন্টার রিমাইন্ডার:\n"
            "✅ এখনই কিছু কাজ করুন এবং অর্থ উপার্জন করুন!\n\n"
            "📊 আপনার আজকের আয় বাড়ানোর জন্য:\n"
            "▫️ বিজ্ঞাপন দেখুন\n"
            "▫️ রেফার করুন\n"
            "▫️ সার্ভে সম্পূর্ণ করুন\n\n"
            "💰 <i>প্রতিটি ঘন্টায় নতুন সুযোগ আসে!</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton("💰 এখনই আয় শুরু করুন", callback_data="earn_now")],
            [InlineKeyboardButton("⏰ পরে মনে করিয়ে দিন", callback_data="remind_later")]
        ]
        
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(
            chat_id=user_id,
            text=notification_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

class EarningMasterBot:
    def __init__(self):
        self.notification = NotificationSystem()
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """বটের হ্যান্ডলার সেটআপ করুন"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """স্টার্ট কমান্ড হ্যান্ডলার"""
        user = update.effective_user
        welcome_msg = (
            f"👋 <b>স্বাগতম, {user.first_name}!</b>\n\n"
            "আপনি এখন ১ ঘন্টা পরপর আয়ের রিমাইন্ডার পাবেন।\n"
            "নিয়মিত কাজ করে বেশি আয় করুন!"
        )
        
        await update.message.reply_text(
            welcome_msg,
            parse_mode='HTML'
        )
        
        # প্রথম নোটিফিকেশন শিডিউল করুন
        asyncio.create_task(self.notification.send_notification(user.id))
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বাটন ক্লিক হ্যান্ডলার"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "earn_now":
            await query.edit_message_text("🎉 চলুন এখনই আয় শুরু করি!")
        elif query.data == "remind_later":
            await query.edit_message_text("👍 ঠিক আছে, আমি ১ ঘন্টা পরে আবার মনে করিয়ে দেব!")

def main():
    """প্রধান অ্যাপ্লিকেশন এন্ট্রি পয়েন্ট"""
    bot = EarningMasterBot()
    bot.notification.scheduler.start()
    bot.application.run_polling()

if __name__ == "__main__":
    # লগিং কনফিগারেশন
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # ডাটাবেস টেবিল তৈরি
    conn = sqlite3.connect('earning_master.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        has_joined_channel BOOLEAN DEFAULT TRUE
    )
    ''')
    conn.commit()
    conn.close()
    
    main()
