from flask import Flask, request, jsonify
import random
import string
import webbrowser
import threading
import time

app = Flask(__name__)

# HTML-код для страницы с обновленным стилем кнопки
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PasswordGenix</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.8/clipboard.min.js"></script>
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .animate-fadeIn {
            animation: fadeIn 0.5s ease-out;
        }
        .gradient-button {
            background: linear-gradient(
                45deg,
                #F3A8C2, #C3A8F3, #F3A8C2, #C3A8F3, 
                #F3A8C2, #F3A8C2, #F3A8C2, #F3A8C2, #C3A8F3
            );
            background-size: 400% 400%;
            animation: gradientShift 3s ease infinite;
            transition: transform 0.3s ease;
        }
        .gradient-button:hover {
            transform: scale(1.05);
        }
        .result-animate {
            animation: fadeIn 0.3s ease-out;
        }
        .history-item {
            transition: all 0.3s ease;
        }
        .history-item:hover {
            transform: translateX(5px);
        }
        .glassmorphism {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body class="min-h-screen bg-gradient-to-br from-purple-600 via-blue-500 to-cyan-400 flex items-center justify-center">
    <div class="glassmorphism p-8 rounded-2xl shadow-xl w-full max-w-md animate-fadeIn">
        <h1 class="text-3xl font-extrabold text-white text-center mb-6 drop-shadow-md">PasswordGenix</h1>
        
        <!-- Форма настроек -->
        <div class="mb-6">
            <label class="block text-sm font-medium text-white mb-2">Длина пароля</label>
            <input type="number" id="length" value="12" min="4" max="50" class="w-full p-3 rounded-lg bg-gray-800 text-white border border-purple-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 transition duration-300">
        </div>
        <div class="mb-6 space-y-3">
            <label class="flex items-center text-white">
                <input type="checkbox" id="letters" checked class="mr-2 h-5 w-5 text-purple-500 rounded focus:ring-purple-500">
                <span>Буквы (a-z, A-Z)</span>
            </label>
            <label class="flex items-center text-white">
                <input type="checkbox" id="numbers" checked class="mr-2 h-5 w-5 text-purple-500 rounded focus:ring-purple-500">
                <span>Цифры (0-9)</span>
            </label>
            <label class="flex items-center text-white">
                <input type="checkbox" id="symbols" checked class="mr-2 h-5 w-5 text-purple-500 rounded focus:ring-purple-500">
                <span>Символы (!@#$%)</span>
            </label>
        </div>
        
        <!-- Кнопка генерации -->
        <button id="generate" class="w-full gradient-button text-white p-3 rounded-lg text-shadow-md">Сгенерировать</button>
        
        <!-- Результат -->
        <div id="result" class="mt-6 p-4 rounded-lg bg-gray-900/50 hidden result-animate">
            <p class="text-white"><strong>Пароль:</strong> <span id="password"></span></p>
            <p class="text-white"><strong>Надежность:</strong> <span id="strength"></span></p>
            <button id="copy" class="mt-3 bg-gradient-to-r from-green-400 to-teal-500 text-white p-2 rounded-lg hover:from-green-500 hover:to-teal-600 transition duration-300" data-clipboard-target="#password">Копировать</button>
        </div>
        
        <!-- История паролей -->
        <div id="history" class="mt-6">
            <h2 class="text-lg font-semibold text-white mb-2">История паролей</h2>
            <ul id="history-list" class="text-white list-disc pl-5 space-y-2"></ul>
        </div>
    </div>

    <script>
        // Инициализация Clipboard.js
        const clipboard = new ClipboardJS('#copy');
        clipboard.on('success', () => alert('Пароль скопирован!'));
        clipboard.on('error', () => alert('Ошибка копирования!'));

        // Генерация пароля
        document.getElementById('generate').addEventListener('click', async () => {
            const length = document.getElementById('length').value;
            const letters = document.getElementById('letters').checked;
            const numbers = document.getElementById('numbers').checked;
            const symbols = document.getElementById('symbols').checked;

            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ length, letters, numbers, symbols })
            });
            const data = await response.json();

            const resultDiv = document.getElementById('result');
            const passwordSpan = document.getElementById('password');
            const strengthSpan = document.getElementById('strength');

            if (data.error) {
                resultDiv.classList.add('hidden');
                alert(data.error);
                return;
            }

            resultDiv.classList.remove('hidden');
            resultDiv.classList.add('result-animate');
            passwordSpan.textContent = data.password;
            strengthSpan.textContent = data.strength;
            strengthSpan.style.color = data.color;

            // Сохранение в историю
            const historyList = document.getElementById('history-list');
            const li = document.createElement('li');
            li.textContent = data.password;
            li.classList.add('history-item');
            historyList.prepend(li);

            // Сохранение в localStorage
            let history = JSON.parse(localStorage.getItem('passwordHistory') || '[]');
            history.unshift(data.password);
            if (history.length > 10) history.pop();
            localStorage.setItem('passwordHistory', JSON.stringify(history));
        });

        // Загрузка истории из localStorage
        window.onload = () => {
            const history = JSON.parse(localStorage.getItem('passwordHistory') || '[]');
            const historyList = document.getElementById('history-list');
            history.forEach(password => {
                const li = document.createElement('li');
                li.textContent = password;
                li.classList.add('history-item');
                historyList.appendChild(li);
            });
        };
    </script>
</body>
</html>
"""

# Функция генерации пароля
def generate_password(length, use_letters, use_numbers, use_symbols):
    characters = ''
    if use_letters:
        characters += string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
    
    if not characters:
        return None
    
    return ''.join(random.choice(characters) for _ in range(length))

# Функция проверки надежности пароля
def check_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1
    
    if score <= 2:
        return "Слабый", "red"
    elif score <= 4:
        return "Средний", "yellow"
    else:
        return "Сильный", "green"

@app.route('/')
def index():
    return HTML_CONTENT

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    length = int(data.get('length', 12))
    use_letters = data.get('letters', False)
    use_numbers = data.get('numbers', False)
    use_symbols = data.get('symbols', False)
    
    password = generate_password(length, use_letters, use_numbers, use_symbols)
    if not password:
        return jsonify({'error': 'Выберите хотя бы один тип символов!'})
    
    strength, color = check_strength(password)
    return jsonify({
        'password': password,
        'strength': strength,
        'color': color
    })

# Функция для открытия браузера
def open_browser():
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Запускаем браузер в отдельном потоке
    threading.Thread(target=open_browser).start()
    app.run(debug=False)
