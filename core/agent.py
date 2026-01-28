"""
EntropyAgent - 核心 Agent 类
实现能量衰减逻辑和基础生命周期管理
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class EnergyState(str, Enum):
    """能量状态枚举"""
    QUANTUM = "quantum"  # 量子态：未塌缩
    COLLAPSING = "collapsing"  # 塌缩中
    ANCHORED = "anchored"  # 已锚定
    DECAYED = "decayed"  # 已衰减


class EntropyAgent(BaseModel):
    """
    EntropyAgent - 熵锚智能体
    
    核心特性：
    1. 能量衰减机制：每次行动消耗能量
    2. 状态机：从量子态到锚定态的塌缩过程
    3. 工作量证明：自动记录所有行动轨迹
    """
    
    id: str = Field(default_factory=lambda: f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    vibe: str = Field(..., description="原始自然语言意图")
    energy: float = Field(default=100.0, ge=0.0, le=100.0, description="当前能量值")
    state: EnergyState = Field(default=EnergyState.QUANTUM, description="当前状态")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 工作量证明记录
    proof_of_work: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 任务规划结果
    task_plan: Optional[Dict[str, Any]] = None
    
    # 工具选择结果
    selected_tools: List[str] = Field(default_factory=list)
    
    # 执行结果
    execution_result: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def consume_energy(self, amount: float) -> bool:
        """
        消耗能量
        
        Args:
            amount: 消耗的能量值
            
        Returns:
            是否成功消耗（能量不足时返回 False）
        """
        if self.energy < amount:
            return False
        
        self.energy -= amount
        self.updated_at = datetime.now()
        
        # 能量过低时进入衰减态
        if self.energy < 10.0:
            self.state = EnergyState.DECAYED
        
        return True
    
    def add_proof_of_work(self, action: str, result: Any, energy_cost: float = 1.0):
        """
        添加工作量证明记录
        
        Args:
            action: 执行的动作
            result: 动作结果
            energy_cost: 消耗的能量
        """
        if not self.consume_energy(energy_cost):
            return False
        
        pow_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": str(result),
            "energy_cost": energy_cost,
            "remaining_energy": self.energy,
        }
        
        self.proof_of_work.append(pow_record)
        return True
    
    def transition_state(self, new_state: EnergyState):
        """
        状态转换
        
        Args:
            new_state: 新状态
        """
        valid_transitions = {
            EnergyState.QUANTUM: [EnergyState.COLLAPSING],
            EnergyState.COLLAPSING: [EnergyState.ANCHORED, EnergyState.DECAYED],
            EnergyState.ANCHORED: [EnergyState.DECAYED],
            EnergyState.DECAYED: [],  # 衰减态是终态
        }
        
        if new_state in valid_transitions.get(self.state, []):
            self.state = new_state
            self.updated_at = datetime.now()
            self.add_proof_of_work(
                action=f"state_transition:{self.state.value}->{new_state.value}",
                result="success",
                energy_cost=0.5
            )
            return True
        
        return False
    
    def get_entropy_report(self) -> Dict[str, Any]:
        """
        生成熵报告（工作量证明摘要）
        
        Returns:
            包含所有关键信息的报告
        """
        return {
            "agent_id": self.id,
            "vibe": self.vibe,
            "current_state": self.state.value,
            "energy_level": self.energy,
            "lifetime": (self.updated_at - self.created_at).total_seconds(),
            "total_actions": len(self.proof_of_work),
            "task_plan": self.task_plan,
            "selected_tools": self.selected_tools,
            "execution_result": self.execution_result,
            "proof_of_work_summary": [
                {
                    "action": pow_item["action"],
                    "energy_cost": pow_item["energy_cost"],
                    "timestamp": pow_item["timestamp"],
                }
                for pow_item in self.proof_of_work[-10:]  # 最近10条记录
            ],
        }
