#!/usr/bin/env python3
"""
CyberRakshak AI - Cybersecurity Chatbot
A Python command-line chatbot for detecting online scams and providing emergency response guidance
Supports English and Hindi languages
"""

import re
import json
import sys
import os
import datetime
import textwrap
from typing import Dict, List, Tuple, Optional

# Optional AI integrations
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

class CyberRakshakAI:
    def __init__(self):
        self.current_language = 'english'
        self.gemini_client = None
        self.safe_browsing_api_key = None
        
        # Initialize Gemini if available
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY", "")
            if api_key:
                try:
                    self.gemini_client = genai.Client(api_key=api_key)
                    print(f"✅ Gemini AI integration enabled")
                except Exception as e:
                    print(f"⚠️  Gemini initialization failed: {str(e)}")
                    self.gemini_client = None
            else:
                print("⚠️  Gemini API key not found, using local detection only")
        
        # Initialize Google Safe Browsing API key
        self.safe_browsing_api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "AIzaSyDj85Ymbz-2PGBfnmyYVkiwEWCUzoWhm6o")
        if self.safe_browsing_api_key and REQUESTS_AVAILABLE:
            print("✅ Google Safe Browsing API enabled")
        
        # Scam detection patterns
        self.scam_patterns = {
            'phishing': {
                'keywords': [
                    'click here', 'verify account', 'suspended account', 'urgent action',
                    'confirm identity', 'update payment', 'security alert', 'limited time',
                    'claim reward', 'congratulations', 'winner', 'prize', 'lottery',
                    'bank account', 'credit card', 'debit card', 'atm', 'pin'
                ],
                'hindi_keywords': [
                    'यहाँ क्लिक करें', 'खाता सत्यापित करें', 'तुरंत कार्रवाई', 'पहचान पुष्टि',
                    'बैंक खाता', 'एटीएम', 'पिन', 'इनाम', 'लॉटरी', 'जीतने वाले'
                ]
            },
            'otp_scam': {
                'keywords': [
                    'otp', 'one time password', 'verification code', 'security code',
                    'pin', 'passcode', 'authentication', 'share otp', 'send otp',
                    'confirm otp', 'validate', 'activate'
                ],
                'hindi_keywords': [
                    'ओटीपी', 'वन टाइम पासवर्ड', 'सत्यापन कोड', 'सुरक्षा कोड',
                    'पिन', 'पासकोड', 'साझा करें', 'भेजें'
                ]
            },
            'job_fraud': {
                'keywords': [
                    'work from home', 'easy money', 'part time job', 'registration fee',
                    'advance payment', 'guaranteed income', 'no experience required',
                    'data entry', 'copy paste', 'survey work', 'earn daily'
                ],
                'hindi_keywords': [
                    'घर से काम', 'आसान पैसा', 'पार्ट टाइम जॉब', 'रजिस्ट्रेशन फीस',
                    'अग्रिम भुगतान', 'गारंटीड आय', 'डेटा एंट्री', 'रोज कमाएं'
                ]
            },
            'fake_link': {
                'keywords': [
                    'bit.ly', 'tinyurl', 'shortened link', 'suspicious domain',
                    'free download', 'install app', 'update required', 'security patch'
                ],
                'hindi_keywords': [
                    'मुफ्त डाउनलोड', 'ऐप इंस्टॉल', 'अपडेट जरूरी', 'सुरक्षा पैच'
                ]
            }
        }
        
        # Emergency contacts and information
        self.emergency_contacts = {
            'cert_in': {
                'phone': '1800-11-4949',
                'email': 'incident@cert-in.org.in',
                'website': 'https://www.cert-in.org.in'
            },
            'cybercrime': {
                'phone': '155',
                'website': 'https://cybercrime.gov.in'
            },
            'banking_fraud': {
                'phone': '1930',
                'description': 'National Cyber Crime Helpline'
            }
        }
        
        # Language translations
        self.translations = {
            'english': {
                'welcome': "🛡️  Welcome to CyberRakshak AI - Your Cybersecurity Guardian",
                'menu_title': "📋 Main Menu",
                'menu_options': [
                    "1. Analyze suspicious message",
                    "2. Emergency response (I got scammed!)",
                    "3. Check URL/Link safety",
                    "4. Learn about common scams",
                    "5. Switch to Hindi",
                    "6. Exit"
                ],
                'enter_message': "Enter the suspicious message you received:",
                'analysis_result': "🔍 Analysis Result:",
                'threat_detected': "⚠️  THREAT DETECTED",
                'safe_message': "✅ Message appears safe",
                'emergency_mode': "🚨 EMERGENCY MODE ACTIVATED",
                'immediate_actions': "Immediate Actions Required:",
                'contact_info': "Emergency Contacts:",
                'choose_option': "Choose an option (1-6):",
                'invalid_option': "Invalid option. Please try again.",
                'goodbye': "Stay safe online! 🛡️"
            },
            'hindi': {
                'welcome': "🛡️  साइबर रक्षक AI में आपका स्वागत है - आपका साइबर सुरक्षा गार्डियन",
                'menu_title': "📋 मुख्य मेनू",
                'menu_options': [
                    "1. संदिग्ध संदेश का विश्लेषण करें",
                    "2. आपातकालीन प्रतिक्रिया (मैं धोखाधड़ी का शिकार हो गया!)",
                    "3. URL/लिंक की सुरक्षा जांचें",
                    "4. आम धोखाधड़ी के बारे में जानें",
                    "5. अंग्रेजी में स्विच करें",
                    "6. बाहर निकलें"
                ],
                'enter_message': "आपको मिला संदिग्ध संदेश दर्ज करें:",
                'analysis_result': "🔍 विश्लेषण परिणाम:",
                'threat_detected': "⚠️  खतरा पाया गया",
                'safe_message': "✅ संदेश सुरक्षित लगता है",
                'emergency_mode': "🚨 आपातकालीन मोड सक्रिय",
                'immediate_actions': "तत्काल आवश्यक कार्रवाई:",
                'contact_info': "आपातकालीन संपर्क:",
                'choose_option': "विकल्प चुनें (1-6):",
                'invalid_option': "गलत विकल्प। कृपया फिर से कोशिश करें।",
                'goodbye': "ऑनलाइन सुरक्षित रहें! 🛡️"
            }
        }

    def get_text(self, key: str) -> str:
        """Get translated text based on current language"""
        return self.translations[self.current_language].get(key, key)

    def print_header(self):
        """Print application header"""
        print("=" * 60)
        print(self.get_text('welcome'))
        print("=" * 60)
        print()

    def print_menu(self):
        """Print main menu"""
        print(self.get_text('menu_title'))
        print("-" * 30)
        for option in self.get_text('menu_options'):
            print(option)
        print()

    def analyze_message_with_gemini(self, message: str) -> Optional[Dict]:
        """Analyze message using Gemini AI"""
        if not self.gemini_client:
            return None
        
        try:
            prompt = f"""
            Analyze this message for cybersecurity threats. Look for:
            1. Phishing attempts
            2. OTP/PIN scams
            3. Job fraud
            4. Fake links/downloads
            5. Social engineering tactics
            
            Message: "{message}"
            
            Respond in JSON format with:
            {{
                "is_threat": boolean,
                "threat_type": "phishing|otp_scam|job_fraud|fake_link|social_engineering|none",
                "confidence": float (0-1),
                "explanation": "detailed explanation",
                "advice": "actionable advice"
            }}
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                return json.loads(response.text)
            return None
            
        except Exception as e:
            print(f"⚠️  Gemini analysis failed: {str(e)}")
            return None

    def analyze_message_local(self, message: str) -> Dict:
        """Analyze message using local keyword-based detection"""
        message_lower = message.lower()
        threats_found = []
        confidence_scores = []
        
        for threat_type, patterns in self.scam_patterns.items():
            # Check English keywords
            english_matches = sum(1 for keyword in patterns['keywords'] 
                                if keyword.lower() in message_lower)
            
            # Check Hindi keywords
            hindi_matches = sum(1 for keyword in patterns['hindi_keywords'] 
                              if keyword in message)
            
            total_matches = english_matches + hindi_matches
            total_keywords = len(patterns['keywords']) + len(patterns['hindi_keywords'])
            
            if total_matches > 0:
                confidence = min(total_matches / total_keywords * 2, 1.0)  # Cap at 1.0
                threats_found.append((threat_type, confidence, total_matches))
                confidence_scores.append(confidence)
        
        if threats_found:
            # Get the threat with highest confidence
            best_threat = max(threats_found, key=lambda x: x[1])
            threat_type, confidence, matches = best_threat
            
            return {
                'is_threat': True,
                'threat_type': threat_type,
                'confidence': confidence,
                'matches': matches,
                'explanation': self.get_threat_explanation(threat_type),
                'advice': self.get_threat_advice(threat_type)
            }
        else:
            return {
                'is_threat': False,
                'threat_type': 'none',
                'confidence': 0.0,
                'matches': 0,
                'explanation': 'No obvious threat patterns detected.',
                'advice': 'Message appears safe, but always remain cautious online.'
            }

    def get_threat_explanation(self, threat_type: str) -> str:
        """Get explanation for detected threat type"""
        explanations = {
            'english': {
                'phishing': "This appears to be a phishing attempt - a fake message designed to steal your personal information, passwords, or financial details.",
                'otp_scam': "This looks like an OTP scam where fraudsters try to trick you into sharing your One-Time Password or verification codes.",
                'job_fraud': "This seems to be a job fraud scheme offering fake employment opportunities to steal money or personal information.",
                'fake_link': "This message contains suspicious links that might lead to malicious websites or download harmful software."
            },
            'hindi': {
                'phishing': "यह एक फिशिंग प्रयास लगता है - एक नकली संदेश जो आपकी व्यक्तिगत जानकारी, पासवर्ड या वित्तीय विवरण चुराने के लिए डिज़ाइन किया गया है।",
                'otp_scam': "यह एक OTP घोटाला लगता है जहाँ धोखेबाज आपको अपना वन-टाइम पासवर्ड या सत्यापन कोड साझा करने के लिए बरगलाने की कोशिश करते हैं।",
                'job_fraud': "यह एक नौकरी धोखाधड़ी योजना लगती है जो पैसे या व्यक्तिगत जानकारी चुराने के लिए नकली रोजगार के अवसर प्रदान करती है।",
                'fake_link': "इस संदेश में संदिग्ध लिंक हैं जो दुर्भावनापूर्ण वेबसाइटों पर ले जा सकते हैं या हानिकारक सॉफ्टवेयर डाउनलोड कर सकते हैं।"
            }
        }
        return explanations[self.current_language].get(threat_type, "Unknown threat type detected.")

    def get_threat_advice(self, threat_type: str) -> str:
        """Get advice for detected threat type"""
        advice = {
            'english': {
                'phishing': "• Do NOT click any links or download attachments\n• Do NOT provide personal information\n• Verify with the official organization directly\n• Report to cybercrime.gov.in",
                'otp_scam': "• NEVER share OTP, PIN, or verification codes with anyone\n• Banks/companies never ask for OTP over phone/message\n• If you shared OTP, immediately contact your bank\n• Block your cards if compromised",
                'job_fraud': "• Do NOT pay any registration or processing fees\n• Legitimate companies don't ask for upfront payments\n• Verify company details independently\n• Report to local cyber police",
                'fake_link': "• Do NOT click on suspicious links\n• Type URLs manually in browser\n• Use antivirus software\n• Report phishing attempts"
            },
            'hindi': {
                'phishing': "• किसी भी लिंक पर क्लिक न करें या अटैचमेंट डाउनलोड न करें\n• व्यक्तिगत जानकारी प्रदान न करें\n• आधिकारिक संगठन से सीधे सत्यापित करें\n• cybercrime.gov.in पर रिपोर्ट करें",
                'otp_scam': "• कभी भी OTP, PIN, या सत्यापन कोड किसी के साथ साझा न करें\n• बैंक/कंपनियां फोन/संदेश पर OTP नहीं मांगती\n• यदि OTP साझा किया है, तुरंत अपने बैंक से संपर्क करें\n• समझौता होने पर कार्ड ब्लॉक करें",
                'job_fraud': "• कोई रजिस्ट्रेशन या प्रोसेसिंग फीस न दें\n• वैध कंपनियां अग्रिम भुगतान नहीं मांगती\n• कंपनी के विवरण स्वतंत्र रूप से सत्यापित करें\n• स्थानीय साइबर पुलिस को रिपोर्ट करें",
                'fake_link': "• संदिग्ध लिंक पर क्लिक न करें\n• ब्राउज़र में URL मैन्युअल रूप से टाइप करें\n• एंटीवायरस सॉफ्टवेयर का उपयोग करें\n• फिशिंग प्रयासों की रिपोर्ट करें"
            }
        }
        return advice[self.current_language].get(threat_type, "Stay vigilant and report suspicious activities.")

    def analyze_message(self):
        """Main message analysis function"""
        print(self.get_text('enter_message'))
        message = input(">> ").strip()
        
        if not message:
            print("No message entered.")
            return
        
        print("\n" + "="*50)
        print(self.get_text('analysis_result'))
        print("="*50)
        
        # Try Gemini analysis first, fall back to local analysis
        result = None
        if self.gemini_client:
            print("🤖 Analyzing with AI...")
            result = self.analyze_message_with_gemini(message)
        
        if not result:
            print("🔍 Analyzing with local patterns...")
            result = self.analyze_message_local(message)
        
        # Display results
        if result['is_threat']:
            print(f"\n{self.get_text('threat_detected')}: {result['threat_type'].upper()}")
            print(f"Confidence: {result['confidence']:.1%}")
            print(f"\n📝 Explanation:")
            print(textwrap.fill(result['explanation'], width=70))
            print(f"\n💡 Advice:")
            print(result['advice'])
            
            # Check for emergency keywords
            emergency_keywords = ['shared otp', 'gave otp', 'sent money', 'got scammed', 
                                'हो गया', 'दिया', 'भेज दिया', 'धोखा']
            if any(keyword in message.lower() for keyword in emergency_keywords):
                self.emergency_response()
        else:
            print(f"\n{self.get_text('safe_message')}")
            print(f"\n📝 Note: {result['explanation']}")
        
        print("\n" + "="*50)

    def emergency_response(self):
        """Handle emergency situations"""
        print(f"\n🚨 {self.get_text('emergency_mode')} 🚨")
        print("="*50)
        
        immediate_actions = {
            'english': [
                "1. STOP all transactions immediately",
                "2. Contact your bank/credit card company NOW",
                "3. Change all passwords and PINs",
                "4. File complaint at cybercrime.gov.in",
                "5. Report to local police cyber cell",
                "6. Keep all evidence (screenshots, messages)"
            ],
            'hindi': [
                "1. तुरंत सभी लेनदेन बंद करें",
                "2. अभी अपने बैंक/क्रेडिट कार्ड कंपनी से संपर्क करें",
                "3. सभी पासवर्ड और PIN बदलें",
                "4. cybercrime.gov.in पर शिकायत दर्ज करें",
                "5. स्थानीय पुलिस साइबर सेल को रिपोर्ट करें",
                "6. सभी सबूत रखें (स्क्रीनशॉट, संदेश)"
            ]
        }
        
        print(f"{self.get_text('immediate_actions')}")
        for action in immediate_actions[self.current_language]:
            print(action)
        
        print(f"\n{self.get_text('contact_info')}")
        print("-" * 30)
        print(f"📞 Cyber Crime Helpline: {self.emergency_contacts['cybercrime']['phone']}")
        print(f"📞 Banking Fraud: {self.emergency_contacts['banking_fraud']['phone']}")
        print(f"📞 CERT-In: {self.emergency_contacts['cert_in']['phone']}")
        print(f"📧 CERT-In Email: {self.emergency_contacts['cert_in']['email']}")
        print(f"🌐 Cyber Crime Portal: {self.emergency_contacts['cybercrime']['website']}")
        
        print("\n⚠️  Act quickly - time is critical in cyber fraud cases!")

    def check_url_with_safe_browsing(self, url: str) -> Dict:
        """Check URL using Google Safe Browsing API"""
        if not self.safe_browsing_api_key or not REQUESTS_AVAILABLE:
            return None
        
        try:
            api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.safe_browsing_api_key}"
            
            payload = {
                "client": {
                    "clientId": "cyberrakshak-ai",
                    "clientVersion": "1.0"
                },
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE",
                        "SOCIAL_ENGINEERING",
                        "UNWANTED_SOFTWARE",
                        "POTENTIALLY_HARMFUL_APPLICATION"
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            }
            
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "matches" in result and result["matches"]:
                    threat_type = result["matches"][0]["threatType"]
                    return {
                        "is_safe": False,
                        "threat_type": threat_type,
                        "details": f"Google Safe Browsing detected: {threat_type}"
                    }
                else:
                    return {
                        "is_safe": True,
                        "threat_type": None,
                        "details": "No threats detected by Google Safe Browsing"
                    }
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  Safe Browsing API check failed: {str(e)}")
            return None

    def check_url_safety(self):
        """Check URL safety"""
        print("Enter the URL/link you want to check:")
        url = input(">> ").strip()
        
        if not url:
            print("No URL entered.")
            return
        
        print(f"\n🔍 URL Analysis: {url}")
        print("-" * 50)
        
        # Try Google Safe Browsing first
        safe_browsing_result = self.check_url_with_safe_browsing(url)
        
        if safe_browsing_result:
            if not safe_browsing_result["is_safe"]:
                print("🚨 DANGER: URL flagged by Google Safe Browsing!")
                print(f"Threat: {safe_browsing_result['threat_type']}")
                print(f"Details: {safe_browsing_result['details']}")
                print("\n💡 Recommendations:")
                print("• DO NOT visit this URL")
                print("• It contains malware or phishing content")
                print("• Report to authorities if received via message")
                return
            else:
                print("✅ Google Safe Browsing: No threats detected")
        
        # Basic local analysis
        suspicious_indicators = [
            'bit.ly', 'tinyurl.com', 'short.link', 'rb.gy',
            'phishing', 'malware', 'suspicious-domain',
            'free-download', 'urgent-update', 'security-alert'
        ]
        
        is_suspicious = any(indicator in url.lower() for indicator in suspicious_indicators)
        
        if is_suspicious:
            print("⚠️  WARNING: URL contains suspicious patterns!")
            print("Reasons:")
            for indicator in suspicious_indicators:
                if indicator in url.lower():
                    print(f"  • Contains: {indicator}")
            
            print("\n💡 Recommendations:")
            print("• Exercise caution with this link")
            print("• Verify the source before clicking")
            print("• Use a URL scanner like VirusTotal")
        else:
            print("✅ No obvious suspicious patterns detected")
            print("⚠️  Always verify unknown links before clicking")

    def learn_about_scams(self):
        """Educational content about common scams"""
        scam_info = {
            'english': {
                'title': "🎓 Common Online Scams - Stay Informed!",
                'scams': {
                    'Phishing': "Fake emails/messages asking for personal info. Look for urgent language, spelling errors, suspicious links.",
                    'OTP Scams': "Fraudsters call pretending to be from bank/company asking for OTP. NEVER share OTP with anyone.",
                    'Job Frauds': "Fake job offers asking for registration fees. Legitimate employers never ask for upfront payments.",
                    'Romance Scams': "Fake profiles on social media/dating apps asking for money after building emotional connection.",
                    'Investment Scams': "Get-rich-quick schemes promising guaranteed returns. Always verify before investing.",
                    'Tech Support Scams': "Fake calls claiming computer issues. Never give remote access to unknown callers."
                }
            },
            'hindi': {
                'title': "🎓 आम ऑनलाइन घोटाले - जानकार रहें!",
                'scams': {
                    'फिशिंग': "व्यक्तिगत जानकारी मांगने वाले नकली ईमेल/संदेश। तत्काल भाषा, वर्तनी त्रुटियों, संदिग्ध लिंक पर ध्यान दें।",
                    'OTP घोटाले': "धोखेबाज बैंक/कंपनी के नाम से फोन करके OTP मांगते हैं। कभी भी OTP किसी के साथ साझा न करें।",
                    'नौकरी धोखाधड़ी': "रजिस्ट्रेशन फीस मांगने वाले नकली जॉब ऑफर। वैध नियोक्ता अग्रिम भुगतान नहीं मांगते।",
                    'रोमांस घोटाले': "भावनात्मक कनेक्शन बनाने के बाद पैसे मांगने वाले नकली प्रोफाइल।",
                    'निवेश घोटाले': "गारंटीड रिटर्न का वादा करने वाली जल्दी-अमीर योजनाएं। निवेश से पहले हमेशा सत्यापित करें।",
                    'टेक सपोर्ट घोटाले': "कंप्यूटर समस्याओं का दावा करने वाले नकली कॉल। अज्ञात कॉलर को रिमोट एक्सेस न दें।"
                }
            }
        }
        
        info = scam_info[self.current_language]
        print(f"\n{info['title']}")
        print("="*60)
        
        for scam_type, description in info['scams'].items():
            print(f"\n🔸 {scam_type}:")
            print(f"   {description}")
        
        print(f"\n💡 {'Remember' if self.current_language == 'english' else 'याद रखें'}:")
        print("• Think before you click")
        print("• Verify before you trust")
        print("• Report suspicious activities")

    def switch_language(self):
        """Switch between English and Hindi"""
        if self.current_language == 'english':
            self.current_language = 'hindi'
            print("भाषा हिंदी में बदल गई। 🇮🇳")
        else:
            self.current_language = 'english'
            print("Language switched to English. 🇺🇸")

    def run(self):
        """Main application loop"""
        self.print_header()
        
        while True:
            try:
                self.print_menu()
                choice = input(self.get_text('choose_option')).strip()
                
                if choice == '1':
                    self.analyze_message()
                elif choice == '2':
                    self.emergency_response()
                elif choice == '3':
                    self.check_url_safety()
                elif choice == '4':
                    self.learn_about_scams()
                elif choice == '5':
                    self.switch_language()
                elif choice == '6':
                    print(f"\n{self.get_text('goodbye')}")
                    break
                else:
                    print(self.get_text('invalid_option'))
                
                # Wait for user input before continuing
                input("\nPress Enter to continue...")
                print("\n" + "="*60 + "\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{self.get_text('goodbye')}")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                print("Please try again.")

def main():
    """Main entry point"""
    try:
        chatbot = CyberRakshakAI()
        chatbot.run()
    except Exception as e:
        print(f"❌ Failed to start CyberRakshak AI: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
