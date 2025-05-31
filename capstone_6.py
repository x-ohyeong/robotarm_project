import tkinter as tk
from tkinter import messagebox
import numpy as np
import webbrowser

# 비율 기반 링크 길이 및 질량 분포
LENGTH_RATIOS = [0.10, 0.18, 0.22, 0.20, 0.15, 0.15]
MASS_RATIOS = [0.08, 0.15, 0.22, 0.25, 0.15, 0.15]

# 링크 길이 추천 함수
def recommend_link_lengths(width_cm, depth_cm, height_cm):
    total_range = (width_cm ** 2 + depth_cm ** 2) ** 0.5 + height_cm
    effective_range = total_range * 0.9
    return [round(effective_range * r, 1) for r in LENGTH_RATIOS]

# 링크 질량 분배 함수
def estimate_link_masses(total_mass_kg):
    return [round(total_mass_kg * r, 2) for r in MASS_RATIOS]

# 조인트별 토크 계산

def calculate_joint_torques(link_lengths_cm, link_masses_kg):
    g = 9.81
    torques = []
    for j in range(6):
        t = 0
        for i in range(j, 6):
            r = sum(link_lengths_cm[j:i+1]) / 100  # cm -> m
            m = link_masses_kg[i]
            t += m * g * r
        torques.append(round(t, 2))
    return torques

# 감속비 및 부하 계산
def determine_reduction_ratio(torque):
    return 10 if torque < 5 else 30 if torque < 10 else 50

def determine_load_condition(torque, reduction_ratio):
    return round(torque * reduction_ratio * 1.2, 2)

# 모터 추천 및 링크 반환
def recommend_motor(torque):
    if torque < 5:
        return "소형 서보모터", "https://www.navimro.com/g/357926/?utm_source=naver&utm_medium=naver_shop&n_media=27758&n_query=%EC%86%8C%ED%98%95%EC%84%9C%EB%B3%B4%EB%AA%A8%ED%84%B0&n_rank=1&n_ad_group=grp-a001-02-000000017409163&n_ad=nad-a001-02-000000236425372&n_campaign_type=2&n_mall_id=navimro&n_mall_pid=357926&n_ad_group_type=2&n_match=3&NaPm=ct%3Dmb3cdqw2%7Cci%3DER8e8e44a4-393a-11f0-bc15-c2a275d5383e%7Ctr%3Dpla%7Chk%3D9c26710947e233df1dcf403a9528aa0384950185%7Cnacn%3DKz32BgwxPnpm"
    elif torque < 10:
        return "중형 서보모터", "https://smartstore.naver.com/medium-servo"
    else:
        return "대형 서보모터", "https://smartstore.naver.com/high-torque-servo"

# 링크 열기 함수
def open_link(event, url):
    webbrowser.open_new(url)

# 기존 링크 제거 후 새로 생성
def update_links(links):
    for lbl in link_labels:
        lbl.destroy()
    link_labels.clear()
    for i, url in enumerate(links):
        lbl = tk.Label(root, text=f"🔗 Joint {i+1} 모터 링크", fg="blue", cursor="hand2", font=("Arial", 9, "underline"))
        lbl.pack()
        lbl.bind("<Button-1>", lambda e, u=url: open_link(e, u))
        link_labels.append(lbl)

# 추천 실행
def run_recommendation():
    try:
        w = float(entry_width.get())
        d = float(entry_depth.get())
        h = float(entry_height.get())
        m = float(entry_mass.get())

        lengths = recommend_link_lengths(w, d, h)
        masses = estimate_link_masses(m)
        torques = calculate_joint_torques(lengths, masses)

        result_lines = ["[📏 링크 길이 추천]"]
        result_lines += [f"Link {i+1}: {lengths[i]} cm, 질량 추정: {masses[i]} kg" for i in range(6)]
        result_lines.append("\n[🧮 조인트별 토크 및 모터 추천]")

        motor_links.clear()

        for i in range(6):
            torque = torques[i]
            ratio = determine_reduction_ratio(torque)
            load = determine_load_condition(torque, ratio)
            motor, link = recommend_motor(torque)
            result_lines.append(
                f"Joint {i+1}: 토크 {torque:.2f} Nm | 감속비 {ratio}:1 | 부하 {load:.2f} Nm\n↳ {motor}"
            )
            motor_links.append(link)

        result_label.config(text="\n".join(result_lines), fg="darkgreen")
        update_links(motor_links)

    except Exception as e:
        messagebox.showerror("입력 오류", f"숫자를 정확히 입력하세요.\n\n{e}")

# GUI 시작
root = tk.Tk()
root.title("🦾 공간 기반 조인트별 모터 추천 GUI")
root.geometry("620x650")

# 입력 영역
tk.Label(root, text="📐 공간 크기 및 무게 입력 (cm, kg)").pack(pady=(10, 2))
frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="가로(Width):").grid(row=0, column=0)
entry_width = tk.Entry(frame)
entry_width.grid(row=0, column=1)

tk.Label(frame, text="세로(Depth):").grid(row=1, column=0)
entry_depth = tk.Entry(frame)
entry_depth.grid(row=1, column=1)

tk.Label(frame, text="높이(Height):").grid(row=2, column=0)
entry_height = tk.Entry(frame)
entry_height.grid(row=2, column=1)

tk.Label(frame, text="물건 총 무게(kg):").grid(row=3, column=0, pady=(10, 0))
entry_mass = tk.Entry(frame)
entry_mass.grid(row=3, column=1, pady=(10, 0))

tk.Button(root, text="▶️ 모터 추천 실행", command=run_recommendation, bg="blue", fg="white").pack(pady=10)

# 결과 출력
tk.Label(root, text="🔎 결과 요약").pack()
result_label = tk.Label(root, text="", justify="left", font=("Courier", 10), wraplength=550)
result_label.pack(pady=5)

# 하이퍼링크 링크 라벨들
link_labels = []
motor_links = []

root.mainloop()
