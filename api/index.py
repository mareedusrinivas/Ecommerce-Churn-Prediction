from app import app

# Vercel needs the 'app' variable at the module level
# This enables the serverless function to find your Flask entry point
application = app
