import discord
from discord.ext import commands
import aiohttp
import re
import time
import datetime

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rates = {}
        self.last_updated = 0
        self.cache_duration = 3600  # 1 hour cache
        # Regex
        # (?i) flag is handled by re.IGNORECASE
        self.pattern = re.compile(r"(\d+(?:\.\d+)?)\s*([a-z]{3})\s*(?:to|in)\s*([a-z]{3})", re.IGNORECASE)

        # Dictionary of currency codes to full names
        self.currency_names = {
            "USD": "United States Dollar", "EUR": "Euro", "GBP": "British Pound Sterling",
            "INR": "Indian Rupee", "AUD": "Australian Dollar", "CAD": "Canadian Dollar",
            "SGD": "Singapore Dollar", "CHF": "Swiss Franc", "MYR": "Malaysian Ringgit",
            "JPY": "Japanese Yen", "CNY": "Chinese Yuan Renminbi", "NZD": "New Zealand Dollar",
            "THB": "Thai Baht", "HUF": "Hungarian Forint", "AED": "United Arab Emirates Dirham",
            "HKD": "Hong Kong Dollar", "MXN": "Mexican Peso", "ZAR": "South African Rand",
            "PHP": "Philippine Peso", "SEK": "Swedish Krona", "IDR": "Indonesian Rupiah",
            "SAR": "Saudi Riyal", "BRL": "Brazilian Real", "TRY": "Turkish Lira",
            "KES": "Kenyan Shilling", "KRW": "South Korean Won", "EGP": "Egyptian Pound",
            "IQD": "Iraqi Dinar", "NOK": "Norwegian Krone", "KWD": "Kuwaiti Dinar",
            "RUB": "Russian Ruble", "DKK": "Danish Krone", "PKR": "Pakistani Rupee",
            "ILS": "Israeli New Shekel", "PLN": "Polish Zloty", "QAR": "Qatari Riyal",
            "XAU": "Gold Ounce", "XAG": "Silver Ounce", "COP": "Colombian Peso",
            "CLP": "Chilean Peso", "TWD": "New Taiwan Dollar", "ARS": "Argentine Peso",
            "CZK": "Czech Koruna", "VND": "Vietnamese Dong", "MAD": "Moroccan Dirham",
            "JOD": "Jordanian Dinar", "BHD": "Bahraini Dinar", "XOF": "CFA Franc BCEAO",
            "LKR": "Sri Lankan Rupee", "UAH": "Ukrainian Hryvnia", "NGN": "Nigerian Naira"
        }

    async def get_rates(self):
        current_time = time.time()
        if not self.rates or (current_time - self.last_updated) > self.cache_duration:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get("https://api.exchangerate-api.com/v4/latest/USD") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.rates = data.get("rates", {})
                            self.last_updated = current_time
                        else:
                            print(f"[ERROR] Failed to fetch currency rates: {resp.status}")
                except Exception as e:
                    print(f"[ERROR] Exception fetching currency rates: {e}")
        return self.rates

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check for matches
        match = self.pattern.search(message.content)
        if match:
            amount_str, from_curr, to_curr = match.groups()
            
            try:
                amount = float(amount_str)
                from_curr = from_curr.upper()
                to_curr = to_curr.upper()

                rates = await self.get_rates()
                
                if not rates:
                    return # Can't convert without rates

                if from_curr not in rates or to_curr not in rates:
                    # Silently ignore invalid currencies to avoid spamming
                    return

                # Convert to USD first (base), then to target
                # rate is "1 USD = x CURR"
                
                # Formula: amount_in_usd = amount / rate_from
                #          amount_in_target = amount_in_usd * rate_to
                
                rate_from = rates.get(from_curr)
                rate_to = rates.get(to_curr)
                
                if rate_from and rate_to:
                    converted_amount = (amount / rate_from) * rate_to
                    
                    # Get full names or fallback to code
                    from_name = self.currency_names.get(from_curr, from_curr)
                    to_name = self.currency_names.get(to_curr, to_curr)

                    # Format output
                    await message.reply(f"{amount:,.2f} {from_name} ≈ {converted_amount:,.2f} {to_name}")

            except Exception as e:
                print(f"[ERROR] Currency conversion error: {e}")

async def setup(bot):
    await bot.add_cog(Currency(bot))
