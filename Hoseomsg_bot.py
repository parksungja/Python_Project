import json
import threading
from telegram import *
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta
import asyncio


# 토큰을 TOKEN 변수에 저장
TOKEN = '7772440463:AAGb2Gh-PXu7oahc9AlToG31ucW-R8mmw74'

# Telegram bot 초기화
app = Application.builder().token(TOKEN).build()

# /start 커맨드 핸들러 - 완
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("[호서대 알리미] 안녕하세요. 호서대 알리미 봇입니다.\n/help 명령어를 통해 이용해주세요")

# /help 커맨드 핸들러 - 커멘드 추가할때마다 수정
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("사용 가능한 명령어:\n"
                                    "/portal - 호서대 포털 사이트\n"
                                    "/info - 호서대 공지사항\n"
                                    "/cominfo - 컴퓨터공학부 공지사항\n"
                                    "/shuttle - 셔틀버스 시간표\n"
                                    "/shumark - 셔틀 즐겨찾기"
                                    "/reminder - 리마인더")
    
# /portal 커맨드 핸들러 - 완
async def portal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("https://sso.hoseo.edu/\n"
                                    "위 사이트에서 호서대 포털을 이용할 수 있습니다.")

# /info 커맨드 핸들러 - 완
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("https://www.hoseo.ac.kr/Home/BBSList.mbz?action=MAPP_1708240139\n"
                                    "위 사이트에서 호서대의 최신 공지사항을 확인할 수 있습니다.")
    
# /cominfo 커맨드 핸들러 - 완
async def cominfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("http://computer.hoseo.ac.kr/Home/BBSList.mbz?action=MAPP_2107121893\n"
                                    "위 사이트에서 컴퓨터공학부의 최신 공지사항을 확인할 수 있습니다.")
                            
# 셔틀버스 시간표 데이터 - 완
data_shuttle_schedule = {
    "평일":{
        "아산캠": {
            "7": ["45분(첫)"],
            "8": ["00분", "15분", "30분", "45분"],
            "9": ["00분", "10분", "15분", "25분", "30분", "40분", "45분", "55분"],
            "10": ["00분", "10분", "15분", "25분", "30분", "45분", "55분"],
            "11": ["00분", "20분", "30분", "40분", "55분"],
            "12": ["00분", "20분", "30분", "40분", "55분"],
            "13": ["00분", "20분", "30분", "40분", "55분"],
            "14": ["00분", "10분", "15분", "25분", "30분", "40분","45분", "55분"],
            "15": ["00분", "10분", "15분", "25분", "30분", "40분", "50분"],
            "16": ["00분", "10분", "15분", "25분", "30분", "40분","45분", "55분"],
            "17": ["00분", "10분", "15분", "25분", "30분", "45분"],
            "18": ["00분", "15분", "30분", "45분"],
            "19": ["00분", "25분", "30분"],
            "20": ["00분", "30분", "55분"],
            "21": ["00분(막)"]
        }
    },
    "토요일": {
        "아산캠": {
            "8": ["20분"],
            "10": ["00분"],
            "12": ["30분"],
            "13": ["30분"],
            "15": ["00분"],
            "16": ["00분"],
            "17": ["00분"],
            "18": ["00분"]
        }
    },
    "일요일(공휴일)": {
        "아산캠": {
            "10": ["00분"],
            "12": ["00분"],
            "13": ["00분"],
            "14": ["00분"],
            "15": ["00분"],
            "16": ["00분"],
            "17": ["00분", "30분"],
            "18": ["00분", "30분"],
            "19": ["00분", "30분"],
            "20": ["00분", "30분"],
            "21": ["00분"]
        }
    }
    # 다른 역의 데이터 추가 가능
}

