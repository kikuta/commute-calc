from flask import Flask, render_template_string, request
import calendar
from datetime import datetime

app = Flask(__name__)

# HTML/JavaScript テンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交通費計算ツール</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f7f6; padding: 20px; color: #333; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .input-section { margin-bottom: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .input-group { display: flex; flex-direction: column; }
        label { font-size: 0.8em; font-weight: bold; margin-bottom: 5px; color: #666; }
        input, select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        
        .calendar-grid { 
            display: grid; 
            grid-template-columns: repeat(7, 1fr); 
            gap: 5px; 
            margin-top: 20px; 
            background: #eee; 
            padding: 10px; 
            border-radius: 8px;
        }
        .day-box { 
            background: white; 
            padding: 10px 5px; 
            text-align: center; 
            border-radius: 4px; 
            font-size: 0.9em;
        }
        .day-box input { cursor: pointer; }
        .weekday-header { font-weight: bold; text-align: center; padding-bottom: 5px; color: #555; }
        
        .result-section { 
            margin-top: 30px; 
            padding: 20px; 
            background: #e9ecef; 
            border-radius: 8px; 
        }
        #output-text { 
            width: 100%; 
            height: 100px; 
            margin-top: 10px; 
            padding: 10px; 
            box-sizing: border-box;
            font-family: monospace;
            border: 1px solid #ddd;
        }
        .total-display { font-size: 1.5em; font-weight: bold; color: #007bff; }
    </style>
</head>
<body>

<div class="container">
    <h2>交通費計算ツール</h2>
    
    <form id="calc-form" method="GET">
        <div class="input-section">
            <div class="input-group">
                <label>年</label>
                <select name="year" onchange="this.form.submit()">
                    {% for y in range(2024, 2028) %}
                    <option value="{{ y }}" {% if y == year %}selected{% endif %}>{{ y }}年</option>
                    {% endfor %}
                </select>
            </div>
            <div class="input-group">
                <label>月</label>
                <select name="month" onchange="this.form.submit()">
                    {% for m in range(1, 13) %}
                    <option value="{{ m }}" {% if m == month %}selected{% endif %}>{{ m }}月</option>
                    {% endfor %}
                </select>
            </div>
            <div class="input-group">
                <label>出発駅</label>
                <input type="text" id="start_station" value="Kuhombutsu" oninput="updateResult()">
            </div>
            <div class="input-group">
                <label>到着駅</label>
                <input type="text" id="end_station" value="Roppongi" oninput="updateResult()">
            </div>
            <div class="input-group">
                <label>片道運賃 (円)</label>
                <input type="number" id="fare" value="358" oninput="updateResult()">
            </div>
        </div>

        <div class="calendar-grid">
            <div class="weekday-header">日</div><div class="weekday-header">月</div>
            <div class="weekday-header">火</div><div class="weekday-header">水</div>
            <div class="weekday-header">木</div><div class="weekday-header">金</div>
            <div class="weekday-header">土</div>
            
            {% for empty in range(first_weekday) %}
                <div></div>
            {% endfor %}
            
            {% for day in days %}
                <div class="day-box">
                    {{ day }}<br>
                    <input type="checkbox" class="day-check" value="{{ day }}" onclick="updateResult()">
                </div>
            {% endfor %}
        </div>
    </form>

    <div class="result-section">
        <div>合計出勤日数: <span id="count-display">0</span> 日</div>
        <div>合計金額: <span class="total-display">¥<span id="total-display">0</span></span></div>
        <hr>
        <label>コピペ用出力:</label>
        <textarea id="output-text" readonly></textarea>
    </div>
</div>

<script>
function updateResult() {
    const start = document.getElementById('start_station').value;
    const end = document.getElementById('end_station').value;
    const fare = parseInt(document.getElementById('fare').value) || 0;
    const year = {{ year }};
    const monthName = "{{ month_name }}";
    
    const checkboxes = document.querySelectorAll('.day-check:checked');
    const selectedDays = Array.from(checkboxes).map(cb => cb.value);
    const count = selectedDays.length;
    const roundTrip = fare * 2;
    const total = roundTrip * count;

    // 表示の更新
    document.getElementById('count-display').innerText = count;
    document.getElementById('total-display').innerText = total.toLocaleString();

    // テキスト生成
    if (count > 0) {
        const daysText = selectedDays.join(', ');
        const output = `${start}=${end} Round Trip Ticket * ${count} Days\\n` +
                       `${daysText} in ${monthName} ${year}\\n` +
                       `${start} <--> ${end} ${fare}*2 (Round Trip) *${count} = ${total}`;
        document.getElementById('output-text').value = output;
    } else {
        document.getElementById('output-text').value = "";
    }
}
// 初期化
updateResult();
</script>

</body>
</html>
"""

@app.route('/')
def index():
    # 現在の年月をデフォルトに設定
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # カレンダー計算
    cal = calendar.monthcalendar(year, month)
    first_weekday = cal[0].index(next(d for d in cal[0] if d != 0))
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)]
    month_name = calendar.month_name[month]

    return render_template_string(
        HTML_TEMPLATE, 
        year=year, 
        month=month, 
        days=days, 
        first_weekday=first_weekday,
        month_name=month_name
    )

if __name__ == '__main__':
    app.run(debug=False)