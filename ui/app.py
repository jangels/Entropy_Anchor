"""
Streamlit UI - Entropy_Anchor 可视化界面
观测 Agent 的"塌缩过程"
"""

import streamlit as st
import requests
import json
import time
from typing import Optional

# 配置页面
st.set_page_config(
    page_title="Entropy_Anchor - The Vibe Architect",
    page_icon="🌀",
    layout="wide",
)

# 标题
st.title("🌀 Entropy_Anchor")
st.caption("Vibe-driven Agent Builder - The Vibe Architect - 意图编译现实的智能体构建器")

st.markdown("""
> "意图架构师: 不要仅仅写代码，要赋予它秩序。开始编译现实。"

> "熵之锚：负熵之锚, 工作于混沌边缘。

> 混乱 > 坍缩 > 秩序, Idea > Action Node。"

### 核心哲学
通过最精简的自然语言意图（Vibe），自动编译并生成具备特定 Skill 的子智能体。

### 架构层次
1. **The Philosopher Layer**: 处理输入的自然语言 Vibe
2. **The Probability Layer**: 评估任务可行性并生成多个执行路径
3. **The Action Node**: 最终生成的 Agent 实例，自带工作量证明（PoW）机制
""")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")
    api_url = st.text_input(
        "API URL",
        value="http://localhost:8003",
        help="Entropy_Anchor API 服务地址",
    )
    energy_budget = st.slider(
        "能量预算",
        min_value=10.0,
        max_value=100.0,
        value=100.0,
        step=5.0,
        help="Agent 可用的最大能量值",
    )

# 主界面
st.header("📝 输入 Vibe")

vibe_input = st.text_area(
    "描述你的意图（Vibe）",
    height=150,
    placeholder="例如：写一个计算斐波那契数列的函数，并测试前10个数",
    help="用自然语言描述你想要完成的任务",
)

if st.button("🚀 开始塌缩", type="primary", use_container_width=True):
    if not vibe_input.strip():
        st.error("请输入你的 Vibe！")
    else:
        with st.spinner("Agent 正在塌缩中..."):
            try:
                # 调用 API
                response = requests.post(
                    f"{api_url}/api/v1/agent/create",
                    json={
                        "vibe": vibe_input,
                        "energy_budget": energy_budget,
                    },
                    timeout=120,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 显示结果
                    st.success("✅ Agent 塌缩完成！")
                    
                    # 创建标签页展示不同信息
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 状态概览",
                        "🎯 任务规划",
                        "⚡ 执行结果",
                        "📜 熵报告",
                    ])
                    
                    with tab1:
                        st.subheader("Agent 状态")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Agent ID", result["agent_id"])
                        
                        with col2:
                            state_emoji = {
                                "quantum": "🌌",
                                "collapsing": "🌀",
                                "anchored": "⚓",
                                "decayed": "💀",
                            }
                            st.metric(
                                "状态",
                                f"{state_emoji.get(result['state'], '❓')} {result['state']}",
                            )
                        
                        with col3:
                            st.metric("剩余能量", f"{result['energy']:.1f}")
                        
                        # 能量条
                        st.progress(result["energy"] / 100.0)
                    
                    with tab2:
                        if result.get("task_plan"):
                            task_plan = result["task_plan"]
                            st.subheader("任务规划")
                            
                            st.write("**意图**:", task_plan.get("intent", "N/A"))
                            st.write("**领域**:", task_plan.get("domain", "N/A"))
                            st.write("**复杂度**:", task_plan.get("complexity", "N/A"))
                            
                            st.write("**执行步骤**:")
                            for i, step in enumerate(task_plan.get("steps", []), 1):
                                st.write(f"{i}. {step}")
                            
                            st.write("**估算能量消耗**:", task_plan.get("estimated_energy_cost", "N/A"))
                        else:
                            st.info("暂无任务规划信息")
                    
                    with tab3:
                        if result.get("execution_result"):
                            exec_result = result["execution_result"]
                            
                            if exec_result.get("success"):
                                st.success("✅ 执行成功")
                                
                                # 显示代码生成结果
                                if "code_generation" in exec_result.get("result", {}):
                                    code_gen = exec_result["result"]["code_generation"]
                                    st.write("**生成的代码文件**:", code_gen.get("filename", "N/A"))
                                    st.write("**文件路径**:", code_gen.get("file_path", "N/A"))
                                
                                # 显示测试结果
                                if "test_execution" in exec_result.get("result", {}):
                                    test_exec = exec_result["result"]["test_execution"]
                                    st.write("**测试状态**:", test_exec.get("status", "N/A"))
                                    
                                    if "results" in test_exec:
                                        for test_result in test_exec["results"]:
                                            if test_result.get("success"):
                                                st.success(f"✅ {test_result.get('file', 'N/A')} 执行成功")
                                                if test_result.get("stdout"):
                                                    st.code(test_result["stdout"], language="text")
                                            else:
                                                st.error(f"❌ {test_result.get('file', 'N/A')} 执行失败")
                                                if test_result.get("stderr"):
                                                    st.code(test_result["stderr"], language="text")
                            else:
                                st.error("❌ 执行失败")
                                st.write("**错误**:", exec_result.get("error", "Unknown error"))
                        else:
                            st.info("暂无执行结果")
                    
                    with tab4:
                        if result.get("entropy_report"):
                            report = result["entropy_report"]
                            
                            st.subheader("熵报告（工作量证明）")
                            
                            st.json(report)
                            
                            # 下载报告
                            report_json = json.dumps(report, ensure_ascii=False, indent=2)
                            st.download_button(
                                label="📥 下载报告",
                                data=report_json,
                                file_name=f"entropy_report_{result['agent_id']}.json",
                                mime="application/json",
                            )
                        else:
                            st.info("暂无熵报告")
                
                else:
                    st.error(f"❌ API 错误: {response.status_code}")
                    st.code(response.text, language="text")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到 API 服务。请确保 API 服务正在运行。")
                st.info("💡 提示：运行 `python api/routes.py` 或 `uvicorn api.routes:app --reload` 启动 API 服务")
            
            except Exception as e:
                st.error(f"❌ 发生错误: {str(e)}")
                st.exception(e)

# 底部说明
st.markdown("---")
st.markdown("""
### 💡 使用说明
1. 在文本框中输入你的自然语言意图（Vibe）
2. 调整能量预算（可选）
3. 点击"开始塌缩"按钮
4. 观察 Agent 从量子态到锚定态的完整塌缩过程

### 🔧 技术栈
- **Backend**: FastAPI + Pydantic
- **Agent Framework**: LangChain + LangGraph
- **UI**: Streamlit
""")
