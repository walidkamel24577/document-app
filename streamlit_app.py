import streamlit as st
from datetime import datetime, date, time
import sqlite3
import os

# إعداد الصفحة والعنوان
st.set_page_config(page_title="نظام طلب المستندات", layout="wide")
st.markdown("<h2 style='text-align: right; color: #1e3a8a;'>📂 موديول طلبات المستندات والمرفقات</h2>", unsafe_allow_html=True)

# الاتصال التلقائي بقاعدة البيانات وحفظ المرفقات
db = sqlite3.connect("data.db", check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS reqs (id TEXT PRIMARY KEY, title TEXT, dept TEXT, status TEXT, limit_date TEXT, file_name TEXT)")
os.makedirs("all_files", exist_ok=True)

# دالة ذكية لحساب المهلة للمستخدمين
def check_time(limit_str):
    try:
        diff = datetime.strptime(limit_str, "%Y-%m-%d %H:%M") - datetime.now()
        if diff.total_seconds() <= 0: return "❌ انتهت المهلة"
        return f"⏳ متبقي {diff.days} يوم و {diff.seconds // 3600} ساعة" if diff.days > 0 else f"🚨 متبقي {diff.seconds // 3600} ساعة فقط!"
    except: return "غير محدد"

# 1. قسم الإحصائيات العلوية
c_all, c_done, c_wait = st.columns(3)
total_count = db.execute("SELECT COUNT(*) FROM reqs").fetchone()[0]
done_count = db.execute("SELECT COUNT(*) FROM reqs WHERE status='تم الرفع'").fetchone()[0]

c_all.metric("إجمالي الطلبات", total_count)
c_done.metric("تم رفعها (المكتمل)", done_count)
c_wait.metric("بانتظار الرفع", total_count - done_count)

st.markdown("---")

# 2. قسم إضافة طلب جديد (خاص بالمراجع)
st.markdown("### ➕ إضافة طلب مستند جديد")
col_t, col_d, col_dt, col_tm = st.columns(4)
with col_t: r_title = st.text_input("المستند المطلوب:")
with col_d: r_dept = st.text_input("القسم المسؤول:")
with col_dt: r_date = st.date_input("تاريخ الاستحقاق:", value=date.today())
with col_tm: r_time = st.time_input("الوقت:", value=time(12, 0))

if st.button("إضافة الطلب للجدول", type="primary"):
    if r_title and r_dept:
        next_id = f"REQ-0{total_count + 1}" if total_count < 9 else f"REQ-{total_count + 1}"
        full_date = f"{r_date} {r_time.strftime('%H:%M')}"
        db.execute("INSERT INTO reqs VALUES (?, ?, ?, 'لم يتم الرفع', ?, NULL)", (next_id, r_title, r_dept, full_date))
        db.commit()
        st.success("تمت الإضافة!")
        st.rerun()

st.markdown("---")

# 3. عرض الجدول ورفع الملفات (خاص بالمستخدمين)
st.markdown("### 📋 جدول المرفقات الحالي")
rows = db.execute("SELECT * FROM reqs").fetchall()

if rows:
    for row in rows:
        with st.container(border=True):
            td1, td2, td3, td4 = st.columns([1, 3, 2, 3])
            td1.markdown(f"**{row[0]}**")
            td2.markdown(f"📄 **{row[1]}**  \n🏢 القسم: {row[2]}")
            
            # حساب وعرض المدة المتبقية للمستخدم
            time_left = "✔️ مكتمل" if row[3] == "تم الرفع" else check_time(row[4])
            td3.markdown(f"**الحالة:** {row[3]}  \n`{time_status}`")
            
            # زر رفع الملف المباشر للمستخدم
            if row[3] == "لم يتم الرفع":
                u_file = td4.file_uploader("رفع الملف", key=row[0], label_visibility="collapsed")
                if u_file:
                    with open(os.path.join("all_files", f"{row[0]}_{u_file.name}"), "wb") as f:
                        f.write(u_file.getbuffer())
                    db.execute("UPDATE reqs SET status='تم الرفع', file_name=? WHERE id=?", (u_file.name, row[0]))
                    db.commit()
                    st.rerun()
            else:
                td4.success(f"📁 تم حفظ: {row[5]}")
else:
    st.info("لا توجد طلبات مستندات حالياً.")
