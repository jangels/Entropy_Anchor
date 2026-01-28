"""
MVA (Minimum Viable Agent) 示例
演示如何根据 Vibe 自动生成 Python 脚本并运行测试
"""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  警告: python-dotenv 未安装，将无法自动加载 .env 文件")
    print("💡 提示: 运行 'uv sync' 或 'pip install python-dotenv' 安装依赖")
    load_dotenv = lambda *args, **kwargs: None  # 空函数，避免报错

# 加载 .env 文件（必须在导入 core 模块之前）
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    # 如果项目根目录没有 .env，尝试加载当前目录的
    load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, str(project_root))

from core import (
    EntropyAgent,
    PhilosopherLayer,
    ProbabilityLayer,
    ActionNode,
)


def main():
    """MVA 示例主函数"""
    
    print("🌀 Entropy_Anchor - MVA Example")
    print("=" * 60)
    
    # 检查环境变量（支持 OpenAI 或 Gemini）
    # 检测逻辑与 LLMFactory._detect_provider() 保持一致
    explicit_provider = os.getenv("LLM_PROVIDER", "").lower()
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))

    print(f"LLM_PROVIDER: {explicit_provider or '(未设置)'}")
    print(f"has_openai: {has_openai}")
    print(f"has_gemini: {has_gemini}")
    
    if not has_openai and not has_gemini:
        print("❌ 错误: 未设置 API Key")
        print("💡 提示: 请创建 .env 文件并设置 OPENAI_API_KEY 或 GEMINI_API_KEY")
        return
    
    # 检测使用的提供商（优先级与 LLMFactory 一致）
    if explicit_provider in ["openai", "gemini"]:
        provider = explicit_provider
    elif has_gemini and not has_openai:
        provider = "gemini"
    elif has_openai:
        provider = "openai"
    else:
        provider = None  # 会使用默认（OpenAI）
    
    if provider == "gemini":
        print(f"✅ 使用 Gemini API")
    elif provider == "openai":
        print(f"✅ 使用 OpenAI API")
    else:
        print(f"✅ 使用默认 API (OpenAI)")
    
    # 示例 Vibe
    vibe = "写一个计算斐波那契数列的函数，并测试前10个数"
    
    print(f"\n📝 Vibe: {vibe}")
    print("\n" + "=" * 60)
    
    try:
        # 创建 Agent
        print("\n[1/4] 创建 Agent...")
        agent = EntropyAgent(vibe=vibe, energy=100.0)
        print(f"✅ Agent 创建成功: {agent.id}")
        print(f"   状态: {agent.state.value}")
        print(f"   能量: {agent.energy}")
        
        # Philosopher Layer: 解析 Vibe
        print("\n[2/4] Philosopher Layer: 解析 Vibe...")
        philosopher = PhilosopherLayer(provider=provider)
        parsed_vibe = philosopher.parse_vibe(vibe)
        print(f"✅ Vibe 解析完成")
        print(f"   意图: {parsed_vibe.intent}")
        print(f"   领域: {parsed_vibe.domain}")
        print(f"   复杂度: {parsed_vibe.complexity}/10")
        print(f"   所需技能: {', '.join(parsed_vibe.required_skills)}")
        
        task_plan = philosopher.extract_task_plan(parsed_vibe)
        agent.task_plan = task_plan
        agent.add_proof_of_work(
            action="vibe_parsing",
            result="Vibe parsed successfully",
            energy_cost=5.0,
        )
        print(f"   任务步骤: {len(task_plan['steps'])} 步")
        
        # Probability Layer: 生成执行路径
        print("\n[3/4] Probability Layer: 生成执行路径...")
        probability_layer = ProbabilityLayer(provider=provider)
        paths = probability_layer.generate_paths(task_plan)
        print(f"✅ 生成了 {len(paths)} 个执行路径")
        
        for i, path in enumerate(paths, 1):
            print(f"\n   路径 {i}: {path.path_id}")
            print(f"   描述: {path.description}")
            print(f"   可行性: {path.feasibility_score:.2f}")
            print(f"   能量消耗: {path.estimated_energy_cost:.1f}")
            print(f"   所需工具: {', '.join(path.tools_required)}")
        
        optimal_path = probability_layer.select_optimal_path(
            paths,
            energy_budget=agent.energy,
        )
        
        if not optimal_path:
            print("❌ 错误: 没有找到可行的执行路径")
            return
        
        print(f"\n✅ 选择最优路径: {optimal_path.path_id}")
        agent.selected_tools = optimal_path.tools_required
        agent.add_proof_of_work(
            action="path_selection",
            result=f"Selected path: {optimal_path.path_id}",
            energy_cost=3.0,
        )
        
        # Action Node: 执行任务
        print("\n[4/4] Action Node: 执行任务...")
        print("   状态转换: QUANTUM -> COLLAPSING")
        action_node = ActionNode(agent, optimal_path, provider=provider)
        
        execution_result = action_node.execute()
        
        print(f"✅ 任务执行完成")
        print(f"   状态转换: COLLAPSING -> {agent.state.value}")
        print(f"   剩余能量: {agent.energy:.1f}")
        
        # 显示执行结果
        if execution_result.get("success"):
            print("\n" + "=" * 60)
            print("📊 执行结果摘要")
            print("=" * 60)
            
            result = execution_result.get("result", {})
            
            if "code_generation" in result:
                code_gen = result["code_generation"]
                print(f"\n✅ 代码生成:")
                print(f"   文件: {code_gen.get('filename', 'N/A')}")
                print(f"   路径: {code_gen.get('file_path', 'N/A')}")
                print(f"   代码长度: {code_gen.get('code_length', 0)} 字符")
            
            if "test_execution" in result:
                test_exec = result["test_execution"]
                print(f"\n✅ 测试执行:")
                print(f"   状态: {test_exec.get('status', 'N/A')}")
                
                if "results" in test_exec:
                    for test_result in test_exec["results"]:
                        file_name = test_result.get("file", "N/A")
                        if test_result.get("success"):
                            print(f"   ✅ {file_name}: 执行成功")
                            if test_result.get("stdout"):
                                print(f"      输出:\n{test_result['stdout']}")
                        else:
                            print(f"   ❌ {file_name}: 执行失败")
                            if test_result.get("stderr"):
                                print(f"      错误:\n{test_result['stderr']}")
            
            # 显示熵报告
            print("\n" + "=" * 60)
            print("📜 熵报告（工作量证明）")
            print("=" * 60)
            
            report = agent.get_entropy_report()
            print(f"\nAgent ID: {report['agent_id']}")
            print(f"状态: {report['current_state']}")
            print(f"能量: {report['energy_level']:.1f}")
            print(f"生命周期: {report['lifetime']:.2f} 秒")
            print(f"总行动数: {report['total_actions']}")
            print(f"工作目录: {report.get('work_directory', 'N/A')}")
            
            if "proof_of_work_summary" in report:
                print(f"\n最近行动记录:")
                for pow_item in report["proof_of_work_summary"]:
                    print(f"  - {pow_item['action']} (消耗能量: {pow_item['energy_cost']:.1f})")
        
        else:
            print(f"\n❌ 执行失败: {execution_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
