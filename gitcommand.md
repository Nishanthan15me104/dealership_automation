git init
git config core.fileMode false
git config core.autocrlf true

Create .gitignore: Add venv/, __pycache__/, .env, and *.log.

Create .gitattributes: Add the line * text=auto.

git add .
git commit -m "Initial commit: Trading bot base with cross-platform config"

git branch -M main
git remote add origin https://github.com/Nishanthan15me104/trading_bot.git
git push -u origin main

