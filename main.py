import discord
import asyncio
import random
import time

TOKEN = "MTU1MDU2MDEyMzIwNDgwMDY1Mg.GEfiUA.uAPsj0ZsM-ICUQxwn4oHiyh1JI30LYVwlxUku8"

class SpammerBot(discord.Bot):
    def __init__(self):
        super().__init__()
        
    @discord.slash_command(name="spam", description="Rozpocznij spamowanie DM")
    async def spam(self, ctx, 
                   token: discord.Option(str, "Token konta do spamowania"),
                   wiadomosc: discord.Option(str, "Wiadomość do wysłania"),
                   delay: discord.Option(int, "Opóźnienie w sekundach", required=False, default=4)):
        
        # Wysyłamy początkową wiadomość na kanał (widoczna dla wszystkich)
        status_msg = await ctx.send(f"🚀 **Uruchamianie spamowania...**\nToken: ||{token[:10]}...||\nPrzygotowanie...")
        
        # Uruchamiamy w tle (nie blokuje)
        asyncio.create_task(self.spam_task(ctx, status_msg, token, wiadomosc, delay))
    
    async def spam_task(self, ctx, status_msg, token, message, delay):
        """Główna logika spamowania z live updatem"""
        temp_client = discord.Client()
        
        @temp_client.event
        async def on_ready():
            sent = 0
            errors = 0
            skipped_bots = 0
            last_update = time.time()
            start_time = time.time()
            
            await status_msg.edit(content=f"🟢 **Spamowanie w trakcie...**\nZalogowano jako: `{temp_client.user.name}`\nWysłano: **0** | Błędy: 0")
            
            for channel in temp_client.private_channels:
                try:
                    # DM 1 na 1
                    if isinstance(channel, discord.DMChannel):
                        user = channel.recipient
                        if user and user.bot:
                            skipped_bots += 1
                            continue
                        
                        await channel.send(message)
                        sent += 1
                        
                    # Grupowe DM
                    elif isinstance(channel, discord.GroupChannel):
                        await channel.send(message)
                        sent += 1
                    
                    # Aktualizacja statusu co 3 sekundy lub co 5 wiadomości
                    current_time = time.time()
                    if current_time - last_update > 3 or sent % 5 == 0:
                        elapsed = int(current_time - start_time)
                        await status_msg.edit(
                            content=f"🟡 **Spamowanie w trakcie...**\n"
                            f"Konto: `{temp_client.user.name}`\n"
                            f"Wysłano: **{sent}** | Pominięto botów: {skipped_bots} | Błędy: {errors}\n"
                            f"Czas: {elapsed}s"
                        )
                        last_update = current_time
                    
                    # Opóźnienie z random
                    await asyncio.sleep(random.uniform(delay, delay + 2))
                    
                except discord.HTTPException as e:
                    if e.status == 429:
                        retry = getattr(e, 'retry_after', 60)
                        await status_msg.edit(
                            content=f"🟠 **Rate Limit!**\nCzekam {retry:.0f}s...\nWysłano dotąd: {sent}"
                        )
                        await asyncio.sleep(retry)
                    else:
                        errors += 1
                except Exception as e:
                    errors += 1
            
            # Finalna aktualizacja
            total_time = int(time.time() - start_time)
            await status_msg.edit(
                content=f"✅ **Zakończono!**\n"
                f"Konto: `{temp_client.user.name}`\n"
                f"Wysłano: **{sent}** wiadomości\n"
                f"Pominięto botów: {skipped_bots}\n"
                f"Błędy: {errors}\n"
                f"Czas: {total_time}s"
            )
            
            await temp_client.close()
        
        try:
            await temp_client.start(token, bot=False)
        except Exception as e:
            await status_msg.edit(content=f"❌ **Błąd logowania:** {str(e)}")

# Uruchomienie
if __name__ == "__main__":
    if TOKEN == "TU_WKLEJ_TOKEN_GŁÓWNEGO_BOTA":
        print("Wpisz token głównego bota w zmiennej TOKEN na górze pliku!")
    else:
        print("Bot startuje...")
        bot = SpammerBot()
        bot.run(TOKEN)
