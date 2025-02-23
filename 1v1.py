import streamlit as st
import pandas as pd
import random
import time

# -------------------------------------------------------------
# 1) ฟังก์ชันโหลดรายชื่อตัวละครจาก CSV ด้วย st.cache_data
# -------------------------------------------------------------
@st.cache_data
def load_characters(csv_file, column_name="Name"):
    df = pd.read_csv(csv_file)
    if column_name not in df.columns:
        st.error(f"ไม่พบคอลัมน์ '{column_name}' ใน CSV")
        return []
    return df[column_name].tolist()

# -------------------------------------------------------------
# 2) ฟังก์ชันสำหรับแสดงรายชื่อตัวละครเป็นกรอบ (box) สีเข้ม
# -------------------------------------------------------------
def display_characters_in_box(characters, title="Characters Selected"):
    """
    แสดงรายชื่อ 'characters' ในกรอบ (box) โดยใช้ <br> ขึ้นบรรทัด
    ปรับสีเข้ม (Dark) เพื่อไม่ให้กลืนกับธีมมืด
    """
    if not characters:
        st.warning("No characters to display.")
        return

    st.markdown(f"#### {title}")

    lines = ""
    for c in characters:
        lines += f"{c}<br>"

    html_content = f"""
    <div style='
        background-color:#444;    /* พื้นหลังสีเทาเข้ม */
        color:#fff;               /* ตัวอักษรสีขาว */
        padding:20px;
        border:1px solid #555;    /* ขอบสีเทาเข้ม */
        border-radius:10px;
        margin-bottom:20px;
    '>
      {lines}
    </div>
    """

    st.markdown(html_content, unsafe_allow_html=True)

# -------------------------------------------------------------
# 3) ฟังก์ชันสร้าง "card" สำหรับแสดงผลสุ่มแบบตัวใหญ่
# -------------------------------------------------------------
def display_card(content, bg_color="#007bff", font_size="60px"):
    return f"""
    <div style='
        font-size:{font_size};
        text-align:center;
        color:#fff;
        background-color:{bg_color};
        padding:20px;
        margin:20px auto;
        border:4px solid #333;
        border-radius:10px;
        width:60%;
    '>
        {content}
    </div>
    """

# -------------------------------------------------------------
# 4) ฟังก์ชันรีเซ็ตการแข่งขัน (Reset Tournament)
#    ปรับแก้ให้ล้างทุกตัวแปรและพยายามเรียก st.experimental_rerun()
#    หากใช้งานไม่ได้ จะแจ้งให้ผู้ใช้รีเฟรชหน้าจอด้วยตนเอง
# -------------------------------------------------------------
def reset_tournament():
    st.session_state["names_confirmed"] = False
    st.session_state["competitor1_name"] = ""
    st.session_state["competitor2_name"] = ""
    st.session_state["picks_confirmed"] = False
    st.session_state["p1_chars"] = []
    st.session_state["p2_chars"] = []
    st.session_state["all_chars"] = []
    st.session_state["pool"] = []
    st.session_state["results"] = {}
    st.session_state["round_winners"] = {}
    st.session_state["current_round"] = 0
    try:
        st.experimental_rerun()
    except Exception:
        st.write("กรุณารีเฟรชหน้าจอด้วยตัวเอง")

# -------------------------------------------------------------
# 5) กำหนดค่าเริ่มต้นใน session state
# -------------------------------------------------------------
if "names_confirmed" not in st.session_state:
    st.session_state["names_confirmed"] = False
if "competitor1_name" not in st.session_state:
    st.session_state["competitor1_name"] = ""
if "competitor2_name" not in st.session_state:
    st.session_state["competitor2_name"] = ""

if "picks_confirmed" not in st.session_state:
    st.session_state["picks_confirmed"] = False
if "p1_chars" not in st.session_state:
    st.session_state["p1_chars"] = []
if "p2_chars" not in st.session_state:
    st.session_state["p2_chars"] = []
if "all_chars" not in st.session_state:
    st.session_state["all_chars"] = []
if "pool" not in st.session_state:
    st.session_state["pool"] = []
if "results" not in st.session_state:
    st.session_state["results"] = {}
if "round_winners" not in st.session_state:
    st.session_state["round_winners"] = {}
if "current_round" not in st.session_state:
    st.session_state["current_round"] = 0

# -------------------------------------------------------------
# 6) โหลดรายชื่อตัวละครจาก CSV
# -------------------------------------------------------------
characters_list = load_characters("ROV_Heroes - Combined_AOV_Heroes.csv", column_name="Name")

# -------------------------------------------------------------
# ส่วนหัวของแอป
# -------------------------------------------------------------
st.title("1v1 Tournament")
st.write("หลังรีเฟรชทัวนาเม้นต์ จะกลับไปกรอกชื่อผู้เข้าแข่งขันใหม่ทันที")

