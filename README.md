# Weather bot
Telegram bot that shows the weather for the entered city using Django service and Yandex API

## Build
1. Create a virtual environment:
```commandline
python -m venv ./venv
```
and activate it. For example on Windows OS: 
```
.\venv\Scripts\Activate.ps1
```
2. Install requirements
```commandline 
pip install -r requirements.txt
```
3. Create .env file with contents shown in .env.example

4. Go into weather_forecast and apply django migrations:
```commandline
python .\manage.py migrate
```

## Run services
1. Launch telegram bot microservice:
```commandline
python .\weather_bot\tgbot\bot.py
```
2. Launch django service from weather_forecast folder:
```commandline
python .\manage.py runserver
```

## Usage
Go into your bot and start conversation by:
```
/start
```
