python

import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os

# 1. إعداد الصفحة والعنوان لتكون عريضة ومناسبة للتصميم الأصلي
st.set_page_config(page_title="موديول طلبات المستندات والمرفقات", layout="wide")

# 2. استدعاء الخطوط وتنسيق الألوان المتطابقة مع الواجهة الأصلية الفاخرة
st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', system-ui, sans-serif !important;
        text-align: right;
        direction: rtl;
    }
    div[data-testid="stForm"] {
        border: 1px solid #e5e7eb !important;
        border-radius: 0.5rem !important;
        background-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. الاتصال التلقائي بقاعدة البيانات السحابية وإنشاء الجداول
db = sqlite3.connect("secure_documents_v4.db", check_same_thread=False)
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

# 4. بيانات تسجيل الدخول الافتراضية الصالحة للنظام
USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "مراجع"},
    "user_finance": {"password": "finance123", "role": "مستخدم", "dept": "المالية"},
    "user_hr": {"password": "hr123", "role": "مستخدم", "dept": "الموارد البشرية"}
}

# 5. دالة ذكية لحساب المهلة الزمنية وتفعيل قفل الحساب تلقائياً للمستخدمين
def check_time_and_lock(limit_str, status):
    try:
        limit_dt = datetime.strptime(limit_str, "%Y-%m-%d %H:%M")
        diff = limit_dt - datetime.now()
        
        if diff.total_seconds() <= 0:
            if status == "لم يتم الرفع":
                return "🚨 انتهت المهلة (الحساب مقفل)", True, 0, "red"
            else:
                return "✔️ مكتمل (تم الرفع قبل القفل)", False, 100, "green"
        
        days = diff.days
        hours = diff.seconds // 3600
        
        if days > 0:
            color = "green" if days >= 3 else "orange"
            pct = 85 if days >= 3 else 50
            return f"⏳ متبقي {days} يوم و {hours} ساعة", False, pct, color
        else:
            return f"🚨 متبقي {hours} ساعة فقط!", False, 20, "red"
    except:
        return "غير حدد", False, 100, "gray"

# 6. إدارة الجلسة ونظام تسجيل الدخول الحامي للمنصة
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["dept"] = ""

if not st.session_state["logged_in"]:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns()
    with col_l2:
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
                <span class="material-symbols-outlined" style="font-size: 48px; color: #1e3a8a;">lock</span>
                <h2 style='color: #1e3a8a; margin-top: 10px; font-weight: 700;'>تسجيل الدخول إلى النظام</h2>
            </div>
        """, unsafe_allow_html=True)
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

# 7. هيدر التطبيق الجانبي للمستخدم الحالي
st.sidebar.markdown(f"### 👋 مرحباً، {st.session_state['username']}")
st.sidebar.markdown(f"**الصلاحية:** {st.session_state['role']}")
if st.session_state["dept"]:
    st.sidebar.markdown(f"**القسم:** {st.session_state['dept']}")
if st.sidebar.button("تسجيل الخروج", type="secondary", use_container_width=True):
    st.session_state["logged_in"] = False
    st.rerun()

# 8. تصميم الهيدر العلوي الأصلي المتطابق بصرياً
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e5e7eb; padding-bottom: 16px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px; float: right;">
            <div style="background-color: #1e3a8a; color: white; padding: 8px; border-radius: 6px; display: flex; align-items: center;">
                <span class="material-symbols-outlined" style="font-size: 28px;">description</span>
            </div>
            <div>
                <h1 style="font-size: 22px; font-weight: 700; color: #1e3a8a; margin: 0;">مواجهة طلبات المستندات والمرفقات <span style="font-size: 14px; font-weight: 400; color: #6b7280;">(نسخة مصغرة)</span></h1>
                <p style="font-size: 12px; color: #9ca3af; margin: 4px 0 0 0;">منصة التنسيق والتدقيق المستندي بين فريق المراجعة والشركة</p>
            </div>
        </div>
        <div style="clear: both;"></div>
    </div>
""", unsafe_allow_html=True)

