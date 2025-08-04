'''
client_id = 'kit4ihbrmhemwh9aeldz8wqeifyena'
client_secret = '3l5e1u3gwa963ni9z2r386kznupmr6'
'''
import socket
import requests
import os

# Настройки
HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = "fyltrix23"  # Ваше имя пользователя Twitch
TOKEN = "oauth:0m7lrh3axdosysc3i9bj6amjo2ipng"  # Ваш OAuth токен. Получить можно здесь: https://twitchapps.com/tmi/
CHANNEL = "#vedal987"  ##Philza Канал, к которому вы хотите подключиться (всегда в нижнем регистре)
OUTPUT_FILE = "vedal987_chat_logm10.txt"

# Получение OAuth токена
def get_oauth_token(client_id, client_secret):
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']

# Подключение к Twitch IRC
def connect_to_twitch():
    sock = socket.socket()
    sock.connect((HOST, PORT))
    sock.send(f"PASS {TOKEN}\n".encode('utf-8'))
    sock.send(f"NICK {NICK}\n".encode('utf-8'))
    sock.send(f"JOIN {CHANNEL}\n".encode('utf-8'))
    return sock

# Запись сообщений в файл
def log_chat(sock):
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as file:
        while True:
            response = sock.recv(2048).decode('utf-8')

            if response.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))

            elif len(response) > 0:
                parts = response.split('PRIVMSG')
                if len(parts) > 1:
                    user = parts[0].split('!')[0][1:]
                    message = parts[1].split(':')[1]
                    log_line = f"{user}: {message}\n"
                    print(log_line)
                    file.write(log_line)
                    file.flush()

# Основная функция
def main():
    # Убедитесь, что OAuth токен действителен
    if TOKEN.startswith('oauth:'):
        try:
            sock = connect_to_twitch()
            log_chat(sock)
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Invalid OAuth token. Please check your token.")

if __name__ == "__main__":
    main()
