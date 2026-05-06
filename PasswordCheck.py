import string
import os
import sys
from pathlib import Path
# Windows систем дээр ANSI өнгөний кодыг дэмждэг болгож идэвхжүүлэх
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    import msvcrt
else:
    import tty
    import termios

# Терминалын өнгөнүүд
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
FILE_PATH = Path(__file__).parent / "blacklist.txt"
# Шалгах функцууд (хэвээр үлдсэн)
def check_length(password: str) -> tuple[int, str]:
    length = len(password)
    if length < 8:
        return 0, "Урт нь дор хаяж 8 тэмдэгт байх ёстой."
    elif 8 <= length < 12:
        return 1, "Урт боломжийн байна."
    else:
        return 2, "Урт хангалттай сайн байна."

def check_upper_lower(password: str) -> tuple[int, str]:
    has_upper = any(ch.isupper() for ch in password)
    has_lower = any(ch.islower() for ch in password)
    if has_upper and has_lower:
        return 1, "Том болон жижиг үсгийн хослол байна."
    return 0, "Том, жижиг үсэг холилдоогүй байна."

def check_digits(password: str) -> tuple[int, str]:
    if any(ch.isdigit() for ch in password):
        return 1, "Тоо агуулагдсан байна."
    return 0, "Тоо алга байна."

def load_blacklist() -> set[str]: # Жагсаалт биш олонлог буцаана
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        # {} хаалт ашиглан set (олонлог) үүсгэж байна
        return {line.strip().lower() for line in f if line.strip()}

def check_dictionary(password: str) -> tuple[int, str]:
    blacklist = load_blacklist()
    lower_pwd = password.lower() 
    for bad_word in blacklist:
        if bad_word in lower_pwd:
            return 0, f"Сул тал: '{bad_word}' гэсэн амархан таагдах үг орсон байна."
            
    return 1, "Түгээмэл сул үг агуулаагүй байна."

def check_symbols(password: str) -> tuple[int, str]:
    symbols = set(string.punctuation)
    if any(ch in symbols for ch in password):
        return 1, "Тусгай тэмдэгт орсон байна."
    return 0, "Тусгай тэмдэгт байхгүй байна."

# Оноо болон мэдээллийг жагсааж буцаах
def calc_score(password: str) -> tuple[int, list[tuple[int, str]]]:
    total = 0
    messages = []
    # Шалгалт бүрийн оноо болон текстийг хадгална
    for check in (check_length, check_upper_lower, check_digits, check_symbols, check_dictionary):
        score, msg = check(password)
        total += score
        messages.append((score, msg))
    return total, messages

def classify(score: int) -> str:
    if score <= 1:
        return f"{RED}Маш сул{RESET}"
    elif score == 2:
        return f"{RED}Сул{RESET}"
    elif score == 3:
        return f"{YELLOW}Дунд зэрэг{RESET}"
    elif score == 4:
        return f"{GREEN}Сайн{RESET}"
    else:
        return f"{GREEN}Маш сайн{RESET}"

# Товчлуур дарахыг шууд мэдрэх функц (OS-оос хамаарч өөр ажиллана)
def get_key_char() -> bytes | None:
    if os.name == 'nt':
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):  # Функционал товчлуурууд (сум гэх мэт)
            msvcrt.getch()
            return None
        return ch
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.encode('utf-8')

def main():
    password = ""
    
    while True:
        # Дэлгэцийг цэвэрлэх (Шууд шинэчлэгдэж байгаа мэт харагдуулна)
        print("\033[H\033[2J\033[3J", end="")
        
        print("=== Нууц үгийн хүч шалгах хэрэгсэл (Мэдрэгч горим) ===")
        print("Бичиж дуусаад 'Enter' дарж баталгаажуулна уу.\n")
        
        # Нууц үгийг харуулах (Хэрэв нууцлахыг хүсвэл '*' * len(password) гэж бичиж болно)
        print(f"Нууц үг: {password}")
        print("-" * 55)
        
        score, msgs = calc_score(password)
        
        # Үр дүнг өнгөтэйгөөр хэвлэх
        print("Шалгуур үзүүлэлтүүд:")
        for status_score, msg in msgs:
            if status_score == 0:
                # Шаардлага хангаагүй бол УЛААН
                print(f" {RED}✗ {msg}{RESET}")
            else:
                # Хангасан бол НОГООН
                print(f" {GREEN}✓ {msg}{RESET}")
                
        print("-" * 55)
        print(f"Нийт оноо: {score} / 6")
        print("Үнэлгээ:", classify(score))
        
        # Хэрэглэгчийн дараагийн товчлуурыг хүлээх
        char_bytes = get_key_char()
        if char_bytes is None:
            continue
            
        # Enter дарагдсан бол дуусгах
        if char_bytes in (b'\r', b'\n'):
            break
        # Backspace дарагдсан бол сүүлийн тэмдэгтийг устгах
        elif char_bytes in (b'\x08', b'\x7f'):
            password = password[:-1]
        else:
            try:
                char_str = char_bytes.decode('utf-8')
                if char_str.isprintable():
                    password += char_str
            except UnicodeDecodeError:
                pass

    print("\nБаярлалаа! Таны нууц үг хадгалагдлаа.")

if __name__ == "__main__":
    main()
