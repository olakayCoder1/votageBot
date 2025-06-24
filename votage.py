#!/usr/bin/env python3
"""
Telegram Autoresponder & Reminder Bot
A comprehensive bot that handles automatic responses and reminder management.
"""

import asyncio
import logging
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, JobQueue
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@dataclass
class AutoResponse:
    """Data class for auto-response rules"""
    trigger: str
    response: str
    exact_match: bool = False
    case_sensitive: bool = False
    enabled: bool = True

@dataclass
class Reminder:
    """Data class for reminders"""
    user_id: int
    message: str
    datetime: datetime
    recurring: Optional[str] = None  # 'daily', 'weekly', 'monthly'
    chat_id: int = None

class AutoResponderBot:
    def __init__(self, token: str, data_file: str = "bot_data.json"):
        self.token = token
        self.data_file = Path(data_file)
        self.auto_responses: Dict[int, List[AutoResponse]] = {}
        self.reminders: List[Reminder] = []
        self.load_data()
        
    def load_data(self):
        """Load bot data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load auto responses
                for user_id, responses in data.get('auto_responses', {}).items():
                    self.auto_responses[int(user_id)] = [
                        AutoResponse(**resp) for resp in responses
                    ]
                
                # Load reminders
                for reminder_data in data.get('reminders', []):
                    reminder_data['datetime'] = datetime.fromisoformat(reminder_data['datetime'])
                    self.reminders.append(Reminder(**reminder_data))
                    
            except Exception as e:
                logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        """Save bot data to file"""
        try:
            data = {
                'auto_responses': {
                    str(user_id): [asdict(resp) for resp in responses]
                    for user_id, responses in self.auto_responses.items()
                },
                'reminders': []
            }
            
            # Convert reminders to serializable format
            for reminder in self.reminders:
                reminder_dict = asdict(reminder)
                reminder_dict['datetime'] = reminder.datetime.isoformat()
                data['reminders'].append(reminder_dict)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")


    async def start_command_old(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with new welcome flow"""
        user_name = update.effective_user.first_name or "Friend"
        
        # First welcome message
        welcome_text = f"""
🎉 Congratulations {user_name}!

One of our users just made 35% profit in a single week using Pilot AI.

Now it's your turn to see what this powerful bot can do.
        """
        
        keyboard = [
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        
        # Wait a moment and send second message
        await asyncio.sleep(2)
        
        second_message = f"""
👉 SEND a MESSAGE to our team now: 👉 @bullpilotofficial 

Just type: "Activate Bot Trial"
They'll get your access ready right away.
        """
        
        keyboard2 = [
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")]
        ]
        reply_markup2 = InlineKeyboardMarkup(keyboard2)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=second_message,
            reply_markup=reply_markup2
        )
        
        # Wait another moment and send third message
        await asyncio.sleep(3)
        
        third_message = f"""
✅ Final Step:

Once you've messaged the team, come back here and click the link below to complete your registration here 👇

👉 [Registration Link](https://votage-page.vercel.app)

This helps us understand your trading experience and lock in your trial access.

You can also request a Zoom call or physical office meeting through the form.

⚠️ Do this now, {user_name} - slots are almost gone!
        """
        
        keyboard3 = [
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")]
        ]
        reply_markup3 = InlineKeyboardMarkup(keyboard3)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=third_message,
            parse_mode='Markdown',
            reply_markup=reply_markup3
        )
        
        # Wait and send final message
        await asyncio.sleep(4)
        
        final_message = f"""
Great job, {user_name}! 
Now you're ready!! ✅

Let's lock this in:
Click the link below to enroll for your trial + webinar access:

👉 [Enrollment Link](https://votage-page.vercel.app)

Seats are filling up fast — only a few left!

This won't take long.
Once you fill the form, my team gets everything they need to plug you in properly.

After registering through the link above, send a quick message to my team:
@bullpilotofficial — just say "I've filled the form"

You can also reach me directly here:
@blisswrld10
        """
        
        keyboard4 = [
            [InlineKeyboardButton("📝 Enrollment Link", url="https://votage-page.vercel.app")],
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")],
            [InlineKeyboardButton("💬 Direct Contact", url="https://t.me/blisswrld10")]
        ]
        reply_markup4 = InlineKeyboardMarkup(keyboard4)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=final_message,
            parse_mode='Markdown',
            reply_markup=reply_markup4
        )



    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with new welcome flow"""
        user_name = update.effective_user.first_name or "Friend"
        
        # First welcome message
        welcome_text = f"""
    🎉 Congratulations {user_name}!

    One of our users just made 35% profit in a single week using Pilot AI.

    Now it's your turn to see what this powerful bot can do.
        """
        
        keyboard = [
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        
        # Wait a moment and send second message
        await asyncio.sleep(1)
        
        second_message = f"""
    👉 SEND a MESSAGE to our team now: 👉 @bullpilotofficial 

    Just type: "Activate Bot Trial"
    They'll get your access ready right away.
        """
        
        keyboard2 = [
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")]
        ]
        reply_markup2 = InlineKeyboardMarkup(keyboard2)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=second_message,
            reply_markup=reply_markup2
        )
        
        # Wait another moment and send third message
        await asyncio.sleep(1)
        
        third_message = f"""
    ✅ Final Step:

    Once you've messaged the team, come back here and click the link below to complete your registration here 👇

    👉 [Registration Link](https://votage-page.vercel.app)

    This helps us understand your trading experience and lock in your trial access.

    You can also request a Zoom call or physical office meeting through the form.

    ⚠️ Do this now, {user_name} - slots are almost gone!
        """
        
        keyboard3 = [
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")]
        ]
        reply_markup3 = InlineKeyboardMarkup(keyboard3)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=third_message,
            parse_mode='Markdown',
            reply_markup=reply_markup3
        )
        
        # NEW PROMOTIONAL MESSAGE - Add this here
        await asyncio.sleep(3)
        
        promo_message = """
    🎯 Free Bot Trial (No payment needed)
    ✅ Step 1: Register here → https://tinyurl.com/bullpilot
    ✅ Step 2: Fund $200 minimum  
    ✅ Step 3: Send "TRIAL" to activate your trial
    This activates the bot to trade for you. You earn passively 💰
        """
        
        keyboard_promo = [
            [InlineKeyboardButton("🚀 Register Now", url="https://tinyurl.com/bullpilot")],
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")]
        ]
        reply_markup_promo = InlineKeyboardMarkup(keyboard_promo)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=promo_message,
            reply_markup=reply_markup_promo
        )
        
        # Wait and send final message
        await asyncio.sleep(2)
        
        final_message = f"""
    Great job, {user_name}! 
    Now you're ready!! ✅

    Let's lock this in:
    Click the link below to enroll for your trial + webinar access:

    👉 [Enrollment Link](https://votage-page.vercel.app)

    Seats are filling up fast — only a few left!

    This won't take long.
    Once you fill the form, my team gets everything they need to plug you in properly.

    After registering through the link above, send a quick message to my team:
    @bullpilotofficial — just say "I've filled the form"

    You can also reach me directly here:
    @blisswrld10
        """
        
        keyboard4 = [
            [InlineKeyboardButton("📝 Enrollment Link", url="https://votage-page.vercel.app")],
            [InlineKeyboardButton("📩 Contact Support", url="https://t.me/bullpilotofficial")],
            [InlineKeyboardButton("💬 Direct Contact", url="https://t.me/blisswrld10")]
        ]
        reply_markup4 = InlineKeyboardMarkup(keyboard4)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=final_message,
            parse_mode='Markdown',
            reply_markup=reply_markup4
        )


    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin - you can customize this"""
        # Add your admin user IDs here
        admin_ids = [
            # Add your Telegram user ID here
            # Example: 123456789
        ]
        return user_id in admin_ids

    async def add_response_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addresponse command"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        if not context.args:
            await update.message.reply_text(
                "Please provide trigger and response separated by '|'\n"
                "Example: `/addresponse hello | Hi there!`",
                parse_mode='Markdown'
            )
            return
        
        text = ' '.join(context.args)
        if '|' not in text:
            await update.message.reply_text("Please separate trigger and response with '|'")
            return
        
        trigger, response = text.split('|', 1)
        trigger = trigger.strip()
        response = response.strip()
        
        if not trigger or not response:
            await update.message.reply_text("Both trigger and response must be provided")
            return
        
        user_id = update.effective_user.id
        if user_id not in self.auto_responses:
            self.auto_responses[user_id] = []
        
        auto_response = AutoResponse(trigger=trigger, response=response)
        self.auto_responses[user_id].append(auto_response)
        self.save_data()
        
        await update.message.reply_text(
            f"✅ Auto-response added!\n\n"
            f"*Trigger:* {trigger}\n"
            f"*Response:* {response}",
            parse_mode='Markdown'
        )

    async def add_exact_response_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addresponse_exact command"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        if not context.args:
            await update.message.reply_text(
                "Please provide trigger and response separated by '|'\n"
                "Example: `/addresponse_exact hello | Hi there!`",
                parse_mode='Markdown'
            )
            return
        
        text = ' '.join(context.args)
        if '|' not in text:
            await update.message.reply_text("Please separate trigger and response with '|'")
            return
        
        trigger, response = text.split('|', 1)
        trigger = trigger.strip()
        response = response.strip()
        
        user_id = update.effective_user.id
        if user_id not in self.auto_responses:
            self.auto_responses[user_id] = []
        
        auto_response = AutoResponse(trigger=trigger, response=response, exact_match=True)
        self.auto_responses[user_id].append(auto_response)
        self.save_data()
        
        await update.message.reply_text(
            f"✅ Exact-match auto-response added!\n\n"
            f"*Trigger:* {trigger}\n"
            f"*Response:* {response}",
            parse_mode='Markdown'
        )

    async def list_responses_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listresponses command"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        user_id = update.effective_user.id
        responses = self.auto_responses.get(user_id, [])
        
        if not responses:
            await update.message.reply_text("You don't have any auto-responses set up.")
            return
        
        text = "*Your Auto-Responses:*\n\n"
        for i, resp in enumerate(responses, 1):
            status = "✅" if resp.enabled else "❌"
            match_type = "Exact" if resp.exact_match else "Contains"
            text += f"{i}. {status} *{resp.trigger}*\n"
            text += f"   └ {resp.response}\n"
            text += f"   └ Match: {match_type}\n\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def delete_response_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /deleteresponse command"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        if not context.args:
            await update.message.reply_text("Please provide the response number to delete")
            return
        
        try:
            response_num = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Please provide a valid number")
            return
        
        user_id = update.effective_user.id
        responses = self.auto_responses.get(user_id, [])
        
        if response_num < 1 or response_num > len(responses):
            await update.message.reply_text("Invalid response number")
            return
        
        deleted_response = responses.pop(response_num - 1)
        self.save_data()
        
        await update.message.reply_text(
            f"✅ Deleted auto-response:\n*{deleted_response.trigger}*",
            parse_mode='Markdown'
        )

    async def toggle_response_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /toggleresponse command"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        if not context.args:
            await update.message.reply_text("Please provide the response number to toggle")
            return
        
        try:
            response_num = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Please provide a valid number")
            return
        
        user_id = update.effective_user.id
        responses = self.auto_responses.get(user_id, [])
        
        if response_num < 1 or response_num > len(responses):
            await update.message.reply_text("Invalid response number")
            return
        
        response = responses[response_num - 1]
        response.enabled = not response.enabled
        self.save_data()
        
        status = "enabled" if response.enabled else "disabled"
        await update.message.reply_text(
            f"✅ Auto-response {status}:\n*{response.trigger}*",
            parse_mode='Markdown'
        )

    def parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse various time formats into datetime"""
        now = datetime.now()
        time_str = time_str.lower().strip()
        
        logger.info(f"Parsing time string: '{time_str}'")
        logger.info(f"Current time: {now}")
        
        # Handle relative times (10s, 5m, 2h, 3d)
        if re.match(r'^\d+[smhd]$', time_str):
            num = int(time_str[:-1])
            unit = time_str[-1]
            
            result = None
            if unit == 's':
                result = now + timedelta(seconds=num)
            elif unit == 'm':
                result = now + timedelta(minutes=num)
            elif unit == 'h':
                result = now + timedelta(hours=num)
            elif unit == 'd':
                result = now + timedelta(days=num)
            
            logger.info(f"Parsed relative time: {result}")
            return result
        
        # Handle "tomorrow" or "tomorrow 9am"
        if time_str.startswith('tomorrow'):
            tomorrow = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
            if len(time_str) > 8:  # "tomorrow 9am"
                time_part = time_str[9:].strip()
                try:
                    time_obj = datetime.strptime(time_part, '%I%p').time()
                    tomorrow = tomorrow.replace(hour=time_obj.hour, minute=time_obj.minute)
                except:
                    try:
                        time_obj = datetime.strptime(time_part, '%H:%M').time()
                        tomorrow = tomorrow.replace(hour=time_obj.hour, minute=time_obj.minute)
                    except:
                        pass
            logger.info(f"Parsed tomorrow: {tomorrow}")
            return tomorrow
        
        # Handle specific datetime formats
        formats = [
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d-%m-%Y %H:%M'
        ]
        
        for fmt in formats:
            try:
                result = datetime.strptime(time_str, fmt)
                logger.info(f"Parsed specific datetime: {result}")
                return result
            except ValueError:
                continue
        
        logger.warning(f"Could not parse time string: '{time_str}'")
        return None

    async def remind_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remind command with better error handling"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: `/remind <time> <message>`\n\n"
                "Time examples:\n"
                "• `10s` - 10 seconds\n"
                "• `5m` - 5 minutes\n"
                "• `2h` - 2 hours\n"
                "• `3d` - 3 days\n"
                "• `tomorrow 9am`\n"
                "• `2024-12-25 10:30`",
                parse_mode='Markdown'
            )
            return
        
        time_str = context.args[0]
        message = ' '.join(context.args[1:])
        
        remind_time = self.parse_time(time_str)
        if not remind_time:
            await update.message.reply_text("Invalid time format. Please check the examples in /admin")
            return
        
        if remind_time <= datetime.now():
            await update.message.reply_text("Reminder time must be in the future")
            return
        
        # Calculate delay in seconds for debugging
        delay_seconds = (remind_time - datetime.now()).total_seconds()
        logger.info(f"Setting reminder for {delay_seconds} seconds from now")
        
        reminder = Reminder(
            user_id=update.effective_user.id,
            message=message,
            datetime=remind_time,
            chat_id=update.effective_chat.id
        )
        
        self.reminders.append(reminder)
        self.save_data()
        
        # Check if job_queue is available
        if context.job_queue is None:
            await update.message.reply_text("❌ Reminder scheduling is not available. Please restart the bot.")
            return
        
        # Schedule the reminder with better error handling
        try:
            # Use timedelta for all delays to avoid timezone issues
            job = context.job_queue.run_once(
                self.send_reminder,
                when=timedelta(seconds=delay_seconds),
                data={'reminder': reminder, 'original_time': remind_time},
                name=f"reminder_{update.effective_user.id}_{len(self.reminders)}"
            )
            
            logger.info(f"Successfully scheduled reminder job: {job.name}")
            logger.info(f"Reminder will fire in {delay_seconds} seconds")
            logger.info(f"Current time: {datetime.now()}")
            
        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}")
            await update.message.reply_text(f"❌ Error scheduling reminder: {str(e)}")
            # Remove the reminder since scheduling failed
            self.reminders.remove(reminder)
            self.save_data()
            return
        
        await update.message.reply_text(
            f"⏰ Reminder set!\n\n"
            f"*Time:* {remind_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"*Message:* {message}\n"
            f"*Delay:* {delay_seconds:.1f} seconds",
            parse_mode='Markdown'
        )

    async def reminders_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reminders command"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        user_id = update.effective_user.id
        user_reminders = [r for r in self.reminders if r.user_id == user_id]
        
        if not user_reminders:
            await update.message.reply_text("You don't have any reminders set up.")
            return
        
        text = "*Your Reminders:*\n\n"
        for i, reminder in enumerate(user_reminders, 1):
            text += f"{i}. {reminder.datetime.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"   └ {reminder.message}\n\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def delete_reminder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /deletereminder command"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("You don't have permission to use this command.")
            return
            
        if not context.args:
            await update.message.reply_text("Please provide the reminder number to delete")
            return
        
        try:
            reminder_num = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Please provide a valid number")
            return
        
        user_id = update.effective_user.id
        user_reminders = [r for r in self.reminders if r.user_id == user_id]
        
        if reminder_num < 1 or reminder_num > len(user_reminders):
            await update.message.reply_text("Invalid reminder number")
            return
        
        reminder_to_delete = user_reminders[reminder_num - 1]
        self.reminders.remove(reminder_to_delete)
        self.save_data()
        
        await update.message.reply_text(
            f"✅ Deleted reminder:\n{reminder_to_delete.message}",
            parse_mode='Markdown'
        )

    async def send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send a scheduled reminder with better error handling"""
        try:
            reminder = context.job.data['reminder']
            original_time = context.job.data['original_time']
            
            logger.info(f"Sending reminder: {reminder.message}")
            logger.info(f"Scheduled for: {original_time}")
            logger.info(f"Current time: {datetime.now()}")
            
            await context.bot.send_message(
                chat_id=reminder.chat_id,
                text=f"⏰ *Reminder:*\n{reminder.message}",
                parse_mode='Markdown'
            )
            
            logger.info("Reminder sent successfully!")
            
            # Remove completed reminder
            if reminder in self.reminders:
                self.reminders.remove(reminder)
                self.save_data()
                logger.info("Reminder removed from list")
                
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages for auto-responses"""
        if not update.message or not update.message.text:
            return
        
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check for auto-responses
        responses = self.auto_responses.get(user_id, [])
        for response in responses:
            if not response.enabled:
                continue
            
            trigger = response.trigger
            if not response.case_sensitive:
                trigger = trigger.lower()
                message_text_check = message_text.lower()
            else:
                message_text_check = message_text
            
            # Check for match
            match = False
            if response.exact_match:
                match = message_text_check == trigger
            else:
                match = trigger in message_text_check
            
            if match:
                await update.message.reply_text(response.response)
                break  # Only send first matching response

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "manage_responses":
            text = """
📝 *Auto-Response Management*

Use these commands to manage your auto-responses:
• `/addresponse <trigger> | <response>` - Add new response
• `/addresponse_exact <trigger> | <response>` - Add exact match response
• `/listresponses` - View all responses
• `/deleteresponse <number>` - Delete response
• `/toggleresponse <number>` - Enable/disable response
            """
            await query.edit_message_text(text, parse_mode='Markdown')
            
        elif query.data == "manage_reminders":
            text = """
⏰ *Reminder Management*

Use these commands to manage your reminders:
• `/remind <time> <message>` - Set new reminder
• `/reminders` - View all reminders
• `/deletereminder <number>` - Delete reminder

*Time formats:*
• `10s`, `5m`, `2h`, `3d` - Relative time
• `tomorrow 9am` - Tomorrow at 9 AM
• `2024-12-25 10:30` - Specific date and time
            """
            await query.edit_message_text(text, parse_mode='Markdown')
            
        elif query.data == "help":
            await self.admin_command(update, context)

    def setup_jobs(self, job_queue: JobQueue):
        """Setup scheduled jobs for existing reminders"""
        if job_queue is None:
            logger.error("JobQueue is None - reminders will not work!")
            return
        
        logger.info(f"Setting up {len(self.reminders)} existing reminders")
        
        for i, reminder in enumerate(self.reminders):
            if reminder.datetime > datetime.now():
                try:
                    delay_seconds = (reminder.datetime - datetime.now()).total_seconds()
                    
                    # Use timedelta for all delays to avoid timezone issues
                    job = job_queue.run_once(
                        self.send_reminder,
                        when=timedelta(seconds=delay_seconds),
                        data={'reminder': reminder, 'original_time': reminder.datetime},
                        name=f"startup_reminder_{i}"
                    )
                    
                    logger.info(f"Scheduled startup reminder: {reminder.message} at {reminder.datetime}")
                except Exception as e:
                    logger.error(f"Error scheduling startup reminder: {e}")
            else:
                logger.info(f"Skipping past reminder: {reminder.message}")

    def run(self):
        """Start the bot with enhanced logging"""
        logger.info("Initializing bot...")
        
        try:
            app = Application.builder().token(self.token).build()
        except Exception as e:
            logger.error(f"Error building application: {e}")
            return
        
        # Check if job queue is available
        if app.job_queue is None:
            logger.error("JobQueue is not available! Install with: pip install 'python-telegram-bot[job-queue]'")
            print("⚠️  WARNING: Reminders will not work without JobQueue!")
            print("Run: pip install 'python-telegram-bot[job-queue]'")
        else:
            logger.info("JobQueue is available - reminders will work!")
            logger.info(f"Scheduler class: {type(app.job_queue.scheduler)}")
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start_command))
        # app.add_handler(CommandHandler("admin", self.admin_command))  # New admin command
        app.add_handler(CommandHandler("addresponse", self.add_response_command))
        app.add_handler(CommandHandler("addresponse_exact", self.add_exact_response_command))
        app.add_handler(CommandHandler("listresponses", self.list_responses_command))
        app.add_handler(CommandHandler("deleteresponse", self.delete_response_command))
        app.add_handler(CommandHandler("toggleresponse", self.toggle_response_command))
        app.add_handler(CommandHandler("remind", self.remind_command))
        app.add_handler(CommandHandler("reminders", self.reminders_command))
        app.add_handler(CommandHandler("deletereminder", self.delete_reminder_command))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Setup existing reminders
        if app.job_queue is not None:
            self.setup_jobs(app.job_queue)
        
        logger.info("Bot starting...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Replace with your bot token from @BotFather
    # get the token from env
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please set your bot token!")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your bot token")
        print("3. Set BOT_TOKEN environment variable")
        print("   Example: export BOT_TOKEN='your_token_here'")
        exit(1)
    
    bot = AutoResponderBot(BOT_TOKEN)
    bot.run()