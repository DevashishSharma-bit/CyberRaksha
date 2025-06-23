#!/usr/bin/env python3
"""
CyberRakshak AI Telegram Bot
A Telegram bot interface for the cybersecurity chatbot
"""

import logging
import os
import json
import asyncio
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Import the main CyberRakshak AI class
from main import CyberRakshakAI

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CyberRakshakTelegramBot:
    def __init__(self):
        self.cyber_ai = CyberRakshakAI()
        self.user_languages = {}  # Store user language preferences
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start command handler"""
        user_id = update.effective_user.id
        self.user_languages[user_id] = 'english'  # Default language
        
        welcome_text = """🛡️ Welcome to CyberRakshak AI!

I'm your personal cybersecurity guardian. I can help you:

🔍 Analyze suspicious messages for scams
🚨 Get emergency help if you've been scammed
🔗 Check if URLs/links are safe
📚 Learn about common online scams
🌐 Switch between English and Hindi

Choose what you'd like to do:"""
        
        keyboard = [
            [InlineKeyboardButton("🔍 Analyze Message", callback_data='analyze')],
            [InlineKeyboardButton("🚨 Emergency Help", callback_data='emergency')],
            [InlineKeyboardButton("🔗 Check URL Safety", callback_data='url_check')],
            [InlineKeyboardButton("📚 Learn About Scams", callback_data='learn')],
            [InlineKeyboardButton("🌐 Switch to Hindi", callback_data='hindi')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        current_lang = self.user_languages.get(user_id, 'english')
        
        if query.data == 'analyze':
            await query.edit_message_text(
                "📝 Send me the suspicious message you received (SMS, email, WhatsApp, etc.) and I'll analyze it for potential threats."
            )
            context.user_data['waiting_for'] = 'message_analysis'
            
        elif query.data == 'emergency':
            await self.send_emergency_response(query, current_lang)
            
        elif query.data == 'url_check':
            await query.edit_message_text(
                "🔗 Send me the URL/link you want me to check for safety."
            )
            context.user_data['waiting_for'] = 'url_check'
            
        elif query.data == 'learn':
            await self.send_scam_education(query, current_lang)
            
        elif query.data == 'hindi':
            self.user_languages[user_id] = 'hindi'
            await self.send_main_menu_hindi(query)
            
        elif query.data == 'english':
            self.user_languages[user_id] = 'english'
            await self.send_main_menu_english(query)

    async def send_main_menu_hindi(self, query):
        """Send main menu in Hindi"""
        welcome_text = """🛡️ साइबर रक्षक AI में आपका स्वागत है!

मैं आपका व्यक्तिगत साइबर सुरक्षा गार्डियन हूँ। मैं आपकी मदद कर सकता हूँ:

🔍 संदिग्ध संदेशों का विश्लेषण करने में
🚨 धोखाधड़ी की स्थिति में आपातकालीन सहायता
🔗 URL/लिंक की सुरक्षा जांचने में
📚 आम ऑनलाइन घोटालों के बारे में जानने में
🌐 अंग्रेजी और हिंदी के बीच स्विच करने में

आप क्या करना चाहते हैं:"""
        
        keyboard = [
            [InlineKeyboardButton("🔍 संदेश विश्लेषण", callback_data='analyze')],
            [InlineKeyboardButton("🚨 आपातकालीन सहायता", callback_data='emergency')],
            [InlineKeyboardButton("🔗 URL सुरक्षा जांच", callback_data='url_check')],
            [InlineKeyboardButton("📚 घोटालों के बारे में जानें", callback_data='learn')],
            [InlineKeyboardButton("🌐 Switch to English", callback_data='english')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)

    async def send_main_menu_english(self, query):
        """Send main menu in English"""
        welcome_text = """🛡️ Welcome to CyberRakshak AI!

I'm your personal cybersecurity guardian. I can help you:

🔍 Analyze suspicious messages for scams
🚨 Get emergency help if you've been scammed
🔗 Check if URLs/links are safe
📚 Learn about common online scams
🌐 Switch between English and Hindi

Choose what you'd like to do:"""
        
        keyboard = [
            [InlineKeyboardButton("🔍 Analyze Message", callback_data='analyze')],
            [InlineKeyboardButton("🚨 Emergency Help", callback_data='emergency')],
            [InlineKeyboardButton("🔗 Check URL Safety", callback_data='url_check')],
            [InlineKeyboardButton("📚 Learn About Scams", callback_data='learn')],
            [InlineKeyboardButton("🌐 Switch to Hindi", callback_data='hindi')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages"""
        user_id = update.effective_user.id
        current_lang = self.user_languages.get(user_id, 'english')
        self.cyber_ai.current_language = current_lang
        
        waiting_for = context.user_data.get('waiting_for')
        
        if waiting_for == 'message_analysis':
            await self.analyze_message(update, context)
        elif waiting_for == 'url_check':
            await self.check_url(update, context)
        else:
            # Default behavior - analyze any message sent
            await self.analyze_message(update, context)

    async def analyze_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Analyze a message for threats"""
        message_text = update.message.text
        user_id = update.effective_user.id
        current_lang = self.user_languages.get(user_id, 'english')
        self.cyber_ai.current_language = current_lang
        
        # Send "analyzing" message
        analyzing_msg = "🤖 Analyzing with AI..." if current_lang == 'english' else "🤖 AI के साथ विश्लेषण कर रहा हूँ..."
        status_message = await update.message.reply_text(analyzing_msg)
        
        try:
            # Try Gemini analysis first
            result = None
            if self.cyber_ai.gemini_client:
                result = self.cyber_ai.analyze_message_with_gemini(message_text)
            
            # Fall back to local analysis if Gemini fails
            if not result:
                local_msg = "🔍 Analyzing with local patterns..." if current_lang == 'english' else "🔍 स्थानीय पैटर्न के साथ विश्लेषण..."
                await status_message.edit_text(local_msg)
                result = self.cyber_ai.analyze_message_local(message_text)
            
            # Format and send results
            await status_message.delete()
            await self.send_analysis_result(update, result, current_lang, message_text)
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            error_msg = "⚠️ Analysis failed. Using basic detection." if current_lang == 'english' else "⚠️ विश्लेषण असफल। मूल जांच का उपयोग।"
            await status_message.edit_text(error_msg)
            
            # Fall back to local analysis
            result = self.cyber_ai.analyze_message_local(message_text)
            await self.send_analysis_result(update, result, current_lang, message_text)
        
        # Clear waiting state
        context.user_data.pop('waiting_for', None)

    async def send_analysis_result(self, update: Update, result: Dict, language: str, original_message: str) -> None:
        """Send the analysis result to the user"""
        if result['is_threat']:
            threat_detected = "⚠️ THREAT DETECTED" if language == 'english' else "⚠️ खतरा पाया गया"
            response = f"🔍 *Analysis Result*\n\n{threat_detected}: {result['threat_type'].upper()}\n"
            response += f"Confidence: {result['confidence']:.1%}\n\n"
            response += f"📝 *Explanation:*\n{result['explanation']}\n\n"
            response += f"💡 *Advice:*\n{result['advice']}"
            
            # Check for emergency keywords
            emergency_keywords = ['shared otp', 'gave otp', 'sent money', 'got scammed', 
                                'हो गया', 'दिया', 'भेज दिया', 'धोखा']
            if any(keyword in original_message.lower() for keyword in emergency_keywords):
                emergency_button = InlineKeyboardButton(
                    "🚨 EMERGENCY HELP" if language == 'english' else "🚨 आपातकालीन सहायता", 
                    callback_data='emergency'
                )
                keyboard = [[emergency_button]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text(response, parse_mode='Markdown')
        else:
            safe_msg = "✅ Message appears safe" if language == 'english' else "✅ संदेश सुरक्षित लगता है"
            response = f"🔍 *Analysis Result*\n\n{safe_msg}\n\n📝 Note: {result['explanation']}"
            await update.message.reply_text(response, parse_mode='Markdown')

    async def check_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check URL safety"""
        url = update.message.text.strip()
        user_id = update.effective_user.id
        current_lang = self.user_languages.get(user_id, 'english')
        
        checking_msg = "🔍 Checking URL safety..." if current_lang == 'english' else "🔍 URL सुरक्षा जांच रहा हूँ..."
        status_message = await update.message.reply_text(checking_msg)
        
        try:
            # Try Google Safe Browsing first
            safe_browsing_result = self.cyber_ai.check_url_with_safe_browsing(url)
            
            response = f"🔗 *URL Analysis:* {url}\n\n"
            
            if safe_browsing_result:
                if not safe_browsing_result["is_safe"]:
                    response += "🚨 *DANGER: URL flagged by Google Safe Browsing!*\n"
                    response += f"Threat: {safe_browsing_result['threat_type']}\n"
                    response += f"Details: {safe_browsing_result['details']}\n\n"
                    response += "💡 *Recommendations:*\n• DO NOT visit this URL\n• It contains malware or phishing content\n• Report to authorities if received via message"
                else:
                    response += "✅ Google Safe Browsing: No threats detected\n"
                    response += "⚠️ Always verify unknown links before clicking"
            else:
                # Basic local analysis
                suspicious_indicators = [
                    'bit.ly', 'tinyurl.com', 'short.link', 'rb.gy',
                    'phishing', 'malware', 'suspicious-domain'
                ]
                
                is_suspicious = any(indicator in url.lower() for indicator in suspicious_indicators)
                
                if is_suspicious:
                    response += "⚠️ *WARNING: URL contains suspicious patterns!*\n"
                    response += "💡 Exercise caution with this link"
                else:
                    response += "✅ No obvious suspicious patterns detected\n"
                    response += "⚠️ Always verify unknown links before clicking"
            
            await status_message.delete()
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"URL check failed: {str(e)}")
            error_msg = "⚠️ URL check failed. Please try again." if current_lang == 'english' else "⚠️ URL जांच असफल। कृपया फिर से कोशिश करें।"
            await status_message.edit_text(error_msg)
        
        # Clear waiting state
        context.user_data.pop('waiting_for', None)

    async def send_emergency_response(self, query, language: str) -> None:
        """Send emergency response information"""
        if language == 'english':
            response = """🚨 *EMERGENCY MODE ACTIVATED* 🚨

*Immediate Actions Required:*
1. STOP all transactions immediately
2. Contact your bank/credit card company NOW
3. Change all passwords and PINs
4. File complaint at cybercrime.gov.in
5. Report to local police cyber cell
6. Keep all evidence (screenshots, messages)

*Emergency Contacts:*
📞 Cyber Crime Helpline: 155
📞 Banking Fraud: 1930
📞 CERT-In: 1800-11-4949
📧 CERT-In Email: incident@cert-in.org.in
🌐 Cyber Crime Portal: cybercrime.gov.in

⚠️ Act quickly - time is critical in cyber fraud cases!"""
        else:
            response = """🚨 *आपातकालीन मोड सक्रिय* 🚨

*तत्काल आवश्यक कार्रवाई:*
1. तुरंत सभी लेनदेन बंद करें
2. अभी अपने बैंक/क्रेडिट कार्ड कंपनी से संपर्क करें
3. सभी पासवर्ड और PIN बदलें
4. cybercrime.gov.in पर शिकायत दर्ज करें
5. स्थानीय पुलिस साइबर सेल को रिपोर्ट करें
6. सभी सबूत रखें (स्क्रीनशॉट, संदेश)

*आपातकालीन संपर्क:*
📞 साइबर क्राइम हेल्पलाइन: 155
📞 बैंकिंग फ्रॉड: 1930
📞 CERT-In: 1800-11-4949
📧 CERT-In ईमेल: incident@cert-in.org.in
🌐 साइबर क्राइम पोर्टल: cybercrime.gov.in

⚠️ जल्दी कार्रवाई करें - साइबर फ्रॉड के मामलों में समय महत्वपूर्ण है!"""
        
        await query.edit_message_text(response, parse_mode='Markdown')

    async def send_scam_education(self, query, language: str) -> None:
        """Send educational content about scams"""
        if language == 'english':
            response = """📚 *Common Online Scams - Stay Informed!*

*Phishing:* Fake emails/messages asking for personal info. Look for urgent language, spelling errors, suspicious links.

*OTP Scams:* Fraudsters call pretending to be from bank/company asking for OTP. NEVER share OTP with anyone.

*Job Frauds:* Fake job offers asking for registration fees. Legitimate employers never ask for upfront payments.

*Romance Scams:* Fake profiles on social media/dating apps asking for money after building emotional connection.

*Investment Scams:* Get-rich-quick schemes promising guaranteed returns. Always verify before investing.

*Tech Support Scams:* Fake calls claiming computer issues. Never give remote access to unknown callers.

🛡️ Remember: When in doubt, verify independently!"""
        else:
            response = """📚 *आम ऑनलाइन घोटाले - जानकार रहें!*

*फिशिंग:* व्यक्तिगत जानकारी मांगने वाले नकली ईमेल/संदेश। तत्काल भाषा, वर्तनी त्रुटियों, संदिग्ध लिंक पर ध्यान दें।

*OTP घोटाले:* धोखेबाज बैंक/कंपनी के नाम से फोन करके OTP मांगते हैं। कभी भी OTP किसी के साथ साझा न करें।

*नौकरी धोखाधड़ी:* रजिस्ट्रेशन फीस मांगने वाले नकली जॉब ऑफर। वैध नियोक्ता अग्रिम भुगतान नहीं मांगते।

*रोमांस घोटाले:* भावनात्मक कनेक्शन बनाने के बाद पैसे मांगने वाले नकली प्रोफाइल।

*निवेश घोटाले:* गारंटीड रिटर्न का वादा करने वाली जल्दी-अमीर योजनाएं। निवेश से पहले हमेशा सत्यापित करें।

*तकनीकी सहायता घोटाले:* कंप्यूटर समस्याओं का दावा करने वाले नकली कॉल। अज्ञात कॉल करने वालों को रिमोट एक्सेस न दें।

🛡️ याद रखें: संदेह होने पर स्वतंत्र रूप से सत्यापित करें!"""
        
        await query.edit_message_text(response, parse_mode='Markdown')

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors caused by Updates"""
        logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Main function to run the Telegram bot"""
    # Get Telegram bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not found!")
        print("Please set your Telegram bot token:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get the bot token")
        print("3. Set the TELEGRAM_BOT_TOKEN environment variable")
        return
    
    # Create the bot instance
    bot = CyberRakshakTelegramBot()
    
    # Create the Application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.message_handler))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    print("🤖 CyberRakshak AI Telegram Bot starting...")
    print("✅ Bot is running! Users can now interact with /start")
    
    # Run the bot until Ctrl+C is pressed
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()