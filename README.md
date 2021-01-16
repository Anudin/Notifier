# What's this?
This is a Telegram bot 🤖 which notifies you when you sell in app purchases or get reviews via Google Play.

# How?
The functionality can be provided by one bot or split between multiple, it doesn't really matter. I'll speak of one bot for simplicity reasons.  
The code assumes a "serverless" environment, the bot only reacts to events and persistence is handled by a database. More specificly, it is written for the GCP.  
The bot is triggered by messages on Pub/Sub topics. IAP notifications are provided via Googles "Real-time developer notifications", which publish to a Pub/Sub topic.
New reviews are polled with the Android Publisher API, the polling is triggered by Pub/Sub messages published by Cloud Scheduler. At this point we're already knee deep
in Google products, so Firestore was choosen for persistence.

# Cool, how do I get this working?
Maybe I'll write a guide one day, until then you'll have to figure it out by yourself, sorry.
