"""
Entropy_Anchor 主入口
提供命令行接口来创建和执行 Agent
"""

import argparse
import os
import sys
from pathlib import Path

from core import (
    EntropyAgent,
    PhilosopherLayer,
    ProbabilityLayer,
    ActionNode,
)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Entropy_Anchor - The Vibe Coder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py "写一个计算斐波那契数列的函数"
  python main.py "创建一个简单的 HTTP 服务器" --energy 80
        """,
    )
    
    parser.add_argument(
        "vibe",
        type=str,
        help="自然语言意图（Vibe）",
    )
    
    parser.add_argument(
        "--energy",
        type=float,
        default=100.0,
        help="能量预算 (默认: 100.0)",
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./workspace",
        help="输出目录 (默认: ./workspace)",
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "gemini"],
        default=None,
        help="LLM 提供商 (openai/gemini)，默认自动检测",
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="模型名称，默认使用提供商默认模型",
    )
    
    args = parser.parse_args()
    
    # 检查环境变量（支持 OpenAI 或 Gemini）
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    
    if not has_openai and not has_gemini:
        print("❌ 错误: 未设置 API Key")
        print("💡 提示: 请创建 .env 文件并设置 OPENAI_API_KEY 或 GEMINI_API_KEY")
        sys.exit(1)
    
    # 确定使用的提供商
    provider = args.provider
    if provider:
        provider = provider.lower()
        if provider == "gemini" and not has_gemini:
            print("❌ 错误: 指定使用 Gemini 但未设置 GEMINI_API_KEY")
            sys.exit(1)
        elif provider == "openai" and not has_openai:
            print("❌ 错误: 指定使用 OpenAI 但未设置 OPENAI_API_KEY")
            sys.exit(1)
    else:
        # 自动检测
        provider = "gemini" if has_gemini and not has_openai else None
    
    if provider == "gemini":
        print("✅ 使用 Gemini API")
    else:
        print("✅ 使用 OpenAI API")
    
    print("🌀 Entropy_Anchor - The Vibe Coder")
    print("=" * 60)
    print(f"Vibe: {args.vibe}")
    print(f"能量预算: {args.energy}")
    print("=" * 60)
    
    try:
        # 创建 Agent
        agent = EntropyAgent(vibe=args.vibe, energy=args.energy)
        
        # Philosopher Layer
        print("\n[1/3] Philosopher Layer: 解析 Vibe...")
        philosopher = PhilosopherLayer(provider=provider, model_name=args.model)
        parsed_vibe = philosopher.parse_vibe(args.vibe)
        task_plan = philosopher.extract_task_plan(parsed_vibe)
        agent.task_plan = task_plan
        agent.add_proof_of_work(
            action="vibe_parsing",
            result="Vibe parsed successfully",
            energy_cost=5.0,
        )
        print(f"✅ 意图: {parsed_vibe.intent}")
        print(f"   领域: {parsed_vibe.domain}")
        print(f"   复杂度: {parsed_vibe.complexity}/10")
        
        # Probability Layer
        print("\n[2/3] Probability Layer: 生成执行路径...")
        probability_layer = ProbabilityLayer(provider=provider, model_name=args.model)
        paths = probability_layer.generate_paths(task_plan)
        optimal_path = probability_layer.select_optimal_path(
            paths,
            energy_budget=agent.energy,
        )
        
        if not optimal_path:
            print("❌ 错误: 没有找到可行的执行路径")
            sys.exit(1)
        
        agent.selected_tools = optimal_path.tools_required
        agent.add_proof_of_work(
            action="path_selection",
            result=f"Selected path: {optimal_path.path_id}",
            energy_cost=3.0,
        )
        print(f"✅ 选择路径: {optimal_path.path_id}")
        print(f"   可行性: {optimal_path.feasibility_score:.2f}")
        
        # Action Node
        print("\n[3/3] Action Node: 执行任务...")
        action_node = ActionNode(agent, optimal_path, provider=provider, model_name=args.model)
        execution_result = action_node.execute()
        
        if execution_result.get("success"):
            print("✅ 任务执行成功！")
            
            # 显示报告路径
            report = agent.get_entropy_report()
            work_dir = report.get("work_directory", "N/A")
            print(f"\n📜 熵报告已保存到: {work_dir}")
            
            # 显示生成的文件
            if "files_generated" in report:
                print(f"\n📁 生成的文件:")
                for file in report["files_generated"]:
                    print(f"   - {file}")
        else:
            print(f"❌ 任务执行失败: {execution_result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
