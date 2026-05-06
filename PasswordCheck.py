import string

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

def check_dictionary(password: str) -> tuple[int, str]:
    blacklist = ["password", "12345", "123456", "admin", "qwerty"]
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

def calc_score(password: str) -> tuple[int, list[str]]:
    total = 0
    messages = []
    for check in (check_length, check_upper_lower, check_digits, check_symbols, check_dictionary):
        score, msg = check(password)
        total += score
        messages.append(msg)
    return total, messages

def classify(score: int) -> str:
    if score <= 1:
        return "Маш сул"
    elif score == 2:
        return "Сул"
    elif score == 3:
        return "Дунд зэрэг"
    elif score == 4:
        return "Сайн"
    else:
        return "Маш сайн"

def main():
    print("=== Нууц үгийн хүч шалгах хэрэгсэл ===")
    pwd = input("Нууц үг оруулна уу: ")
    score, msgs = calc_score(pwd)
    print("\nДүн:")
    for m in msgs:
        print("-", m)
    print(f"Нийт оноо: {score} / 6")
    print("Үнэлгээ:", classify(score))

if __name__ == "__main__":
    main()