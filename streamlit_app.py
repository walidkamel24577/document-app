python

import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os

# 1. إعداد الصفحة والعنوان لتكون عريضة ومنظمة
st.set_page_config(page_title="موديول طلبات المستندات والمرفقات", layout="wide")

# تطبيق اتجاه النص العربي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Cairo', system-ui, sans-serif !important;
        text-align: right;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

# 2. الاتصال التلقائي بقاعدة البيانات وإنشاء الجداول
db = sqlite3.connect("secure_documents_final.db", check_same_thread=False)
db.execute("""
    CREATE TABLE IF NOT EXISTS reqs (
        id TEXT PRIMARY KEY, 
        title TEXT, 
        dept TEXT, 
        status TEXT, 
        limit_date TEXT, 
        file_name TEXT
    )
""")
os.makedirs("all_files", exist_ok=True)

# 3. بيانات تسجيل الدخول الافتراضية الصالحة للنظام
USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "مراجع"},
    "user_finance": {"password": "finance123", "role": "مستخدم", "dept": "المالية"},
    "user_hr": {"password": "hr123", "role": "مستخدم", "dept": "الموارد البشرية"}
}

# 4. دالة ذكية لحساب المهلة الزمنية وتفعيل قفل الحساب تلقائياً للمتأخرين
def check_time_and_lock(limit_str, status):
    try:
        limit_dt = datetime.strptime(limit_str, "%Y-%m-%d %H:%M")
        diff = limit_dt - datetime.now()
        
        if diff.total_seconds() <= 0:
            if status == "لم يتم الرفع":
                return "🚨 انتهت المهلة (الحساب مقفل)", True, 0
            else:
                return "✔️ مكتمل (تم الرفع قبل القفل)", False, 100
        
        days = diff.days
        hours = diff.seconds // 3600
        
        if days > 0:
            pct = 85 if days >= 3 else 50
            return f"⏳ متبقي {days} يوم و {hours} ساعة", False, pct
        else:
            return f"🚨 متبقي {hours} ساعة فقط!", False, 20
    except:
        return "غير محدد", False, 100

# 5. إدارة الجلسة ونظام تسجيل الدخول الحامي للمنصة
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["dept"] = ""

if not st.session_state["logged_in"]:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; font-weight: 700;'>🔐 تسجيل الدخول إلى النظام</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username_input = st.text_input("اسم المستخدم:")
        password_input = st.text_input("كلمة المرور:", type="password")
        submit_login = st.form_submit_button("دخول للنظام", use_container_width=True)
        
        if submit_login:
            if username_input in USER_CREDENTIALS and USER_CREDENTIALS[username_input]["password"] == password_input:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_input
                st.session_state["role"] = USER_CREDENTIALS[username_input]["role"]
                st.session_state["dept"] = USER_CREDENTIALS[username_input].get("dept", "")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
    st.stop()

# 6. هيدر التطبيق الجانبي للمستخدم الحالي
st.sidebar.markdown(f"### 👋 مرحباً، {st.session_state['username']}")
st.sidebar.markdown(f"**الصلاحية:** {st.session_state['role']}")
if st.session_state["dept"]:
    st.sidebar.markdown(f"**القسم:** {st.session_state['dept']}")
if st.sidebar.button("تسجيل الخروج", type="secondary", use_container_width=True):
    st.session_state["logged_in"] = False
    st.rerun()

# 7. الهيدر العلوي وعناوين البرنامج الرئيسية
st.title("📄 موديول طلبات المستندات والمرفقات")
st.caption("منصة التنسيق والتدقيق المستندي بين فريق المراجعة والشركة")

# 8. صندوق الإرشادات والملاحظات
st.info("""
• خاص بالمراجع: اكتب الطلب أدناه وحدد عدد أيام المهلة واضغط إضافة الطلب للجدول ليظهر فوراً.
• خاص بالعميل: اضغط على زر رفع الملفات لرفع المستند المطلوب مباشرة قبل انتهاء المهلة وتجميد الحساب.
""")

# 9. حساب الإحصائيات الحية من قاعدة البيانات
total_count = db.execute("SELECT COUNT(*) FROM reqs").fetchone()[0]
done_count = db.execute("SELECT COUNT(*) FROM reqs WHERE status='تم الرفع'").fetchone()[0]
wait_count = total_count - done_count

# عرض الإحصائيات الثلاثية بشكل منظم وبصري ممتاز
c_wait, c_done, c_all = st.columns(3)
c_all.metric(label="إجمالي الطلبات", value=total_count)
c_done.metric(label="تم رفعها (المكتمل)", value=done_count)
c_wait.metric(label="بانتظار الرفع (المتبقي)", value=wait_count)

st.markdown("---")

