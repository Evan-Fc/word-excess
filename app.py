from flask import Flask, render_template, request, jsonify
import json
import random

app = Flask(__name__)

# 导入完整的648个单词数据
from word_data import WORD_DATA

# 为了简洁，这里只显示部分单词，实际使用时应该包含所有648个单词
# 完整的648个单词数据在 word_table_words_simple.py 文件中

# 分类信息
CATEGORIES = {
    "基础术语": ["access", "algorithm", "array", "bug", "cache", "data", "file", "function", "variable", "system", "information"],
    "硬件与设备": ["CPU", "memory", "monitor", "printer", "router", "keyboard", "mouse", "server", "storage", "device", "hardware"],
    "网络与通信": ["Internet", "LAN", "bandwidth", "protocol", "Firewall", "network", "wireless", "ethernet", "modem", "communication", "connection"],
    "软件与开发": ["programming", "debug", "compile", "database", "API", "software", "application", "framework", "library", "development", "code"],
    "安全": ["antivirus", "encryption", "firewall", "phishing", "security", "authentication", "malware", "virus", "protection", "privacy"],
    "品牌与系统": ["Windows", "Linux", "Android", "iOS", "Microsoft", "Apple", "Google", "Amazon", "IBM", "system", "platform"]
}

# 学习进度存储（简单实现，实际应该用数据库）
learning_progress = {}

def get_words_by_category(category_name):
    """根据分类获取单词"""
    if category_name not in CATEGORIES:
        return []
    
    category_words = []
    category_keywords = CATEGORIES[category_name]
    
    for word_obj in WORD_DATA:
        word = word_obj["word"].lower()
        for keyword in category_keywords:
            if keyword.lower() in word:
                category_words.append(word_obj)
                break
    
    return category_words

def update_progress(word, correct):
    """更新学习进度"""
    if word not in learning_progress:
        learning_progress[word] = {
            "correct": 0,
            "total": 0,
            "mastery": 0.0
        }
    
    learning_progress[word]["total"] += 1
    if correct:
        learning_progress[word]["correct"] += 1
    
    # 计算掌握程度
    total = learning_progress[word]["total"]
    correct_count = learning_progress[word]["correct"]
    learning_progress[word]["mastery"] = correct_count / total if total > 0 else 0.0

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', total_words=len(WORD_DATA), categories=list(CATEGORIES.keys()))

@app.route('/learn')
def learn():
    """学习页面"""
    category = request.args.get('category', 'all')
    
    if category == 'all':
        words = WORD_DATA
    else:
        words = get_words_by_category(category)
    
    return render_template('learn.html', words=words, category=category, categories=list(CATEGORIES.keys()))

@app.route('/quiz')
def quiz():
    """测验页面"""
    quiz_type = request.args.get('type', 'random')
    category = request.args.get('category', 'all')
    
    if category == 'all':
        words = WORD_DATA
    else:
        words = get_words_by_category(category)
    
    return render_template('quiz.html', quiz_type=quiz_type, category=category, categories=list(CATEGORIES.keys()))

@app.route('/api/quiz/random')
def api_random_quiz():
    """随机测验API"""
    count = int(request.args.get('count', 10))
    category = request.args.get('category', 'all')
    
    if category == 'all':
        words = WORD_DATA
    else:
        words = get_words_by_category(category)
    
    # 随机选择单词
    selected_words = random.sample(words, min(count, len(words)))
    
    # 随机决定是英译中还是中译英
    quiz_questions = []
    for word in selected_words:
        direction = random.choice(['en_to_ch', 'ch_to_en'])
        if direction == 'en_to_ch':
            question = {
                'word': word['word'],
                'question': f"{word['word']} ({word['phonetic']})",
                'answer': word['chinese'],
                'direction': 'en_to_ch'
            }
        else:
            question = {
                'word': word['word'],
                'question': word['chinese'],
                'answer': word['word'],
                'direction': 'ch_to_en'
            }
        quiz_questions.append(question)
    
    return jsonify(quiz_questions)

@app.route('/api/quiz/check', methods=['POST'])
def api_check_quiz():
    """检查测验答案API"""
    data = request.json
    word = data.get('word')
    user_answer = data.get('user_answer', '').strip()
    correct_answer = data.get('correct_answer', '')
    direction = data.get('direction')
    
    # 检查答案是否正确
    if direction == 'en_to_ch':
        is_correct = user_answer == correct_answer
    else:
        is_correct = user_answer.lower() == correct_answer.lower()
    
    # 更新学习进度
    update_progress(word, is_correct)
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': correct_answer,
        'mastery': learning_progress.get(word, {}).get('mastery', 0.0)
    })

@app.route('/api/words')
def api_words():
    """获取所有单词API"""
    return jsonify(WORD_DATA)

@app.route('/api/progress')
def api_progress():
    """获取学习进度API"""
    return jsonify(learning_progress)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)