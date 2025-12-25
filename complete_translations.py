#!/usr/bin/env python3
"""
Complete all missing translations for global expansion
"""

import json
from pathlib import Path

# Translation data for all languages
TRANSLATIONS = {
    "ar": {
        "welcome": {
            "title": "🌟 مرحباً بك في روبوت UR Trading Expert!",
            "description": "رفيق التداول الخاص بك المدعوم بالذكاء الاصطناعي مع إشارات احترافية",
            "get_started": "ابدأ الآن",
            "features": "الميزات",
            "pricing": "الأسعار"
        },
        "commands": {
            "help": "المساعدة والأوامر",
            "signals": "إشارات التداول",
            "analytics": "التحليلات",
            "education": "التعليم",
            "notifications": "الإشعارات",
            "account": "حسابي",
            "settings": "الإعدادات"
        },
        "signals": {
            "direction_buy": "📈 شراء",
            "direction_sell": "📉 بيع",
            "direction_hold": "⏸️ انتظار",
            "confidence": "الثقة",
            "entry_price": "سعر الدخول",
            "stop_loss": "وقف الخسارة",
            "take_profit": "جني الأرباح",
            "risk_reward": "نسبة المخاطرة/المكافأة",
            "analysis": "التحليل",
            "generated_at": "تم إنشاؤه",
            "signal_quality": "جودة الإشارة",
            "trading_hours": "ساعات التداول"
        },
        "markets": {
            "forex": "الفوركس",
            "crypto": "العملات الرقمية",
            "commodities": "السلع",
            "futures": "العقود المستقبلية",
            "international": "الأسواق الدولية"
        },
        "subscription": {
            "free_tier": "مجاني",
            "premium_tier": "بريميوم",
            "vip_tier": "VIP",
            "upgrade_required": "يتطلب ترقية",
            "upgrade_now": "ترقية الآن",
            "billing": "الفواتير والاشتراك",
            "upgrade_options": "خيارات الترقية",
            "full_international": "وصول دولي كامل",
            "limited_international": "وصول دولي محدود",
            "use_subscribe": "استخدم /subscribe للترقية!"
        },
        "errors": {
            "general_error": "حدث خطأ. يرجى المحاولة مرة أخرى.",
            "permission_denied": "ليس لديك صلاحية لاستخدام هذه الوظيفة.",
            "rate_limit": "طلبات كثيرة جداً. يرجى الانتظار والمحاولة مرة أخرى.",
            "service_unavailable": "الخدمة غير متوفرة مؤقتاً.",
            "invalid_command": "أمر غير صحيح. استخدم /help لرؤية الأوامر المتاحة."
        },
        "time": {
            "just_now": "الآن",
            "minutes_ago": "منذ {} دقائق",
            "hours_ago": "منذ {} ساعات",
            "days_ago": "منذ {} أيام",
            "yesterday": "أمس",
            "today": "اليوم",
            "tomorrow": "غداً"
        },
        "numbers": {
            "decimal_separator": ".",
            "thousands_separator": ",",
            "currency_format": "${:,.2f}",
            "percentage_format": "{:.1f}%"
        },
        "trading": {
            "long_position": "صفقة شراء",
            "short_position": "صفقة بيع",
            "leverage": "الرافعة المالية",
            "margin": "الهامش",
            "pnl": "الربح والخسارة",
            "profit": "الربح",
            "loss": "الخسارة",
            "break_even": "نقطة التعادل",
            "trend": "الاتجاه",
            "support": "الدعم",
            "resistance": "المقاومة",
            "spread": "الفرق"
        },
        "international": {
            "cny_title": "🇨🇳 السوق الصيني (CNY)",
            "brl_title": "🇧🇷 الريال البرازيلي (BRL)",
            "eth_title": "₿ عقود إيثريوم (ETH)",
            "asian_session": "الجلسة الآسيوية",
            "americas_session": "الجلسة الأمريكية",
            "crypto_247": "العملات الرقمية 24/7",
            "emerging_market": "سوق ناشئ",
            "high_volatility": "تقلب عالي",
            "low_volatility": "تقلب منخفض",
            "extreme_volatility": "تقلب شديد",
            "processing_asian": "معالجة بيانات السوق الآسيوي...",
            "analyzing_cny": "تحليل إشارات USD/CNY",
            "market_info": "معلومات السوق",
            "cny_unavailable": "إشارة CNY غير متوفرة",
            "try_again": "حاول مرة أخرى خلال دقائق قليلة",
            "cny_error": "خطأ في إشارة CNY"
        }
    },
    "ru": {
        "welcome": {
            "title": "🌟 Добро пожаловать в UR Trading Expert Bot!",
            "description": "Ваш помощник по трейдингу на базе ИИ с профессиональными сигналами",
            "get_started": "Начать",
            "features": "Функции",
            "pricing": "Цены"
        },
        "commands": {
            "help": "Помощь и команды",
            "signals": "Торговые сигналы",
            "analytics": "Аналитика",
            "education": "Обучение",
            "notifications": "Уведомления",
            "account": "Мой аккаунт",
            "settings": "Настройки"
        },
        "signals": {
            "direction_buy": "📈 ПОКУПКА",
            "direction_sell": "📉 ПРОДАЖА",
            "direction_hold": "⏸️ ДЕРЖАТЬ",
            "confidence": "Уверенность",
            "entry_price": "Цена входа",
            "stop_loss": "Стоп-лосс",
            "take_profit": "Тейк-профит",
            "risk_reward": "Соотношение риска/прибыли",
            "analysis": "Анализ",
            "generated_at": "Создано",
            "signal_quality": "Качество сигнала",
            "trading_hours": "Торговые часы"
        },
        "markets": {
            "forex": "Форекс",
            "crypto": "Криптовалюты",
            "commodities": "Товары",
            "futures": "Фьючерсы",
            "international": "Международные рынки"
        },
        "subscription": {
            "free_tier": "Бесплатно",
            "premium_tier": "Премиум",
            "vip_tier": "VIP",
            "upgrade_required": "Требуется обновление",
            "upgrade_now": "Обновить сейчас",
            "billing": "Биллинг и подписка",
            "upgrade_options": "Варианты обновления",
            "full_international": "Полный международный доступ",
            "limited_international": "Ограниченный международный доступ",
            "use_subscribe": "Используйте /subscribe для обновления!"
        },
        "errors": {
            "general_error": "Произошла ошибка. Попробуйте еще раз.",
            "permission_denied": "У вас нет прав для использования этой функции.",
            "rate_limit": "Слишком много запросов. Подождите и попробуйте еще раз.",
            "service_unavailable": "Сервис временно недоступен.",
            "invalid_command": "Неверная команда. Используйте /help для просмотра доступных команд."
        },
        "time": {
            "just_now": "Только что",
            "minutes_ago": "Минут назад: {}",
            "hours_ago": "Часов назад: {}",
            "days_ago": "Дней назад: {}",
            "yesterday": "Вчера",
            "today": "Сегодня",
            "tomorrow": "Завтра"
        },
        "numbers": {
            "decimal_separator": ",",
            "thousands_separator": " ",
            "currency_format": "${:,.2f}",
            "percentage_format": "{:.1f}%"
        },
        "trading": {
            "long_position": "Длинная позиция",
            "short_position": "Короткая позиция",
            "leverage": "Плечо",
            "margin": "Маржа",
            "pnl": "Прибыль/Убыток",
            "profit": "Прибыль",
            "loss": "Убыток",
            "break_even": "Безубыточность",
            "trend": "Тренд",
            "support": "Поддержка",
            "resistance": "Сопротивление",
            "spread": "Спред"
        },
        "international": {
            "cny_title": "🇨🇳 Китайский рынок (CNY)",
            "brl_title": "🇧🇷 Бразильский реал (BRL)",
            "eth_title": "₿ Фьючерсы Ethereum (ETH)",
            "asian_session": "Азиатская сессия",
            "americas_session": "Американская сессия",
            "crypto_247": "Криптовалюты 24/7",
            "emerging_market": "Развивающийся рынок",
            "high_volatility": "Высокая волатильность",
            "low_volatility": "Низкая волатильность",
            "extreme_volatility": "Экстремальная волатильность",
            "processing_asian": "Обработка данных азиатского рынка...",
            "analyzing_cny": "Анализ сигналов USD/CNY",
            "market_info": "Информация о рынке",
            "cny_unavailable": "СИГНАЛ CNY НЕДОСТУПЕН",
            "try_again": "Попробуйте еще раз через несколько минут",
            "cny_error": "Ошибка сигнала CNY"
        }
    },
    "it": {
        "welcome": {
            "title": "🌟 Benvenuto in UR Trading Expert Bot!",
            "description": "Il tuo compagno di trading basato sull'IA con segnali professionali",
            "get_started": "Inizia",
            "features": "Caratteristiche",
            "pricing": "Prezzi"
        },
        "commands": {
            "help": "Aiuto e Comandi",
            "signals": "Segnali di Trading",
            "analytics": "Analisi",
            "education": "Educazione",
            "notifications": "Notifiche",
            "account": "Il Mio Account",
            "settings": "Impostazioni"
        },
        "signals": {
            "direction_buy": "📈 ACQUISTA",
            "direction_sell": "📉 VENDI",
            "direction_hold": "⏸️ Tieni",
            "confidence": "Fiducia",
            "entry_price": "Prezzo di Entrata",
            "stop_loss": "Stop Loss",
            "take_profit": "Take Profit",
            "risk_reward": "Rapporto Rischio/Rendimento",
            "analysis": "Analisi",
            "generated_at": "Generato",
            "signal_quality": "Qualità del Segnale",
            "trading_hours": "Ore di Trading"
        },
        "markets": {
            "forex": "Forex",
            "crypto": "Criptovalute",
            "commodities": "Materie Prime",
            "futures": "Futures",
            "international": "Mercati Internazionali"
        },
        "subscription": {
            "free_tier": "Gratuito",
            "premium_tier": "Premium",
            "vip_tier": "VIP",
            "upgrade_required": "Aggiornamento Richiesto",
            "upgrade_now": "Aggiorna Ora",
            "billing": "Fatturazione e Abbonamento",
            "upgrade_options": "Opzioni di Aggiornamento",
            "full_international": "Accesso internazionale completo",
            "limited_international": "Accesso internazionale limitato",
            "use_subscribe": "Usa /subscribe per aggiornare!"
        },
        "errors": {
            "general_error": "Si è verificato un errore. Riprova.",
            "permission_denied": "Non hai i permessi per utilizzare questa funzione.",
            "rate_limit": "Troppe richieste. Attendi e riprova.",
            "service_unavailable": "Servizio temporaneamente non disponibile.",
            "invalid_command": "Comando non valido. Usa /help per vedere i comandi disponibili."
        },
        "time": {
            "just_now": "Ora",
            "minutes_ago": "{} minuti fa",
            "hours_ago": "{} ore fa",
            "days_ago": "{} giorni fa",
            "yesterday": "Ieri",
            "today": "Oggi",
            "tomorrow": "Domani"
        },
        "numbers": {
            "decimal_separator": ",",
            "thousands_separator": ".",
            "currency_format": "${:,.2f}",
            "percentage_format": "{:.1f}%"
        },
        "trading": {
            "long_position": "Posizione Lunga",
            "short_position": "Posizione Corta",
            "leverage": "Leva",
            "margin": "Margine",
            "pnl": "Profitto/Perdita",
            "profit": "Profitto",
            "loss": "Perdita",
            "break_even": "Pareggio",
            "trend": "Tendenza",
            "support": "Supporto",
            "resistance": "Resistenza",
            "spread": "Spread"
        },
        "international": {
            "cny_title": "🇨🇳 Mercato Cinese (CNY)",
            "brl_title": "🇧🇷 Real Brasiliano (BRL)",
            "eth_title": "₿ Futures Ethereum (ETH)",
            "asian_session": "Sessione Asiatica",
            "americas_session": "Sessione Americana",
            "crypto_247": "Cripto 24/7",
            "emerging_market": "Mercato Emergente",
            "high_volatility": "Alta Volatilità",
            "low_volatility": "Bassa Volatilità",
            "extreme_volatility": "Volatilità Estrema",
            "processing_asian": "Elaborazione dati mercato asiatico...",
            "analyzing_cny": "Analisi segnali USD/CNY",
            "market_info": "Informazioni di Mercato",
            "cny_unavailable": "SEGNALE CNY NON DISPONIBILE",
            "try_again": "Riprova tra qualche minuto",
            "cny_error": "Errore segnale CNY"
        }
    },
    "de": {
        "welcome": {
            "title": "🌟 Willkommen bei UR Trading Expert Bot!",
            "description": "Ihr KI-gestützter Trading-Begleiter mit professionellen Signalen",
            "get_started": "Loslegen",
            "features": "Funktionen",
            "pricing": "Preise"
        },
        "commands": {
            "help": "Hilfe und Befehle",
            "signals": "Trading-Signale",
            "analytics": "Analysen",
            "education": "Bildung",
            "notifications": "Benachrichtigungen",
            "account": "Mein Konto",
            "settings": "Einstellungen"
        },
        "signals": {
            "direction_buy": "📈 KAUFEN",
            "direction_sell": "📉 VERKAUFEN",
            "direction_hold": "⏸️ HALTEN",
            "confidence": "Konfidenz",
            "entry_price": "Einstiegspreis",
            "stop_loss": "Stop-Loss",
            "take_profit": "Take-Profit",
            "risk_reward": "Risiko/Rendite-Verhältnis",
            "analysis": "Analyse",
            "generated_at": "Erstellt",
            "signal_quality": "Signalqualität",
            "trading_hours": "Handelszeiten"
        },
        "markets": {
            "forex": "Forex",
            "crypto": "Kryptowährungen",
            "commodities": "Rohstoffe",
            "futures": "Futures",
            "international": "Internationale Märkte"
        },
        "subscription": {
            "free_tier": "Kostenlos",
            "premium_tier": "Premium",
            "vip_tier": "VIP",
            "upgrade_required": "Upgrade erforderlich",
            "upgrade_now": "Jetzt upgraden",
            "billing": "Abrechnung und Abonnement",
            "upgrade_options": "Upgrade-Optionen",
            "full_international": "Voller internationaler Zugang",
            "limited_international": "Eingeschränkter internationaler Zugang",
            "use_subscribe": "Verwenden Sie /subscribe zum Upgrade!"
        },
        "errors": {
            "general_error": "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
            "permission_denied": "Sie haben keine Berechtigung, diese Funktion zu verwenden.",
            "rate_limit": "Zu viele Anfragen. Warten Sie und versuchen Sie es erneut.",
            "service_unavailable": "Dienst vorübergehend nicht verfügbar.",
            "invalid_command": "Ungültiger Befehl. Verwenden Sie /help, um verfügbare Befehle zu sehen."
        },
        "time": {
            "just_now": "Gerade eben",
            "minutes_ago": "Vor {} Minuten",
            "hours_ago": "Vor {} Stunden",
            "days_ago": "Vor {} Tagen",
            "yesterday": "Gestern",
            "today": "Heute",
            "tomorrow": "Morgen"
        },
        "numbers": {
            "decimal_separator": ",",
            "thousands_separator": ".",
            "currency_format": "${:,.2f}",
            "percentage_format": "{:.1f}%"
        },
        "trading": {
            "long_position": "Long-Position",
            "short_position": "Short-Position",
            "leverage": "Hebel",
            "margin": "Margin",
            "pnl": "Gewinn/Verlust",
            "profit": "Gewinn",
            "loss": "Verlust",
            "break_even": "Break-Even",
            "trend": "Trend",
            "support": "Support",
            "resistance": "Resistance",
            "spread": "Spread"
        },
        "international": {
            "cny_title": "🇨🇳 Chinesischer Markt (CNY)",
            "brl_title": "🇧🇷 Brasilianischer Real (BRL)",
            "eth_title": "₿ Ethereum Futures (ETH)",
            "asian_session": "Asiatische Session",
            "americas_session": "Amerikanische Session",
            "crypto_247": "Krypto 24/7",
            "emerging_market": "Schwellenmarkt",
            "high_volatility": "Hohe Volatilität",
            "low_volatility": "Niedrige Volatilität",
            "extreme_volatility": "Extreme Volatilität",
            "processing_asian": "Verarbeitung asiatischer Marktdaten...",
            "analyzing_cny": "Analyse USD/CNY Signale",
            "market_info": "Marktinformationen",
            "cny_unavailable": "CNY SIGNAL NICHT VERFÜGBAR",
            "try_again": "Versuchen Sie es in ein paar Minuten erneut",
            "cny_error": "CNY Signal Fehler"
        }
    },
    "ja": {
        "welcome": {
            "title": "🌟 UR Trading Expert Botへようこそ!",
            "description": "プロフェッショナルなシグナルを提供するAI搭載のトレーディングコンパニオン",
            "get_started": "始める",
            "features": "機能",
            "pricing": "料金"
        },
        "commands": {
            "help": "ヘルプとコマンド",
            "signals": "トレーディングシグナル",
            "analytics": "分析",
            "education": "教育",
            "notifications": "通知",
            "account": "マイアカウント",
            "settings": "設定"
        },
        "signals": {
            "direction_buy": "📈 買い",
            "direction_sell": "📉 売り",
            "direction_hold": "⏸️ ホールド",
            "confidence": "信頼度",
            "entry_price": "エントリー価格",
            "stop_loss": "ストップロス",
            "take_profit": "テイクプロフィット",
            "risk_reward": "リスク/リワード比率",
            "analysis": "分析",
            "generated_at": "生成日時",
            "signal_quality": "シグナル品質",
            "trading_hours": "取引時間"
        },
        "markets": {
            "forex": "外国為替",
            "crypto": "暗号通貨",
            "commodities": "商品",
            "futures": "先物",
            "international": "国際市場"
        },
        "subscription": {
            "free_tier": "無料",
            "premium_tier": "プレミアム",
            "vip_tier": "VIP",
            "upgrade_required": "アップグレードが必要です",
            "upgrade_now": "今すぐアップグレード",
            "billing": "請求とサブスクリプション",
            "upgrade_options": "アップグレードオプション",
            "full_international": "完全な国際アクセス",
            "limited_international": "制限された国際アクセス",
            "use_subscribe": "/subscribeを使用してアップグレードしてください！"
        },
        "errors": {
            "general_error": "エラーが発生しました。もう一度お試しください。",
            "permission_denied": "この機能を使用する権限がありません。",
            "rate_limit": "リクエストが多すぎます。待ってからもう一度お試しください。",
            "service_unavailable": "サービスが一時的に利用できません。",
            "invalid_command": "無効なコマンドです。/helpを使用して利用可能なコマンドを確認してください。"
        },
        "time": {
            "just_now": "たった今",
            "minutes_ago": "{}分前",
            "hours_ago": "{}時間前",
            "days_ago": "{}日前",
            "yesterday": "昨日",
            "today": "今日",
            "tomorrow": "明日"
        },
        "numbers": {
            "decimal_separator": ".",
            "thousands_separator": ",",
            "currency_format": "${:,.2f}",
            "percentage_format": "{:.1f}%"
        },
        "trading": {
            "long_position": "ロングポジション",
            "short_position": "ショートポジション",
            "leverage": "レバレッジ",
            "margin": "マージン",
            "pnl": "損益",
            "profit": "利益",
            "loss": "損失",
            "break_even": "損益分岐点",
            "trend": "トレンド",
            "support": "サポート",
            "resistance": "レジスタンス",
            "spread": "スプレッド"
        },
        "international": {
            "cny_title": "🇨🇳 中国市場 (CNY)",
            "brl_title": "🇧🇷 ブラジルレアル (BRL)",
            "eth_title": "₿ Ethereum先物 (ETH)",
            "asian_session": "アジアセッション",
            "americas_session": "アメリカセッション",
            "crypto_247": "暗号通貨24/7",
            "emerging_market": "新興市場",
            "high_volatility": "高ボラティリティ",
            "low_volatility": "低ボラティリティ",
            "extreme_volatility": "極端なボラティリティ",
            "processing_asian": "アジア市場データの処理中...",
            "analyzing_cny": "USD/CNYシグナルの分析",
            "market_info": "市場情報",
            "cny_unavailable": "CNYシグナルが利用できません",
            "try_again": "数分後にもう一度お試しください",
            "cny_error": "CNYシグナルエラー"
        }
    },
    "fr": {
        "welcome": {
            "title": "🌟 Bienvenue sur UR Trading Expert Bot!",
            "description": "Votre compagnon de trading alimenté par l'IA avec des signaux professionnels",
            "get_started": "Commencer",
            "features": "Fonctionnalités",
            "pricing": "Tarifs"
        },
        "commands": {
            "help": "Aide et Commandes",
            "signals": "Signaux de Trading",
            "analytics": "Analyses",
            "education": "Éducation",
            "notifications": "Notifications",
            "account": "Mon Compte",
            "settings": "Paramètres"
        },
        "signals": {
            "direction_buy": "📈 ACHETER",
            "direction_sell": "📉 VENDRE",
            "direction_hold": "⏸️ TENIR",
            "confidence": "Confiance",
            "entry_price": "Prix d'Entrée",
            "stop_loss": "Stop Loss",
            "take_profit": "Take Profit",
            "risk_reward": "Ratio Risque/Récompense",
            "analysis": "Analyse",
            "generated_at": "Généré",
            "signal_quality": "Qualité du Signal",
            "trading_hours": "Heures de Trading"
        },
        "markets": {
            "forex": "Forex",
            "crypto": "Cryptomonnaies",
            "commodities": "Matières Premières",
            "futures": "Contrats à Terme",
            "international": "Marchés Internationaux"
        },
        "subscription": {
            "free_tier": "Gratuit",
            "premium_tier": "Premium",
            "vip_tier": "VIP",
            "upgrade_required": "Mise à niveau requise",
            "upgrade_now": "Mettre à niveau maintenant",
            "billing": "Facturation et Abonnement",
            "upgrade_options": "Options de mise à niveau",
            "full_international": "Accès international complet",
            "limited_international": "Accès international limité",
            "use_subscribe": "Utilisez /subscribe pour mettre à niveau!"
        },
        "errors": {
            "general_error": "Une erreur s'est produite. Veuillez réessayer.",
            "permission_denied": "Vous n'avez pas la permission d'utiliser cette fonction.",
            "rate_limit": "Trop de demandes. Veuillez patienter et réessayer.",
            "service_unavailable": "Service temporairement indisponible.",
            "invalid_command": "Commande invalide. Utilisez /help pour voir les commandes disponibles."
        },
        "time": {
            "just_now": "À l'instant",
            "minutes_ago": "Il y a {} minutes",
            "hours_ago": "Il y a {} heures",
            "days_ago": "Il y a {} jours",
            "yesterday": "Hier",
            "today": "Aujourd'hui",
            "tomorrow": "Demain"
        },
        "numbers": {
            "decimal_separator": ",",
            "thousands_separator": " ",
            "currency_format": "${:,.2f}",
            "percentage_format": "{:.1f}%"
        },
        "trading": {
            "long_position": "Position Longue",
            "short_position": "Position Courte",
            "leverage": "Levier",
            "margin": "Marge",
            "pnl": "Profit/Perte",
            "profit": "Profit",
            "loss": "Perte",
            "break_even": "Seuil de Rentabilité",
            "trend": "Tendance",
            "support": "Support",
            "resistance": "Résistance",
            "spread": "Spread"
        },
        "international": {
            "cny_title": "🇨🇳 Marché Chinois (CNY)",
            "brl_title": "🇧🇷 Réal Brésilien (BRL)",
            "eth_title": "₿ Futures Ethereum (ETH)",
            "asian_session": "Session Asiatique",
            "americas_session": "Session Américaine",
            "crypto_247": "Crypto 24/7",
            "emerging_market": "Marché Émergent",
            "high_volatility": "Haute Volatilité",
            "low_volatility": "Basse Volatilité",
            "extreme_volatility": "Volatilité Extrême",
            "processing_asian": "Traitement des données du marché asiatique...",
            "analyzing_cny": "Analyse des signaux USD/CNY",
            "market_info": "Informations sur le Marché",
            "cny_unavailable": "SIGNAL CNY NON DISPONIBLE",
            "try_again": "Réessayez dans quelques minutes",
            "cny_error": "Erreur du signal CNY"
        }
    },
    "hi": {
        "welcome": {
            "title": "🌟 UR Trading Expert Bot में आपका स्वागत है!",
            "description": "पेशेवर सिग्नल के साथ आपका AI-संचालित ट्रेडिंग साथी",
            "get_started": "शुरू करें",
            "features": "सुविधाएं",
            "pricing": "मूल्य निर्धारण"
        },
        "commands": {
            "help": "सहायता और कमांड",
            "signals": "ट्रेडिंग सिग्नल",
            "analytics": "विश्लेषण",
            "education": "शिक्षा",
            "notifications": "सूचनाएं",
            "account": "मेरा खाता",
            "settings": "सेटिंग्स"
        },
        "signals": {
            "direction_buy": "📈 खरीदें",
            "direction_sell": "📉 बेचें",
            "direction_hold": "⏸️ होल्ड करें",
            "confidence": "विश्वास",
            "entry_price": "प्रवेश मूल्य",
            "stop_loss": "स्टॉप लॉस",
            "take_profit": "टेक प्रॉफिट",
            "risk_reward": "जोखिम/इनाम अनुपात",
            "analysis": "विश्लेषण",
            "generated_at": "जनरेट किया गया",
            "signal_quality": "सिग्नल गुणवत्ता",
            "trading_hours": "ट्रेडिंग घंटे"
        },
        "markets": {
            "forex": "फॉरेक्स",
            "crypto": "क्रिप्टोकरेंसी",
            "commodities": "कमोडिटीज",
            "futures": "फ्यूचर्स",
            "international": "अंतरराष्ट्रीय बाजार"
        },
        "subscription": {
            "free_tier": "मुफ्त",
            "premium_tier": "प्रीमियम",
            "vip_tier": "VIP",
            "upgrade_required": "अपग्रेड आवश्यक",
            "upgrade_now": "अभी अपग्रेड करें",
            "billing": "बिलिंग और सब्सक्रिप्शन",
            "upgrade_options": "अपग्रेड विकल्प",
            "full_international": "पूर्ण अंतरराष्ट्रीय पहुंच",
            "limited_international": "सीमित अंतरराष्ट्रीय पहुंच",
            "use_subscribe": "अपग्रेड करने के लिए /subscribe का उपयोग करें!"
        },
        "errors": {
            "general_error": "एक त्रुटि हुई। कृपया पुनः प्रयास करें।",
            "permission_denied": "आपके पास इस फंक्शन का उपयोग करने की अनुमति नहीं है।",
            "rate_limit": "बहुत अधिक अनुरोध। प्रतीक्षा करें और पुनः प्रयास करें।",
            "service_unavailable": "सेवा अस्थायी रूप से अनुपलब्ध है।",
            "invalid_command": "अमान्य कमांड। उपलब्ध कमांड देखने के लिए /help का उपयोग करें।"
        },
        "time": {
            "just_now": "अभी",
            "minutes_ago": "{} मिनट पहले",
            "hours_ago": "{} घंटे पहले",
            "days_ago": "{} दिन पहले",
            "yesterday": "कल",
            "today": "आज",
            "tomorrow": "कल"
        },
        "numbers": {
            "decimal_separator": ".",
            "thousands_separator": ",",
            "currency_format": "${:,.2f}",
            "percentage_format": "{:.1f}%"
        },
        "trading": {
            "long_position": "लॉन्ग पोजीशन",
            "short_position": "शॉर्ट पोजीशन",
            "leverage": "लिवरेज",
            "margin": "मार्जिन",
            "pnl": "लाभ/हानि",
            "profit": "लाभ",
            "loss": "हानि",
            "break_even": "ब्रेक ईवन",
            "trend": "ट्रेंड",
            "support": "सपोर्ट",
            "resistance": "रेजिस्टेंस",
            "spread": "स्प्रेड"
        },
        "international": {
            "cny_title": "🇨🇳 चीनी बाजार (CNY)",
            "brl_title": "🇧🇷 ब्राजीलियाई रियल (BRL)",
            "eth_title": "₿ Ethereum फ्यूचर्स (ETH)",
            "asian_session": "एशियाई सत्र",
            "americas_session": "अमेरिकी सत्र",
            "crypto_247": "क्रिप्टो 24/7",
            "emerging_market": "उभरता बाजार",
            "high_volatility": "उच्च अस्थिरता",
            "low_volatility": "निम्न अस्थिरता",
            "extreme_volatility": "अत्यधिक अस्थिरता",
            "processing_asian": "एशियाई बाजार डेटा प्रोसेस हो रहा है...",
            "analyzing_cny": "USD/CNY सिग्नल विश्लेषण",
            "market_info": "बाजार जानकारी",
            "cny_unavailable": "CNY सिग्नल उपलब्ध नहीं",
            "try_again": "कुछ मिनटों में पुनः प्रयास करें",
            "cny_error": "CNY सिग्नल त्रुटि"
        }
    }
}

def main():
    languages_dir = Path("languages")

    for lang_code, translations in TRANSLATIONS.items():
        lang_file = languages_dir / f"{lang_code}.json"

        # Load existing file or create new one
        if lang_file.exists():
            with open(lang_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        # Merge translations
        def merge_dict(target, source):
            for key, value in source.items():
                if isinstance(value, dict):
                    if key not in target or not isinstance(target[key], dict):
                        target[key] = {}
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        merge_dict(existing_data, translations)

        # Save updated file
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        print(f"Completed translations for {lang_code}")

    print("All translations completed!")

if __name__ == "__main__":
    main()
