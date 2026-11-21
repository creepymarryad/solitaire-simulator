import sys
import os
import glob
import datetime
import pickle
import shutil
import logic

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# Avoid UnicodeEncodeError on consoles that can't display Polish characters
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

import pygame
import game_class
        
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "in")
OUTPUT_DIR = os.path.join(BASE_DIR, "out")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")
REPLAY_FILE = os.path.join(OUTPUT_DIR, "replay.pkl")
REPORT_FILE = os.path.join(OUTPUT_DIR, "raport.html")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

def ensure_dirs():
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

def run_auto_backup():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    current_backup_path = os.path.join(BACKUP_DIR, now_str)

    if os.path.exists(current_backup_path):
        print(f"[BACKUP] Folder {now_str} już istnieje. Pomijam archiwizację")
        return 

    try:
        print(f"[BACKUP] Archiwizowanie danych do: {current_backup_path} ...")
        shutil.copytree(INPUT_DIR, os.path.join(current_backup_path, "in"))
        shutil.copytree(OUTPUT_DIR, os.path.join(current_backup_path, "out"))
        print("[BACKUP] Gotowe")
    except Exception as e:
        print(f"[BACKUP] Błąd podczas kopiowania: {e}")

def save_individual_log(entry):
    base_name = os.path.splitext(entry['filename'])[0]
    log_path = os.path.join(LOGS_DIR, f"{base_name}_log.txt")
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"--- WYNIK DLA PLIKU: {entry['filename']} ---\n")
        f.write(f"Data symulacji: {now_str}\n")
        f.write(f"Status: {entry['status']}\n")
        f.write(f"Liczba ruchow: {entry['moves_count']}\n")
        if entry['error_msg']:
            f.write(f"Informacja: {entry['error_msg']}\n")
        f.write("-" * 30 + "\n")

def run_batch_simulation():
    ensure_dirs()
    if os.path.exists(REPLAY_FILE):
        try:
            os.remove(REPLAY_FILE)
        except:
            pass

    old_logs = glob.glob(os.path.join(LOGS_DIR, "*.txt"))
    for f in old_logs:
        try:
            os.remove(f)
        except:
            pass

    files = glob.glob(os.path.join(INPUT_DIR, "*.txt"))
    results = [] 
    all_winning_games = [] 

    print(f"Przetwarzanie {len(files)} plików...")

    for filepath in files:
        filename = os.path.basename(filepath)
        entry = {
            "filename": filename,
            "status": "UNKNOWN",
            "moves_count": 0,
            "error_msg": ""
        }

        try:
            deck = logic.load_deck_from_file(filepath)
            won, moves, initial_deck, layout, hand = logic.play_game(predefined_deck=deck)

            entry["moves_count"] = len(moves) 

            if won:
                entry["status"] = "SUKCES"
                all_winning_games.append({
                    "filename": filename,
                    "moves_count": len(moves),
                    "initial_deck": initial_deck,
                    "moves": moves
                })
            else:
                entry["status"] = "PORAŻKA"
                entry["error_msg"] = f"Niepoprawny układ po {len(moves)} ruchach"

        except ValueError as e:
            entry["status"] = "BŁĄD DANYCH"
            entry["error_msg"] = str(e)
        except Exception as e:
            entry["status"] = "BŁĄD KRYTYCZNY"
            entry["error_msg"] = str(e)

        results.append(entry)
        save_individual_log(entry)

    create_html_report(results)
    
    if all_winning_games:
        with open(REPLAY_FILE, 'wb') as f:
            pickle.dump(all_winning_games, f)
        print(f"Znaleziono {len(all_winning_games)} wygranych. Gotowe do wizualizacji")
    else:
        print("Brak wygranych gier")
        
    run_auto_backup()

def create_html_report(results):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""
    <html>
    <head><title>Raport Pasjans</title></head>
    <body>
        <h1>Raport Symulacji Pasjansa</h1>
        <p>Data: {now}</p>
        <p>Pliki: {len(results)}</p>
        <hr>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr>
                <th>Nazwa pliku</th>
                <th>Status</th>
                <th>Ruchy</th>
                <th>Info</th>
            </tr>
    """

    for r in results:
        html += f"""
            <tr>
                <td>{r['filename']}</td>
                <td>{r['status']}</td>
                <td>{r['moves_count']}</td>
                <td>{r['error_msg']}</td>
            </tr>
        """
    html += "</table></body></html>"

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Raport HTML wygenerowany: {REPORT_FILE}")

def run_gui_replay():
    if not os.path.exists(REPLAY_FILE):
        print("Brak zapisanych wygranych gier")
        return

    with open(REPLAY_FILE, 'rb') as f:
        winning_games = pickle.load(f)
    
    pygame.init()
    
    try:
        info = pygame.display.Info()
        SCREEN_WIDTH = info.current_w
        SCREEN_HEIGHT = info.current_h
    except:
        SCREEN_WIDTH = 1200
        SCREEN_HEIGHT = 800

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = game_class.Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

    for idx, game_data in enumerate(winning_games):
        filename = game_data["filename"]
        moves_cnt = game_data.get("moves_count", 0)
        
        pygame.display.set_caption(f"WIZUALIZACJA ({idx+1}/{len(winning_games)}) - {filename}")
        
        game.set_game_data(
            game_data["initial_deck"], 
            game_data["moves"], 
            filename=filename, 
            moves_count=moves_cnt
        )
        game.run()
    
    pygame.quit()

def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "--batch":
            run_batch_simulation()
        elif mode == "--replay":
            run_gui_replay()
        else:
            print(f"Nieznana opcja: {mode}")
            print("Użycie: python main.py --batch | --replay")
    else:
        print("Użycie: python main.py --batch | --replay  (lub uruchom run.bat / run.sh)")

if __name__ == "__main__":
    main()