# 9. صندوق الإرشادات والملاحظات الأصلي بالألوان الخضراء
st.markdown("""
    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; margin-bottom: 24px; font-size: 13px; line-height: 1.6; text-align: right;">
        <p style="color: #166534; font-weight: 600; margin: 0 0 4px 0;">• خاص بالمراجع: <span style="font-weight: 400; color: #4b5563;">اكتب الطلب أدناه وحدد "عدد أيام المهلة للمستخدم" واضغط "إضافة الطلب للجدول" ليظهر فوراً.</span></p>
        <p style="color: #166534; font-weight: 600; margin: 0;">• خاص بالعميل: <span style="font-weight: 400; color: #4b5563;">اضغط على زر (Browse files) لرفع المستند المطلوب مباشرة وسيتم تحديث الحالة تلقائياً إلى "تم الرفع".</span></p>
    </div>
""", unsafe_allow_html=True)

# 10. حساب الإحصائيات الحية وعرض كروت الإحصائيات الثلاثية الأصلية الملونة
total_count = db.execute("SELECT COUNT(*) FROM reqs").fetchone()[0]
done_count = db.execute("SELECT COUNT(*) FROM reqs WHERE status='تم الرفع'").fetchone()[0]
wait_count = total_count - done_count

st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-bottom: 32px; text-align: center;">
        <div style="border: 1px solid #fee2e2; border-radius: 8px; padding: 16px; background-color: #fef2f2;">
            <div style="font-size: 13px; color: #dc2626; font-weight: 600;">بانتظار الرفع (المتبقي)</div>
            <div style="font-size: 32px; font-weight: 700; color: #dc2626; margin-top: 4px;">{wait_count}</div>
        </div>
        <div style="border: 1px solid #dcfce7; border-radius: 8px; padding: 16px; background-color: #f0fdf4;">
            <div style="font-size: 13px; color: #16a34a; font-weight: 600;">تم رفعها (المكتمل)</div>
            <div style="font-size: 32px; font-weight: 700; color: #16a34a; margin-top: 4px;">{done_count}</div>
        </div>
        <div style="border: 1px solid #e0f2fe; border-radius: 8px; padding: 16px; background-color: #f0f9ff;">
            <div style="font-size: 13px; color: #0369a1; font-weight: 600;">إجمالي الطلبات</div>
            <div style="font-size: 32px; font-weight: 700; color: #0369a1; margin-top: 4px;">{total_count}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- واجهة المراجع (ADMIN) ---
if st.session_state["role"] == "مراجع":
    
    # زر إعادة ضبط النظام ومسح كافة الطلبات
    if st.sidebar.button("🧹 مسح كافة الطلبات وإعادة الضبط", use_container_width=True):
        db.execute("DELETE FROM reqs")
        db.commit()
        st.rerun()

    # تصميم فورم إضافة طلب جديد المتطابق بالكامل مع المظهر الأصلي
    st.markdown("""
        <h3 style="font-size: 15px; font-weight: 700; color: #1e3a8a; margin-bottom: 12px; display: flex; align-items: center; gap: 4px;">
            <span class="material-symbols-outlined" style="font-size: 18px;">add_circle</span> إضافة طلب جديد (خاص بالمراجع)
        </h3>
    """, unsafe_allow_html=True)
    
    with st.form("add_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            r_title = st.text_input("المستند المطلوب:", placeholder="مثال: ميزان المراجعة لعام 2025")
        with f2:
            r_dept = st.selectbox("القسم المسؤول بالشركة:", ["المالية", "الموارد البشرية"])
        with f3:
            r_days = st.number_input("المهلة (عدد أيام العمل المتاحة):", min_value=1, max_value=30, value=3)
            
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        sub_btn = st.form_submit_button("إضافة الطلب للجدول")
        
        if sub_btn and r_title:
            next_id = f"REQ-0{total_count + 1}" if total_count < 9 else f"REQ-{total_count + 1}"
            calculated_deadline = (datetime.now() + timedelta(days=int(r_days))).strftime("%Y-%m-%d %H:%M")
            db.execute("INSERT INTO reqs VALUES (?, ?, ?, 'لم يتم الرفع', ?, NULL)", (next_id, r_title, r_dept, calculated_deadline))
            db.commit()
            st.rerun()

st.markdown("---")

# --- عرض جدول المرفقات الرئيسي بالشكل الكحلي الأصلي الفاخر ---
st.markdown("""
    <h3 style="font-size: 15px; font-weight: 700; color: #1e3a8a; margin-bottom: 16px; display: flex; align-items: center; gap: 4px;">

يُرجى استخدام الرمز البرمجي بحذر.
