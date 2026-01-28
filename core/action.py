"""
ActionNode - 行动节点
最终生成的 Agent 实例，自带工作量证明机制
"""

import subprocess
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from .agent import EntropyAgent, EnergyState
from .probability import ExecutionPath
from .llm_factory import LLMFactory, ModelProvider

load_dotenv()


class ProofOfWork:
    """
    工作量证明机制
    记录所有执行轨迹，生成可验证的工作报告
    """
    
    def __init__(self, agent_id: str, work_dir: str = "./workspace"):
        """
        初始化工作量证明
        
        Args:
            agent_id: Agent ID
            work_dir: 工作目录
        """
        self.agent_id = agent_id
        self.work_dir = Path(work_dir) / agent_id
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.work_dir / "proof_of_work.log"
        self.report_file = self.work_dir / "entropy_report.json"
    
    def log_action(self, action: str, result: Any, metadata: Optional[Dict] = None):
        """
        记录行动
        
        Args:
            action: 行动描述
            result: 行动结果
            metadata: 额外元数据
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": str(result),
            "metadata": metadata or {},
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def save_file(self, filename: str, content: str):
        """
        保存生成的文件
        
        Args:
            filename: 文件名
            content: 文件内容
        """
        file_path = self.work_dir / filename
        file_path.write_text(content, encoding="utf-8")
        self.log_action("file_created", f"Created {filename}", {"path": str(file_path)})
        return str(file_path)
    
    def generate_report(self, agent: EntropyAgent) -> Dict[str, Any]:
        """
        生成完整的工作量证明报告
        
        Args:
            agent: Agent 实例
            
        Returns:
            报告字典
        """
        report = agent.get_entropy_report()
        report["work_directory"] = str(self.work_dir)
        report["files_generated"] = [
            f.name for f in self.work_dir.iterdir() if f.is_file()
        ]
        
        # 保存报告
        with open(self.report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report


class ActionNode:
    """
    行动节点 - 执行具体的任务
    """
    
    def __init__(
        self,
        agent: EntropyAgent,
        execution_path: ExecutionPath,
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
    ):
        """
        初始化行动节点
        
        Args:
            agent: Agent 实例
            execution_path: 选定的执行路径
            provider: LLM 提供商 ("openai" 或 "gemini")，如果为 None 则自动检测
            model_name: 使用的 LLM 模型名称，如果为 None 则使用默认值
        """
        self.agent = agent
        self.execution_path = execution_path
        self.pow = ProofOfWork(agent.id)
        
        self.llm = LLMFactory.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=0.5,
        )
    
    def execute(self) -> Dict[str, Any]:
        """
        执行任务
        
        Returns:
            执行结果
        """
        # 转换状态为塌缩中
        self.agent.transition_state(EnergyState.COLLAPSING)
        
        try:
            # 根据执行路径选择工具并执行
            result = self._execute_path()
            
            # 转换状态为已锚定
            self.agent.transition_state(EnergyState.ANCHORED)
            
            # 生成工作量证明报告
            report = self.pow.generate_report(self.agent)
            
            self.agent.execution_result = {
                "success": True,
                "result": result,
                "report": report,
            }
            
            return self.agent.execution_result
            
        except Exception as e:
            # 执行失败，进入衰减态
            self.agent.transition_state(EnergyState.DECAYED)
            self.agent.execution_result = {
                "success": False,
                "error": str(e),
            }
            self.pow.log_action("execution_failed", str(e))
            raise
    
    def _execute_path(self) -> Dict[str, Any]:
        """
        根据执行路径执行任务
        
        Returns:
            执行结果
        """
        tools = self.execution_path.tools_required
        result = {}
        
        # 根据工具类型执行相应操作
        if "code_generator" in tools:
            code_result = self._generate_code()
            result["code_generation"] = code_result
        
        if "test_runner" in tools:
            test_result = self._run_tests()
            result["test_execution"] = test_result
        
        if "file_manager" in tools:
            file_result = self._manage_files()
            result["file_management"] = file_result
        
        return result
    
    def _generate_code(self) -> Dict[str, Any]:
        """
        生成代码
        
        Returns:
            代码生成结果
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的代码生成器。根据用户的需求生成完整的、可运行的 Python 代码。

要求：
1. 代码必须完整且可运行
2. 包含必要的注释
3. 遵循 Python 最佳实践
4. 如果可能，包含简单的测试或示例用法"""),
            ("human", "需求：{vibe}\n\n请生成代码："),
        ])
        
        messages = prompt.format_messages(vibe=self.agent.vibe)
        response = self.llm.invoke(messages)
        
        code = response.content
        
        # 提取代码块（如果 LLM 返回了 markdown 格式）
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        # 保存代码文件
        filename = f"generated_{self.agent.id}.py"
        file_path = self.pow.save_file(filename, code)
        
        self.agent.add_proof_of_work(
            action="code_generation",
            result=f"Generated {filename}",
            energy_cost=15.0,
        )
        
        self.pow.log_action("code_generated", filename, {"code_length": len(code)})
        
        return {
            "filename": filename,
            "file_path": file_path,
            "code_length": len(code),
        }
    
    def _run_tests(self) -> Dict[str, Any]:
        """
        运行测试
        
        Returns:
            测试执行结果
        """
        # 查找生成的代码文件
        code_files = [
            f for f in self.pow.work_dir.iterdir()
            if f.suffix == ".py" and f.name.startswith("generated_")
        ]
        
        if not code_files:
            return {"status": "skipped", "reason": "No code file found"}
        
        test_results = []
        
        for code_file in code_files:
            try:
                # 尝试执行代码
                # 使用绝对路径，避免 cwd 导致的路径重复问题
                code_file_abs = code_file.resolve()
                result = subprocess.run(
                    ["python", str(code_file_abs)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.pow.work_dir.resolve()),
                )
                
                test_result = {
                    "file": code_file.name,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0,
                }
                
                test_results.append(test_result)
                
                self.pow.log_action(
                    "test_executed",
                    f"Executed {code_file.name}",
                    test_result,
                )
                
            except subprocess.TimeoutExpired:
                test_results.append({
                    "file": code_file.name,
                    "success": False,
                    "error": "Timeout",
                })
            except Exception as e:
                test_results.append({
                    "file": code_file.name,
                    "success": False,
                    "error": str(e),
                })
        
        self.agent.add_proof_of_work(
            action="test_execution",
            result=f"Executed {len(test_results)} test(s)",
            energy_cost=10.0,
        )
        
        return {
            "status": "completed",
            "results": test_results,
        }
    
    def _manage_files(self) -> Dict[str, Any]:
        """
        管理文件
        
        Returns:
            文件管理结果
        """
        files = [
            {
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            }
            for f in self.pow.work_dir.iterdir()
            if f.is_file()
        ]
        
        self.agent.add_proof_of_work(
            action="file_management",
            result=f"Managed {len(files)} file(s)",
            energy_cost=2.0,
        )
        
        return {
            "files": files,
            "count": len(files),
        }
