"""Knowledge Base Management Page — upload, search, manage insurance knowledge."""
import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="知识库管理 — InsureAI", page_icon="📚", layout="wide")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("📚 知识库管理")
st.caption("投喂保险知识：上传文档 → 自动切片 → 向量化 → 入库 → Agent 自动引用")
st.markdown("---")

# Tabs for different functions
tab_upload, tab_search, tab_stats = st.tabs(["📤 投喂知识", "🔍 检索测试", "📊 知识库统计"])

# ==================== TAB 1: Upload ====================
with tab_upload:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📄 上传文档")
        uploaded_file = st.file_uploader(
            "拖拽或点击上传保险文档",
            type=["pdf", "docx", "txt", "md"],
            help="支持 PDF、Word、文本、Markdown。自动提取文本、切片、向量化。",
        )

        category = st.selectbox(
            "知识分类",
            options=["policy_clauses", "underwriting_guides", "claims_rules", "regulations", "industry_benchmarks"],
            format_func=lambda x: {
                "policy_clauses": "📋 保单条款库",
                "underwriting_guides": "🔍 核保指南库",
                "claims_rules": "⚠️ 理赔规则库",
                "regulations": "⚖️ 监管法规库",
                "industry_benchmarks": "📊 行业基准库",
            }.get(x, x),
        )

        source_label = st.text_input("来源标注（可选）", placeholder="如：平安财险核保手册 v2024")

        if uploaded_file and st.button("🚀 投喂到知识库", type="primary", use_container_width=True):
            with st.spinner("正在处理..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/api/v1/kb/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        data={"category": category, "source": source_label or uploaded_file.name},
                        timeout=120,
                    )
                    if resp.ok:
                        data = resp.json()
                        st.success(f"✅ 投喂成功！")
                        st.metric("新增知识块", data["chunks_added"])
                        st.metric("原文长度", f"{data['text_length']:,} 字")
                        with st.expander("📝 内容预览"):
                            st.text(data["preview"])
                    else:
                        st.error(f"失败: {resp.status_code} — {resp.text}")
                except Exception as e:
                    st.error(f"请求失败: {e}")

    with col_right:
        st.subheader("✏️ 直接粘贴文本")
        st.caption("不想上传文件？直接粘贴保险知识文本。")

        paste_text = st.text_area(
            "保险知识内容",
            height=250,
            placeholder="粘贴保单条款、核保指南、理赔规则、监管法规等中文保险知识...\n\n例如：\n【财产一切险 — 保障范围】\n保险人承保被保险财产因意外事故造成的直接物质损失...",
        )

        paste_category = st.selectbox(
            "知识分类",
            options=["policy_clauses", "underwriting_guides", "claims_rules", "regulations", "industry_benchmarks"],
            format_func=lambda x: {
                "policy_clauses": "📋 保单条款库",
                "underwriting_guides": "🔍 核保指南库",
                "claims_rules": "⚠️ 理赔规则库",
                "regulations": "⚖️ 监管法规库",
                "industry_benchmarks": "📊 行业基准库",
            }.get(x, x),
            key="paste_cat",
        )

        paste_source = st.text_input("来源标注", placeholder="手动输入", key="paste_src")

        if paste_text.strip() and st.button("✈️ 添加到知识库", type="primary", use_container_width=True):
            with st.spinner("正在向量化..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/api/v1/kb/add-text",
                        json={"text": paste_text, "category": paste_category, "source": paste_source or "manual"},
                        timeout=60,
                    )
                    if resp.ok:
                        data = resp.json()
                        st.success(f"✅ 添加成功！{data['chunks_added']} 个知识块")
                    else:
                        st.error(resp.text)
                except Exception as e:
                    st.error(f"请求失败: {e}")