# /shuttle 명령어 핸들러 - 완
async def shuttle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("평일", callback_data='weekday')],
        [InlineKeyboardButton("토요일", callback_data='saturday')],
        [InlineKeyboardButton("일요일(공휴일)", callback_data='sunday')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("셔틀버스 일정을 선택하세요:", reply_markup=reply_markup)

# 평일/주말 선택 후 시간대 선택 - 완
async def day_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 선택된 day_type 설정
    if query.data == 'weekday':
        day_type = '평일'
    elif query.data == 'saturday':
        day_type = '토요일'
    elif query.data == 'sunday':
        day_type = '일요일(공휴일)'

    context.user_data['day_type'] = day_type

    keyboard = [
        [InlineKeyboardButton("특정시간대", callback_data='specific_time')],
        [InlineKeyboardButton("전체", callback_data='full_schedule')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 기존 메시지를 수정
    await query.edit_message_text(
        text=f"{day_type} 셔틀버스 시간표를 선택하세요:",
        reply_markup=reply_markup
    )

# 특정시간대 또는 전체 시간표 선택 - 완
async def schedule_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    day_type = context.user_data.get('day_type')
    location = "아산캠"

    if not day_type:
        await query.edit_message_text("일정 유형이 선택되지 않았습니다. 다시 시도해주세요.")
        return

    if query.data == 'specific_time':
        context.user_data['specific_time'] = True
        await query.edit_message_text("조회할 시간을 입력하세요 (예: 9):")
    elif query.data == 'full_schedule':
        full_schedule_text = get_full_schedule(day_type, location)
        await query.edit_message_text(f"전체 시간표:\n```\n{full_schedule_text}\n```", parse_mode="Markdown")

# 사용자가 특정 시간을 입력하면 해당 시간표를 출력 - 완
async def specific_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('specific_time'):
        time_input = update.message.text.strip()
        if not time_input.isdigit():
            await update.message.reply_text("올바른 숫자를 입력하세요 (예: 9)")
            return

        day_type = context.user_data.get('day_type')
        location = "아산캠"

        # 시간표 조회
        table_text = get_shuttle_schedule(day_type, location, time_input)
        await update.message.reply_text(f"```\n{table_text}\n```", parse_mode="Markdown")
        del context.user_data['specific_time']

# 특정 시간대 시간표 조회 함수 - 완
def get_shuttle_schedule(day_type, location, hour):
    schedule = data_shuttle_schedule.get(day_type, {}).get(location, {})
    if hour in schedule:
        times = schedule[hour]
        header = f"{day_type} {location} {hour}시 출발 시간표"
        separator = "-" * len(header)
        rows = [header, separator] + [f"{hour}시 {time} 출발" for time in times]
        return "\n".join(rows)
    return "해당 시간에 대한 셔틀버스 정보가 없습니다."

# 전체 시간표 조회 함수 - 완
def get_full_schedule(day_type, location):
    schedule = data_shuttle_schedule.get(day_type, {}).get(location, {})
    rows = [f"{hour}시: " + ", ".join(times) for hour, times in schedule.items()]
    return "\n".join(rows) if rows else "전체 시간표를 찾을 수 없습니다."

# 사용자 즐겨찾기 데이터를 저장할 딕셔너리
user_favorites = {}
user_notifications = {}

# JSON 파일로 데이터 저장
def save_data():
    with open('user_favorites.json', 'w') as file:
        json.dump(user_favorites, file)

# JSON 파일에서 데이터 불러오기
def load_data():
    global user_favorites
    try:
        with open('user_favorites.json', 'r') as file:
            user_favorites = json.load(file)
    except FileNotFoundError:
        user_favorites = {}

# 데이터 로드
load_data()

# /remark 명령어 - 즐겨찾기 추가 및 수정
async def remark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_favorites:
        user_favorites[user_id] = []

    keyboard = [
        [InlineKeyboardButton("추가", callback_data='add_favorite')],
        [InlineKeyboardButton("수정", callback_data='edit_favorite')],
        [InlineKeyboardButton("종료", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 메인 메뉴를 새로운 메시지로 보냄
    if update.message:
        await update.message.reply_text("즐겨찾기를 추가하거나 수정하세요:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("즐겨찾기를 추가하거나 수정하세요:", reply_markup=reply_markup)
    
# 종료 버튼 핸들러
async def exit_remark_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("메뉴를 종료합니다.")
    
# 즐겨찾기 항목 보기
async def show_favorite_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    favorites = user_favorites.get(user_id, [])

    # 즐겨찾기 목록 확인
    if not favorites:
        await query.edit_message_text("저장된 즐겨찾기가 없습니다.")
        return

    # 저장된 즐겨찾기 목록을 버튼으로 표시
    buttons = [[InlineKeyboardButton(f"{fav} 삭제", callback_data=f"delete_{idx}")] for idx, fav in enumerate(favorites)]
    buttons.append([InlineKeyboardButton("뒤로가기", callback_data='back_to_menu')])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("즐겨찾기 목록:", reply_markup=reply_markup)

# 즐겨찾기 추가/수정 선택 핸들러
async def remark_option_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'add_favorite':
        await show_days_for_favorite(update, context)
    elif query.data == 'edit_favorite':
        await show_favorite_list(update, context)

# 즐겨찾기 항목 삭제
async def delete_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    index_str = query.data.split("_")[1]

    if not index_str.isdigit():
        await query.edit_message_text("잘못된 인덱스입니다.")
        return

    index = int(index_str)
    favorites = user_favorites.get(user_id, [])

    if index < 0 or index >= len(favorites):
        await query.edit_message_text("삭제할 항목이 없습니다.")
        return

    deleted_item = favorites.pop(index)
    save_data()

    # 삭제 후 메시지 수정
    await query.edit_message_text(f"삭제됨: {deleted_item}")

    # 메인 메뉴를 새로운 메시지로 표시
    await remark_command(update, context)

# 요일 선택 핸들러
async def show_days_for_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 요일 선택 버튼 생성
    keyboard = [
        [InlineKeyboardButton("월요일", callback_data='day_mon'), InlineKeyboardButton("화요일", callback_data='day_tue')],
        [InlineKeyboardButton("수요일", callback_data='day_wed'), InlineKeyboardButton("목요일", callback_data='day_thu')],
        [InlineKeyboardButton("금요일", callback_data='day_fri'), InlineKeyboardButton("토요일", callback_data='day_sat')],
        [InlineKeyboardButton("일요일", callback_data='day_sun')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 현재 메시지 텍스트와 버튼이 동일한지 확인 후 수정
    current_text = query.message.text if query.message else ""
    new_text = "요일을 선택하세요:"
    if current_text != new_text or query.message.reply_markup != reply_markup:
        await query.edit_message_text(new_text, reply_markup=reply_markup)
        
# 요일 선택 핸들러
async def handle_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 사용자가 선택한 요일을 저장
    selected_day = query.data.split('_')[1]
    context.user_data['selected_day'] = selected_day

    # 시간 선택 화면으로 이동
    await show_hours_for_favorite(update, context)

# 시간 선택
ITEMS_PER_PAGE = 5  # 한 페이지당 표시할 시간 개수
async def show_hours_for_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_day = context.user_data.get('selected_day')
    if not selected_day:
        await query.edit_message_text("요일 선택이 잘못되었습니다. 다시 시도해주세요.")
        return

    current_page = context.user_data.get('hour_page', 0)
    hours = [f"{hour}시" for hour in range(7, 22)]
    total_pages = (len(hours) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_index = current_page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    page_hours = hours[start_index:end_index]
    buttons = [[InlineKeyboardButton(hour, callback_data=f"select_hour:{hour.split('시')[0]}")] for hour in page_hours]

    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(InlineKeyboardButton("이전", callback_data='prev_hour_page'))
    if current_page < total_pages - 1:
        navigation_buttons.append(InlineKeyboardButton("다음", callback_data='next_hour_page'))
    buttons.append(navigation_buttons)

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("시간을 선택하세요:", reply_markup=reply_markup)
    
# 페이지 변경 핸들러(시간)
async def change_hour_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 현재 페이지 가져오기
    current_page = context.user_data.get('hour_page', 0)

    # 페이지 변경
    if query.data == 'prev_hour_page':
        context.user_data['hour_page'] = current_page - 1
    elif query.data == 'next_hour_page':
        context.user_data['hour_page'] = current_page + 1

    # 변경된 페이지에서 다시 시간 선택 화면 표시
    await show_hours_for_favorite(update, context)

# 시간 선택 핸들러
async def handle_hour_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 선택한 시간을 저장
    selected_hour = query.data.split(':')[1]
    context.user_data['selected_hour'] = selected_hour

    # 분 선택 화면으로 이동
    await show_minutes_for_favorite(update, context)

# 분 선택
ITEMS_PER_PAGE_MINUTES = 4  # 한 페이지당 표시할 분 개수
async def show_minutes_for_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_hour = context.user_data.get('selected_hour')
    if not selected_hour:
        await query.edit_message_text("시간 선택이 잘못되었습니다. 다시 시도해주세요.")
        return

    current_page = context.user_data.get('minute_page', 0)
    minutes = ["00분", "15분", "30분", "45분"]
    start_index = current_page * ITEMS_PER_PAGE_MINUTES
    end_index = start_index + ITEMS_PER_PAGE_MINUTES

    page_minutes = minutes[start_index:end_index]
    buttons = [[InlineKeyboardButton(minute, callback_data=f"select_minute:{minute.split('분')[0]}")] for minute in page_minutes]

    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(InlineKeyboardButton("이전", callback_data='prev_minute_page'))
    if end_index < len(minutes):
        navigation_buttons.append(InlineKeyboardButton("다음", callback_data='next_minute_page'))
    buttons.append(navigation_buttons)

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("분을 선택하세요:", reply_markup=reply_markup)
    
# 페이지 변경 핸들러(분)
async def change_minute_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 현재 페이지 가져오기
    current_page = context.user_data.get('minute_page', 0)

    # 페이지 변경
    if query.data == 'prev_minute_page':
        context.user_data['minute_page'] = current_page - 1
    elif query.data == 'next_minute_page':
        context.user_data['minute_page'] = current_page + 1

    await show_minutes_for_favorite(update, context)

# 분 선택 핸들러
async def handle_minute_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    selected_day = context.user_data.get('selected_day')
    selected_hour = context.user_data.get('selected_hour')
    selected_minute = query.data.split(':')[1]

    if not selected_day or not selected_hour or not selected_minute:
        await query.edit_message_text("잘못된 입력입니다. 다시 시도해주세요.")
        return

    favorite_time = f"{selected_day} {selected_hour}:{selected_minute}"
    if user_id not in user_favorites:
        user_favorites[user_id] = []

    # 즐겨찾기 추가 처리
    if favorite_time not in user_favorites[user_id]:
        user_favorites[user_id].append(favorite_time)
        save_data()
        await query.edit_message_text(f"즐겨찾기 추가됨: {favorite_time}")
    else:
        await query.edit_message_text("이미 추가된 즐겨찾기입니다.")

    # 메인 메뉴를 새로운 메시지로 표시
    await remark_command(update, context)

# 즐겨찾기 저장
async def save_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    selected_day = context.user_data.get('selected_day')
    selected_hour = context.user_data.get('selected_hour')
    selected_minute = query.data.split(":")[1]

    if not selected_day or not selected_hour or not selected_minute:
        await query.edit_message_text("잘못된 입력입니다. 다시 시도해주세요.")
        return

    favorite_time = f"{selected_day} {selected_hour}:{selected_minute}"

    if user_id not in user_favorites:
        user_favorites[user_id] = []

    if favorite_time not in user_favorites[user_id]:
        user_favorites[user_id].append(favorite_time)
        save_data()
        await query.edit_message_text(f"즐겨찾기 추가됨: {favorite_time}")
    else:
        await query.edit_message_text("이미 추가된 즐겨찾기입니다.")

# /shumark 명령어 핸들러
async def shumark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    favorites = user_favorites.get(user_id, [])
    if not favorites:
        await update.message.reply_text("저장된 즐겨찾기가 없습니다.")
        return
    favorites_text = "\n".join(favorites)
    await update.message.reply_text(f"저장된 즐겨찾기 목록:\n{favorites_text}")

# /reminder 커맨드 - 알림 설정 시작
async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("오늘", callback_data='today'), InlineKeyboardButton("내일", callback_data='tomorrow')],
        [InlineKeyboardButton("직접 입력", callback_data='manual')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("알림 날짜를 선택하세요:", reply_markup=reply_markup)

# 날짜 선택 시 시간 선택을 위한 버튼 표시
async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    date_choice = query.data
    if date_choice == 'today':
        context.user_data['reminder_date'] = datetime.now().strftime("%Y-%m-%d")
    elif date_choice == 'tomorrow':
        context.user_data['reminder_date'] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        await query.edit_message_text("MM-DD 형식으로 날짜를 입력해주세요.")
        context.user_data['manual_date'] = True
        return

    # 시간 선택 버튼 표시 - 직접입력 칸 추가
    keyboard = [
        [InlineKeyboardButton(f"{hour}:00", callback_data=f"{hour}:00"), InlineKeyboardButton(f"{hour}:30", callback_data=f"{hour}:30")]
        for hour in range(8, 22)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("알림 시간을 선택하세요:", reply_markup=reply_markup)

# 시간 선택 시 리마인더 메시지 요청
async def time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    time_choice = query.data
    context.user_data['reminder_time'] = time_choice

    await query.edit_message_text("알림 메시지를 입력해주세요.")

# 사용자가 메시지를 입력하면 리마인더 설정 완료
async def message_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminder_message = update.message.text
    reminder_date = context.user_data.get('reminder_date')
    reminder_time = context.user_data.get('reminder_time')
    
    # 날짜와 시간 조합하여 알림 시간 설정
    reminder_datetime = datetime.strptime(f"{reminder_date} {reminder_time}", "%Y-%m-%d %H:%M")

    # 현재 시간보다 이른 경우 다음 날로 조정
    if reminder_datetime < datetime.now():
        reminder_datetime += timedelta(days=1)

    delay = (reminder_datetime - datetime.now()).total_seconds()

    await update.message.reply_text(f"리마인더가 {reminder_datetime.strftime('%Y-%m-%d %H:%M')}에 전송됩니다: '{reminder_message}'")

    # 알림 시간까지 대기 후 알림 전송
    await asyncio.sleep(delay)
    await update.message.reply_text(f"🔔 리마인더: {reminder_message}")

# 메인 함수
def main():
    # Telegram bot 초기화
    app = Application.builder().token(TOKEN).build()

    # 모든 핸들러 등록
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("shuttle", shuttle_command))
    app.add_handler(CallbackQueryHandler(day_selected, pattern='^(weekday|saturday|sunday)$'))
    app.add_handler(CallbackQueryHandler(schedule_type_selected, pattern='^(specific_time|full_schedule)$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, specific_time_handler))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("cominfo", cominfo_command))
    app.add_handler(CommandHandler("portal", portal_command))
    app.add_handler(CommandHandler("reminder", reminder))
    app.add_handler(CallbackQueryHandler(date_selected, pattern='^(today|tomorrow|manual)$'))
    app.add_handler(CallbackQueryHandler(time_selected, pattern=r'^\d{1,2}:\d{2}$'))
    app.add_handler(CommandHandler("shumark", shumark_command))
    app.add_handler(CommandHandler("remark", remark_command))
    
    # /remark 콜백 핸들러 추가
    app.add_handler(CallbackQueryHandler(remark_option_selected, pattern='^(add_favorite|edit_favorite)$'))
    app.add_handler(CallbackQueryHandler(show_days_for_favorite, pattern='^(mon|tue|wed|thu|fri|sat|sun)$'))
    app.add_handler(CallbackQueryHandler(handle_day_selection, pattern='^day_'))
    app.add_handler(CallbackQueryHandler(show_hours_for_favorite, pattern='^hour:'))
    app.add_handler(CallbackQueryHandler(handle_hour_selection, pattern='^select_hour:'))
    app.add_handler(CallbackQueryHandler(show_minutes_for_favorite, pattern='^minute:'))
    app.add_handler(CallbackQueryHandler(handle_minute_selection, pattern='^select_minute:'))
    app.add_handler(CallbackQueryHandler(save_favorite, pattern='^minute:'))
    app.add_handler(CallbackQueryHandler(delete_favorite, pattern='^delete_\\d+$'))
    app.add_handler(CallbackQueryHandler(change_hour_page, pattern='^(prev_hour_page|next_hour_page)$'))
    app.add_handler(CallbackQueryHandler(change_minute_page, pattern='^(prev_minute_page|next_minute_page)$'))
    app.add_handler(CallbackQueryHandler(exit_remark_menu, pattern='^exit$'))

    # Telegram bot 실행
    app.run_polling()

if __name__ == "__main__":
    main()
