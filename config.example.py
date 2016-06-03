# Development Settings
DEBUG = False
HOST = "127.0.0.1"
PORT = "5000"

# Application Settings
SECRET_KEY = "changeme"
SESSION_TYPE = "redis"

RECAPTCHA_PUBLIC_KEY = 'reCAPTHCASiteKey'
RECAPTCHA_PRIVATE_KEY = 'reCAPTCHASecretKey'

REDDIT_CLIENT_ID = "RedditID"
REDDIT_CLIENT_SECRET = "RedditSecret"
REDDIT_REDIRECT_URI = "http://example.com/reddit/callback"

REDDIT_BOT_CLIENT_ID = "RedditID"
REDDIT_BOT_CLIENT_SECRET = "RedditSecret"
REDDIT_BOT_USERNAME = "BromBot"
REDDIT_BOT_PASSWORD = "RedditPassword"
REDDIT_SUBREDDIT = "brom"
REDDIT_CSS_MARKER = "/* End BromFlair */"

SCHEMATICS_PATH = "/home/minecraft/planning/plugins/WorldEdit/schematics/"