# -------------------------------------------------------------
# 7) กรอกชื่อผู้เข้าแข่งขัน (ถ้ายังไม่กรอก)
# -------------------------------------------------------------
if not st.session_state["names_confirmed"]:
    st.subheader("กรอกชื่อผู้เข้าแข่งขัน")
    comp1 = st.text_input("ชื่อผู้เข้าแข่งขัน 1", key="comp1")
    comp2 = st.text_input("ชื่อผู้เข้าแข่งขัน 2", key="comp2")
    if st.button("ยืนยันชื่อผู้เข้าแข่งขัน"):
        if comp1 and comp2:
            st.session_state["competitor1_name"] = comp1
            st.session_state["competitor2_name"] = comp2
            st.session_state["names_confirmed"] = True
            st.success("ยืนยันชื่อผู้เข้าแข่งขันเรียบร้อย!")
        else:
            st.error("กรุณากรอกชื่อผู้เข้าแข่งขันทั้งสองฝ่าย")
    st.stop()

# -------------------------------------------------------------
# 8) เลือกตัวละคร (แต่ละฝ่ายเลือก 5 ตัว)
# -------------------------------------------------------------
if not st.session_state["picks_confirmed"]:
    st.subheader("เลือกตัวละคร (แต่ละฝ่ายเลือก 5 ตัว)")
    st.write(f"**{st.session_state['competitor1_name']}** เลือกตัวละคร:")
    p1_selection = st.multiselect("Player 1 ตัวเลือก", characters_list, key="p1")
    
    st.write(f"**{st.session_state['competitor2_name']}** เลือกตัวละคร:")
    p2_selection = st.multiselect("Player 2 ตัวเลือก", characters_list, key="p2")
    
    if st.button("ยืนยันการเลือกตัวละคร"):
        if len(p1_selection) == 5 and len(p2_selection) == 5:
            st.session_state["p1_chars"] = p1_selection
            st.session_state["p2_chars"] = p2_selection
            st.session_state["all_chars"] = p1_selection + p2_selection
            st.session_state["pool"] = st.session_state["all_chars"].copy()
            st.session_state["picks_confirmed"] = True
            st.session_state["current_round"] = 1
            st.success("ยืนยันการเลือกตัวละครเรียบร้อย!")
        else:
            st.error("กรุณาเลือกตัวละครให้ครบ 5 ตัวสำหรับแต่ละฝ่าย")
    st.stop()

# -------------------------------------------------------------
# 9) แสดงรายชื่อที่เลือกทั้งหมด (10 ตัว) ในกรอบ (box) สีเข้ม
# -------------------------------------------------------------
st.subheader("ตัวละครที่เลือกทั้งหมด (10 ตัว)")
display_characters_in_box(st.session_state["all_chars"], title="Selected Characters")

# -------------------------------------------------------------
# 10) แสดงผลการสุ่มในแต่ละรอบ (ถ้ายังไม่มีให้บอกว่ายังไม่สุ่ม)
# -------------------------------------------------------------
st.subheader("ผลการสุ่มในแต่ละรอบ (Best of 3):")
for rnd in ["1", "2", "3"]:
    chosen_char = st.session_state["results"].get(rnd, None)
    winner = st.session_state["round_winners"].get(rnd, None)
    if chosen_char is None:
        st.markdown(display_card(f"รอบที่ {rnd}: ยังไม่สุ่ม", bg_color="#6c757d", font_size="40px"), unsafe_allow_html=True)
    else:
        text_to_show = f"รอบที่ {rnd}: {chosen_char}"
        if winner:
            text_to_show += f" - ชนะโดย {winner}"
            st.markdown(display_card(text_to_show, bg_color="#28a745", font_size="40px"), unsafe_allow_html=True)
        else:
            st.markdown(display_card(text_to_show + " - (ยังไม่ได้เลือกผู้ชนะ)", bg_color="#ffc107", font_size="40px"), unsafe_allow_html=True)

# -------------------------------------------------------------
# ฟังก์ชันสำหรับคำนวณคะแนนปัจจุบัน
# -------------------------------------------------------------
def get_current_score():
    score_comp1 = sum(1 for w in st.session_state["round_winners"].values() if w == st.session_state["competitor1_name"])
    score_comp2 = sum(1 for w in st.session_state["round_winners"].values() if w == st.session_state["competitor2_name"])
    return score_comp1, score_comp2

current_round = st.session_state["current_round"]

# -------------------------------------------------------------
# 11) รอบที่ 1
# -------------------------------------------------------------
if current_round == 1:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("รอบที่ 1")

    if "1" not in st.session_state["results"]:
        if st.button("เริ่มสุ่ม รอบที่ 1"):
            placeholder = st.empty()
            for _ in range(20):
                temp_choice = random.choice(st.session_state["pool"])
                placeholder.markdown(display_card(temp_choice), unsafe_allow_html=True)
                time.sleep(0.1)
            final_char = random.choice(st.session_state["pool"])
            st.session_state["results"]["1"] = final_char
            placeholder.markdown(display_card(final_char, bg_color="#17a2b8"), unsafe_allow_html=True)

    if "1" in st.session_state["results"] and "1" not in st.session_state["round_winners"]:
        winner_select = st.radio(
            "เลือกผู้ชนะรอบที่ 1:",
            [st.session_state["competitor1_name"], st.session_state["competitor2_name"]],
            key="winner_select_1"
        )
        if st.button("ยืนยันผู้ชนะรอบ 1"):
            st.session_state["round_winners"]["1"] = winner_select
            st.success(f"บันทึกผู้ชนะรอบที่ 1: {winner_select}")

    if "1" in st.session_state["round_winners"]:
        if st.button("ถัดไป (ไปสู่รอบที่ 2)"):
            chosen = st.session_state["results"]["1"]
            if chosen in st.session_state["pool"]:
                st.session_state["pool"].remove(chosen)
            st.session_state["current_round"] = 2

    st.write("Pool ที่เหลือ:", st.session_state["pool"])

