"""Intake Builder Page — Structured information collection forms."""
import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="信息采集表单 — InsureAI", page_icon="📝", layout="wide")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("📝 信息采集表单 (Intake Builder)")
st.caption("构建结构化信息采集页面，替代非结构化的邮件往返")
st.markdown("---")

tab_create, tab_list = st.tabs(["➕ 创建表单", "📋 已有表单"])

with tab_create:
    st.subheader("创建新的采集表单")

    form_title = st.text_input("表单标题", placeholder="如：车险理赔受理表")
    form_description = st.text_area("表单描述（可选）", placeholder="简要说明此表单的用途")
    insurance_stage = st.selectbox(
        "关联保险环节",
        options=["claims", "new_business", "underwriting", "renewal", "servicing"],
        format_func=lambda x: {"claims": "⚠️ 理赔", "new_business": "📋 新业务", "underwriting": "🔍 核保", "renewal": "📈 续保", "servicing": "🔄 服务"}.get(x, x),
    )

    st.markdown("**表单字段定义：**")

    # Dynamic field builder
    if "intake_fields" not in st.session_state:
        st.session_state.intake_fields = []

    col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 1])
    with col_a:
        field_name = st.text_input("字段名", key="f_name", placeholder="如: claimant_name")
    with col_b:
        field_label = st.text_input("显示标签", key="f_label", placeholder="如: 申请人姓名")
    with col_c:
        field_type = st.selectbox("类型", ["text", "number", "select", "date"], key="f_type")
    with col_d:
        if st.button("➕ 添加", key="add_field"):
            if field_name and field_label:
                st.session_state.intake_fields.append({
                    "name": field_name,
                    "label": field_label,
                    "type": field_type,
                    "required": True,
                    "options": [] if field_type == "select" else None,
                })
                st.rerun()

    # Show current fields
    if st.session_state.intake_fields:
        st.markdown("**已添加的字段：**")
        for i, f in enumerate(st.session_state.intake_fields):
            col1, col2 = st.columns([8, 1])
            with col1:
                st.text(f"• {f['label']} ({f['name']}) — {f['type']}")
            with col2:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.intake_fields.pop(i)
                    st.rerun()

    if st.button("📝 创建表单", type="primary", use_container_width=True):
        if not form_title:
            st.error("请输入表单标题")
        elif not st.session_state.intake_fields:
            st.error("请至少添加一个字段")
        else:
            try:
                resp = requests.post(
                    f"{API_BASE}/api/v1/intake/forms",
                    json={
                        "title": form_title,
                        "description": form_description,
                        "fields": st.session_state.intake_fields,
                        "insurance_stage": insurance_stage,
                    },
                    timeout=10,
                )
                if resp.ok:
                    data = resp.json()
                    st.success(f"✅ 表单创建成功！")
                    st.code(f"分享链接: {API_BASE}/api/v1/intake/forms/{data['form_id']}")
                    st.session_state.intake_fields = []  # Reset
                else:
                    st.error(f"创建失败: {resp.status_code}")
            except Exception as e:
                st.error(f"请求失败: {e}")

with tab_list:
    st.subheader("已创建的表单")
    try:
        resp = requests.get(f"{API_BASE}/api/v1/intake/forms", timeout=5)
        if resp.ok:
            forms = resp.json().get("forms", [])
            if not forms:
                st.info("还没有创建任何表单")
            else:
                for form in forms:
                    with st.expander(f"📝 {form['title']} ({form['insurance_stage']})"):
                        st.markdown(f"**描述**: {form.get('description', 'N/A')}")
                        st.markdown(f"**链接**: `{API_BASE}/api/v1/intake/forms/{form['id']}`")
                        st.markdown(f"**提交数**: {len(form.get('submissions', []))}")
                        st.markdown("**字段**:")
                        for field in form.get("fields", []):
                            required = " *" if field.get("required") else ""
                            st.markdown(f"  - {field['label']} ({field['type']}){required}")
        else:
            st.warning("无法加载表单")
    except Exception:
        st.warning("后端不可达")
