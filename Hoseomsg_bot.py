from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 토큰을 TOKEN 변수에 저장
TOKEN = '7772440463:AAGb2Gh-PXu7oahc9AlToG31ucW-R8mmw74'

# /start 커맨드 핸들러 - 완
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("[호서대 알리미] 안녕하세요. 호서대 알리미 봇입니다.\n/help 명령어를 통해 이용해주세요")

# /help 커맨드 핸들러 - 커멘드 추가할때마다 수정
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("사용 가능한 명령어:\n"
                                    "/portal - 호서대 포털 사이트"
                                    "/info - 학교 공지사항\n"
                                    "/cominfo - 컴퓨터공학부 공지사항\n"
                                    "/shuttle - 셔틀버스 시간표\n"
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
    
# /shuttle 커맨드 핸들러
async def shuttle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ex) /shu 천안아산역 10\n"
                                    "    /shu 아산캠 13\n"
                                    "형식으로 입력시 해당역, 시간에 맞는 시간표를 보내드립니다.\n"
                                    "도착 시간에 대한 정보는 나오지 않습니다.\n"
                                    "전체 시간표를 원하신다면 /shuall 을 입력해주세요")
                                    
# 데이터 예시
data_shuttle_schedule = {
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
    },
    # 다른 역의 데이터 추가 가능
}

# 특정 시간에 맞는 표 형식의 셔틀버스 시간표 생성 함수
def get_shuttle_schedule_table(location, hour):
    if location in data_shuttle_schedule and hour in data_shuttle_schedule[location]:
        times = data_shuttle_schedule[location][hour]
        header = f"{location} {hour}시 출발 시간표"
        separator = "-" * len(header)
        rows = [header, separator]
        
        # 각 시간을 표 형식으로 추가
        for time in times:
            rows.append(f"{hour}시 {time} 출발")
        
        return "\n".join(rows)
    else:
        return "해당 시간에 대한 셔틀버스 정보가 없습니다."

# /shu 커맨드 핸들러 - 완
async def shu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        message = ' '.join(context.args)
        split_message = message.split()

        # 명령어 형식 확인
        if len(split_message) == 2:
            location, hour = split_message
            table_text = get_shuttle_schedule_table(location, hour)
            await update.message.reply_text(f"```\n{table_text}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text("형식에 맞게 다시 입력해 주세요.\nex) /shu 아산캠 8")
    else:
        await update.message.reply_text("형식에 맞게 다시 입력해 주세요.\nex) /shu 아산캠 8")

# /shuall 데이터 준비 - 완
data_shuall_asancamp = [
    ["", "", "아산캠 출발", "시간", "", "", "", "", ""],
    ["07시", 45, "<=", "첫차입니다.", "", "", "", "", ""],
    ["08시", 00, 15, 30, 45, "", "", "", ""],
    ["09시", 00, 10, 15, 25, 30, 40, 45, 55],
    ["10시", 00, 10, 15, 25, 30, 45, 55, ""],
    ["11시", 00, 20, 30, 40, 55, "", "", ""],
    ["12시", 00, 20, 30, 40, 55, "", "", ""],
    ["13시", 00, 20, 30, 40, 55, "", "", ""],
    ["14시", 00, 10, 15, 25, 30, 40, 45, 55],
    ["15시", 00, 10, 15, 25, 30, 40, 50, ""],
    ["16시", 00, 10, 15, 25, 30, 40, 45, 55],
    ["17시", 00, 10, 15, 25, 30, 45, "", ""],
    ["18시", 00, 15, 30, 45, "", "", "", ""],
    ["19시", 00, 25, 30, "", "", "", "", ""],
    ["20시", 00, 30, 55, "", "", "", "", ""],
    ["21시", 00, "<=", "막차입니다.", "", "", "", "", ""]
]

# 표 헤더와 줄 맞춤을 위한 구분선 출력
def shuall_asancamp():
    header = "{:<3} {:<3} {:<3} {:<3} {:<3} {:<3} {:<3} {:<3}".format(data_shuall_asancamp[0][0], data_shuall_asancamp[0][1], data_shuall_asancamp[0][2],
                                                                      data_shuall_asancamp[0][3], data_shuall_asancamp[0][4], data_shuall_asancamp[0][5],
                                                                      data_shuall_asancamp[0][6], data_shuall_asancamp[0][7], data_shuall_asancamp[0][8])
    separator = "-" * len(header)
    rows = [header, separator]
    
    for row in data_shuall_asancamp[1:]: # 데이터 행 출력
        rows.append("{:<3} {:<3} {:<3} {:<3} {:<3} {:<3} {:<3} {:<3}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    return "\n".join(rows)

# /shuall 커맨드 핸들러 - 완
async def shuall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shuall_text = shuall_asancamp()
    await update.message.reply_text("현재 아산캠 -> 천안캠 방면 출발 시간표만 출력됩니다\n"
                                    "추후에 더 많은 기능을 지원하겠습니다.\n"
                                    f"```\n{shuall_text}\n```", parse_mode="Markdown")

# 메인 함수
def main():
    # Application 생성 및 토큰 설정
    app = Application.builder().token(TOKEN).build()

    # 커맨드 핸들러 추가
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("shuttle", shuttle_command))
    app.add_handler(CommandHandler("shu", shu))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("cominfo", cominfo_command))
    app.add_handler(CommandHandler("shuall", shuall_command))


    # 봇 시작
    app.run_polling()

if __name__ == '__main__':
    main()