# -------------------------------------------------------------
# 12) รอบที่ 2
# -------------------------------------------------------------
elif current_round == 2:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("รอบที่ 2")
    st.write("Pool ที่เหลือ:", st.session_state["pool"])

    if "2" not in st.session_state["results"]:
        if st.button("เริ่มสุ่ม รอบที่ 2"):
            placeholder = st.empty()
            for _ in range(20):
                temp_choice = random.choice(st.session_state["pool"])
                placeholder.markdown(display_card(temp_choice), unsafe_allow_html=True)
                time.sleep(0.1)
            final_char = random.choice(st.session_state["pool"])
            st.session_state["results"]["2"] = final_char
            placeholder.markdown(display_card(final_char, bg_color="#17a2b8"), unsafe_allow_html=True)

    if "2" in st.session_state["results"] and "2" not in st.session_state["round_winners"]:
        winner_select = st.radio(
            "เลือกผู้ชนะรอบที่ 2:",
            [st.session_state["competitor1_name"], st.session_state["competitor2_name"]],
            key="winner_select_2"
        )
        if st.button("ยืนยันผู้ชนะรอบ 2"):
            st.session_state["round_winners"]["2"] = winner_select
            st.success(f"บันทึกผู้ชนะรอบที่ 2: {winner_select}")

    score_comp1, score_comp2 = get_current_score()
    st.write(f"คะแนน: {st.session_state['competitor1_name']} {score_comp1} - {score_comp2} {st.session_state['competitor2_name']}")

    if score_comp1 == 2 or score_comp2 == 2:
        champion = st.session_state["competitor1_name"] if score_comp1 == 2 else st.session_state["competitor2_name"]
        st.success(f"ผู้ชนะโดยรวม: {champion}")
        if st.button("รีเฟรชทัวนาเม้นต์ (หลังเกมที่ 2)"):
            reset_tournament()
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("รีเฟรชทัวนาเม้นต์"):
                reset_tournament()
        with col2:
            if "2" in st.session_state["round_winners"]:
                if st.button("เกมที่ 3"):
                    chosen = st.session_state["results"]["2"]
                    if chosen in st.session_state["pool"]:
                        st.session_state["pool"].remove(chosen)
                    st.session_state["current_round"] = 3

# -------------------------------------------------------------
# 13) รอบที่ 3
# -------------------------------------------------------------
elif current_round == 3:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("รอบที่ 3")
    st.write("Pool ที่เหลือ:", st.session_state["pool"])

    if "3" not in st.session_state["results"]:
        if st.button("เริ่มสุ่ม รอบที่ 3"):
            placeholder = st.empty()
            for _ in range(20):
                temp_choice = random.choice(st.session_state["pool"])
                placeholder.markdown(display_card(temp_choice), unsafe_allow_html=True)
                time.sleep(0.1)
            final_char = random.choice(st.session_state["pool"])
            st.session_state["results"]["3"] = final_char
            placeholder.markdown(display_card(final_char, bg_color="#17a2b8"), unsafe_allow_html=True)

    if "3" in st.session_state["results"] and "3" not in st.session_state["round_winners"]:
        winner_select = st.radio(
            "เลือกผู้ชนะรอบที่ 3:",
            [st.session_state["competitor1_name"], st.session_state["competitor2_name"]],
            key="winner_select_3"
        )
        if st.button("ยืนยันผู้ชนะรอบที่ 3"):
            st.session_state["round_winners"]["3"] = winner_select
            st.success(f"บันทึกผู้ชนะรอบที่ 3: {winner_select}")

    score_comp1, score_comp2 = get_current_score()
    st.write(f"คะแนนรวม: {st.session_state['competitor1_name']} {score_comp1} - {score_comp2} {st.session_state['competitor2_name']}")

    if score_comp1 >= 2 or score_comp2 >= 2 or ("3" in st.session_state["round_winners"]):
        if score_comp1 > score_comp2:
            st.success(f"ผู้ชนะโดยรวม: {st.session_state['competitor1_name']}")
        elif score_comp2 > score_comp1:
            st.success(f"ผู้ชนะโดยรวม: {st.session_state['competitor2_name']}")
        else:
            st.info("ผลเสมอ")
        
        if st.button("รีเฟรชทัวนาเม้นต์ (หลังเกมที่ 3)"):
            reset_tournament()