# 10. واجهة المراجع (ADMIN) - إضافة وحذف وإعادة ضبط
if st.session_state["role"] == "مراجع":
    
    if st.sidebar.button("🧹 مسح كافة الطلبات وإعادة الضبط", use_container_width=True):
        db.execute("DELETE FROM reqs")
        db.commit()
        st.rerun()

    st.markdown("### ➕ إضافة طلب جديد (خاص بالمراجع)")
    with st.form("add_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            r_title = st.text_input("المستند المطلوب:", placeholder="مثال: ميزان المراجعة لعام 2025")
        with f2:
            r_dept = st.selectbox("القسم المسؤول بالشركة:", ["المالية", "الموارد البشرية"])
        with f3:
            r_days = st.number_input("المهلة (عدد أيام العمل المتاحة):", min_value=1, max_value=30, value=3)
            
        sub_btn = st.form_submit_button("إضافة الطلب للجدول", use_container_width=True)
        
        if sub_btn and r_title:
            next_id = f"REQ-0{total_count + 1}" if total_count < 9 else f"REQ-{total_count + 1}"
            calculated_deadline = (datetime.now() + timedelta(days=int(r_days))).strftime("%Y-%m-%d %H:%M")
            db.execute("INSERT INTO reqs VALUES (?, ?, ?, 'لم يتم الرفع', ?, NULL)", (next_id, r_title, r_dept, calculated_deadline))
            db.commit()
            st.rerun()

st.markdown("---")

# 11. عرض جدول المرفقات الحالي بتنسيق الأعمدة المتطابقة والنظيفة
st.markdown("### 📋 جدول المرفقات الحالي")

# رؤوس الأعمدة الرئيسية للجدول
h1, h2, h3, h4, h5, h6 = st.columns([1, 2.5, 1.5, 1.5, 2, 1.5])
h1.markdown("**رقم الطلب**")
h2.markdown("**المستند المطلوب**")
h3.markdown("**القسم المسؤول**")
h4.markdown("**حالة الطلب**")
h5.markdown("**المهلة الزمنية المتبقية**")
h6.markdown("**العمليات / المرفق**")
st.markdown("<hr style='margin: 8px 0; border-color: #1e3a8a; border-width: 2px;' />", unsafe_allow_html=True)

# جلب الصفوف وتصفيتها حسب الصلاحيات لقاعدة البيانات
if st.session_state["role"] == "مراجع":
    rows = db.execute("SELECT * FROM reqs").fetchall()
else:
    rows = db.execute("SELECT * FROM reqs WHERE dept=?", (st.session_state["dept"],)).fetchall()

if rows:
    for row in rows:
        r_id, r_title, r_dept, r_status, r_limit, r_file = row
        time_status, is_locked, pct = check_time_and_lock(r_limit, r_status)
        
        t1, t2, t3, t4, t5, t6 = st.columns([1, 2.5, 1.5, 1.5, 2, 1.5])
        
        t1.markdown(f" `{r_id}` ")
        t2.markdown(f"**{r_title}**")
        t3.markdown(r_dept)
        
        # عرض حالة الطلب الملونة
        if r_status == "تم الرفع":
            t4.success("🟢 تم الرفع")
        else:
            t4.error("🔴 لم يتم الرفع")
            
        # عرض شريط تقدم المدة والوقت المتبقي للمستخدمين
        with t5:
            st.markdown(f"<span style='font-size:12px;'>{time_status}</span>", unsafe_allow_html=True)
            st.progress(pct / 100)
            
        # قسم الرفع أو الحذف الفردي الآمن
        with t6:
            if st.session_state["role"] == "مراجع":
                if st.button("🗑️ إلغاء", key=f"del_{r_id}", use_container_width=True):
                    db.execute("DELETE FROM reqs WHERE id=?", (r_id,))
                    db.commit()
                    st.rerun()
            else:
                if r_status == "تم الرفع":
                    st.info(f"📁 {r_file}")
                elif is_locked:
                    st.error("🔒 مقفل")
                else:
                    u_file = st.file_uploader("رفع الملف", key=f"up_{r_id}", label_visibility="collapsed")
                    if u_file:
                        file_path = os.path.join("all_files", f"{r_id}_{u_file.name}")
                        with open(file_path, "wb") as f:
                            f.write(u_file.getbuffer())
                        db.execute("UPDATE reqs SET status='تم الرفع', file_name=? WHERE id=?", (u_file.name, r_id))
                        db.commit()
                        st.rerun()
        st.markdown("<hr style='margin: 4px 0; border-color: #f3f4f6;' />", unsafe_allow_html=True)
else:
    st.info("لا توجد طلبات معلقة حالياً.")

يُرجى استخدام الرمز البرمجي بحذر.