# ==================== TAB 2: Search ====================
with tab_search:
    st.subheader("🔍 语义检索测试")
    st.caption("输入查询，测试知识库能否召回相关知识。这就是 Agent 实际使用的检索能力。")

    col_s, col_k = st.columns([3, 1])
    with col_s:
        search_query = st.text_input("搜索查询", placeholder="例如：电子厂火灾理赔需要哪些材料？")
    with col_k:
        search_cat = st.selectbox(
            "分类范围",
            options=["all"] + list({
                "policy_clauses": "📋 保单条款库",
                "underwriting_guides": "🔍 核保指南库",
                "claims_rules": "⚠️ 理赔规则库",
                "regulations": "⚖️ 监管法规库",
                "industry_benchmarks": "📊 行业基准库",
            }.keys()),
            format_func=lambda x: "全部" if x == "all" else {
                "policy_clauses": "📋 保单条款库",
                "underwriting_guides": "🔍 核保指南库",
                "claims_rules": "⚠️ 理赔规则库",
                "regulations": "⚖️ 监管法规库",
                "industry_benchmarks": "📊 行业基准库",
            }.get(x, x),
        )

    if search_query and st.button("🔍 检索", type="primary"):
        with st.spinner("检索中..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/api/v1/kb/search",
                    json={
                        "query": search_query,
                        "top_k": 5,
                        "category": None if search_cat == "all" else search_cat,
                    },
                    timeout=30,
                )
                if resp.ok:
                    data = resp.json()
                    st.info(f"共找到 {data['total_found']} 条结果")

                    for i, r in enumerate(data["results"], 1):
                        with st.container():
                            st.markdown(f"### [{i}] {r['category_name']}")
                            st.caption(f"相关度: {r['score']:.0%} | 来源: {r['source']}")
                            st.markdown(r["content"])
                            st.divider()
                else:
                    st.error(resp.text)
            except Exception as e:
                st.error(f"请求失败: {e}")

# ==================== TAB 3: Stats ====================
with tab_stats:
    st.subheader("📊 知识库统计")

    if st.button("🔄 刷新统计", type="primary"):
        pass  # trigger rerun below

    try:
        resp = requests.get(f"{API_BASE}/api/v1/kb/stats", timeout=5)
        if resp.ok:
            data = resp.json()
            stats = data["stats"]

            # Summary row
            total_docs = sum(s["documents"] for s in stats.values())
            cols = st.columns(5)
            metrics = [
                ("📋 保单条款", stats.get("policy_clauses", {}).get("documents", 0)),
                ("🔍 核保指南", stats.get("underwriting_guides", {}).get("documents", 0)),
                ("⚠️ 理赔规则", stats.get("claims_rules", {}).get("documents", 0)),
                ("⚖️ 监管法规", stats.get("regulations", {}).get("documents", 0)),
                ("📊 行业基准", stats.get("industry_benchmarks", {}).get("documents", 0)),
            ]
            for col, (label, count) in zip(cols, metrics):
                with col:
                    st.metric(label, count)

            st.metric("📚 知识库总量", f"{total_docs} 条")

            # Detail table
            st.markdown("### 分类详情")
            detail_data = []
            for cat_key, cat_info in stats.items():
                detail_data.append({
                    "分类": cat_info.get("description", cat_key),
                    "Key": cat_key,
                    "知识条数": cat_info.get("documents", 0),
                })
            st.dataframe(detail_data, use_container_width=True, hide_index=True)

            # Seed data button
            st.markdown("---")
            st.markdown("### 🛠️ 工具")
            if st.button("🌱 重新注入种子数据", help="清空现有数据并重新注入预置的保险知识库种子数据。会覆盖已有数据！"):
                with st.spinner("正在重新注入种子数据..."):
                    try:
                        # Clear all first, then seed
                        for cat in stats.keys():
                            requests.delete(f"{API_BASE}/api/v1/kb/clear/{cat}", timeout=10)
                        resp = requests.post(f"{API_BASE}/api/v1/kb/seed", timeout=120)
                        if resp.ok:
                            st.success("✅ 种子数据已重新注入！")
                            st.rerun()
                        else:
                            st.error(resp.text)
                    except Exception as e:
                        st.error(f"操作失败: {e}")
        else:
            st.warning("后端不可达")
    except Exception:
        st.warning("无法连接后端服务")

st.markdown("---")
st.info("""
**💡 知识库使用说明：**
1. **投喂**：上传保险相关的 PDF/Word/文本，或直接粘贴。自动切片 + 向量化。
2. **分类**：选择合适的知识分类（条款/核保/理赔/法规/基准），Agent 会优先检索对应分类。
3. **Agent 自动引用**：每次处理理赔/核保/续保时，Agent 自动从知识库检索相关知识并引用来源。
4. **来源标注**：上传时标注来源，方便后续追溯（如"平安财险核保手册 v2024"）。
""")
