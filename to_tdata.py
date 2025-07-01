from asyncio import sleep, create_task, new_event_loop, current_task, get_event_loop
from datetime import datetime
from json import loads
from os import path, walk, makedirs
from random import choice
import shutil
from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, UseCurrentSession, CreateNewSession
from telethon.errors.common import AuthKeyNotFound
from python_socks import ProxyType
    

class MyTelegramClient(TelegramClient):
    def __init__(self, *args, session_file = None, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, _exc_type, _exc_val, _exc_tb, **kwargs):  
        if self.is_connected():
            print("Отключаюсь")
        
        await self.disconnect()
    
        while not self.disconnected:
            await sleep(1)
    
    async def tl_connection(self, timeout): 
        async def connect(self):
            try:
                await self.connect()
                
            except AuthKeyNotFound:
                current_task(loop = self.loop).cancel()
        
        task = create_task(connect(self))
                
        start_date = datetime.now()
        while (datetime.now() - start_date).total_seconds() < timeout and not task.done() and not task.cancelled():
            await sleep(1)
        
        if not task.done() and not task.cancelled():
            task.cancel()
        
        while not task.done() and not task.cancelled():
            await sleep(0.5)
        
        return not task.cancelled()
    
async def start(session_file, json_data, proxy, flag):
    try:
        
        async with MyTelegramClient(
                    session_file[1],
                    json_data['app_id'],
                    json_data['app_hash'],
                    device_model = json_data['device'],
                    system_version = json_data['sdk'],
                    app_version = json_data['app_version'],
                    lang_code = json_data['lang_code'],
                    system_lang_code = json_data['system_lang_code'],
                    timeout = 19,
                    retry_delay = 3,
                    connection_retries = 2,
                    use_ipv6 = True if proxy is not None and proxy['ipv6'] == 'ipv6' else False,
                    proxy = None if proxy is None else 
                        {
                        'proxy_type': ProxyType.SOCKS5 if proxy['type'] == 'socks5' else ProxyType.HTTP,
                        'addr': proxy['addr'],
                        'port': proxy['port'],
                        'username': proxy['username'],
                        'password': proxy['password'],
                        'rdns': True
                        },
                    session_file = session_file,
                    
                    ) as client:
            try:
                print(f"[{session_file[0]}] Пробую подключиться")
                
                if not await client.tl_connection(15):
                    print(f"[{session_file[0]}] Нет связи с телеграм")
                    
                elif await client.is_user_authorized():
                    print(f"[{session_file[0]}] Подключился успешно")
                    
                    output_dir = path.dirname(session_file[1])

                    session_name, _ext = path.splitext(path.basename(session_file[1]))
                    
                    tdata_folder = path.join(output_dir, session_name, 'tdata')
                    
                    tdesk = await client.ToTDesktop(flag = flag)
        
                    makedirs(tdata_folder, exist_ok = True)
        
                    tdesk.SaveTData(tdata_folder)
                    
                    print(f"[{session_file[0]}] Tdata успешно создана. Путь: {tdata_folder}")
                     
                else:
                    print(f"[{session_file[0]}] Сессия не активна или забанена")
                    
            except Exception as ex:
                print(f"({ex.__class__.__name__}) {ex}")
                
    except Exception as ex:
        print(f"({ex.__class__.__name__}) {ex}")
        
def find_all_session_files():
    script_dir = path.dirname(path.abspath(__file__))
    session_files = []

    for root, _dirs, files in walk(script_dir):
        for file in files:
            if file.endswith(".session"):
                full_path = path.join(root, file)
                session_files.append([file, full_path])

    return session_files

def get_proxy_list():
    proxy_list = []
    if path.isfile("proxy.txt"):
        with open("proxy.txt", "r") as file:
            for line in file:
                if '#' in line:
                    continue
                
                proxy = line.strip().split(':')
                proxy = {'addr': proxy[0], 'port': int(proxy[1]), 'username': proxy[2], 'password': proxy[3], "type": proxy[4],  "ipv6": proxy[5], }
                proxy_list.append(proxy)
    
    else:
        with open("proxy.txt", "w") as file:
            file.write("#ПРИМЕР КАК НАДО ЗАПИСЫВАТЬ ПРОКСИ, С НОВОЙ СТРОКИ:\n#ip_адрес:порт:логин:пароль:тип_socks5_или_http:ipv6_или_ipv4 Пример: 164.33.200.248:8000:Yhydf:tNMeJe:socks5:ipv4")
    
    print(f"Загружено {len(proxy_list)} прокси")
    return proxy_list

if __name__ == '__main__':
    try:
        proxy_list = get_proxy_list()
        session_files = find_all_session_files()
        
        if len(proxy_list) <= 0:
            print("!!!!  ПОДКЛЮЧЕНИЯ БУДУТ ПРОИЗВОДИТЬСЯ С ВАШЕГО РЕЛЬНОГО IP !!!")
            
        if len(session_files) <= 0:
            print("Сессий не найдено")
        
        else:
            print(f"Найдено {len(session_files)} сессий")
            
            while True:
                print("Выберите сессию:")
                try:
                    for i in range(len(session_files)):
                        print(f"{i+1} - {session_files[i][0]} ({session_files[i][1]})")
                        
                    session_file = session_files[int(input("Выберите сессию > ")) - 1]
                    json_file = session_file[1].replace(".session", ".json")
                    print(json_file)
                    if path.isfile(json_file):
                        with open(json_file, 'r') as file:
                            json_data = loads(file.read())
                            
                        print(f"Выбран файл сессии: {session_file[1]}")
                        
                        flag = None
                        while flag is None:
                            try:
                                print("Выберите тип работы:")
                                print("1 - Создать новую (еще одну на аккаунте) сессию")
                                print("2 - Создать на основе текущей от telethon (не реклмендуется)")
                                
                                cmd = int(input('> '))
                                
                                if cmd == 1:
                                    flag = CreateNewSession
                                
                                elif cmd == 2:
                                    flag = UseCurrentSession
                                    
                            except Exception:
                                pass
                        
                        input("Для начала работы нажмите Enter")
                        new_event_loop().run_until_complete(start(session_file, json_data, choice(proxy_list) if len(proxy_list) > 0 else None, flag))
                        
                    else:
                        print(f"Файл .json от сессии {session_file[0]} не найден")
                         
                    input("Что бы начать с начала Enter")
                    
                except Exception:
                    pass
                    
            
    except Exception as ex:
        print(f"({ex.__class__.__name__}) {ex}")
        
input("Скрипт завершён")
