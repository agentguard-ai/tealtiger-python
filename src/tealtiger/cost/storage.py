"""Cost storage interfaces and implementations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
from .types import CostRecord, CostSummary, ModelProvider


class CostStorage(ABC):
    """Abstract interface for cost storage."""
    
    @abstractmethod
    async def store(self, record: CostRecord) -> None:
        """Store a cost record."""
        pass
    
    @abstractmethod
    async def get(self, id: str) -> Optional[CostRecord]:
        """Get a cost record by ID."""
        pass
    
    @abstractmethod
    async def get_by_request_id(self, request_id: str) -> List[CostRecord]:
        """Get cost records by request ID."""
        pass
    
    @abstractmethod
    async def get_by_agent_id(
        self, agent_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CostRecord]:
        """Get cost records by agent ID."""
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[CostRecord]:
        """Get cost records within a time range."""
        pass
    
    @abstractmethod
    async def get_summary(
        self, start_date: datetime, end_date: datetime,
        agent_id: Optional[str] = None
    ) -> CostSummary:
        """Get cost summary for a time period."""
        pass
    
    @abstractmethod
    async def delete_older_than(self, before_date: datetime) -> int:
        """Delete cost records older than a date."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cost records."""
        pass


class InMemoryCostStorage(CostStorage):
    """In-memory cost storage implementation."""
    
    def __init__(self):
        self.records: Dict[str, CostRecord] = {}
    
    async def store(self, record: CostRecord) -> None:
        """Store a cost record."""
        self.records[record.id] = record
    
    async def get(self, id: str) -> Optional[CostRecord]:
        """Get a cost record by ID."""
        return self.records.get(id)
    
    async def get_by_request_id(self, request_id: str) -> List[CostRecord]:
        """Get cost records by request ID."""
        return [r for r in self.records.values() if r.request_id == request_id]
    
    async def get_by_agent_id(
        self, agent_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CostRecord]:
        """Get cost records by agent ID."""
        records = [r for r in self.records.values() if r.agent_id == agent_id]
        
        if start_date:
            records = [r for r in records if datetime.fromisoformat(r.timestamp) >= start_date]
        if end_date:
            records = [r for r in records if datetime.fromisoformat(r.timestamp) <= end_date]
        
        return records
    
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[CostRecord]:
        """Get cost records within a time range."""
        return [
            r for r in self.records.values()
            if start_date <= datetime.fromisoformat(r.timestamp) <= end_date
        ]
    
    async def get_summary(
        self, start_date: datetime, end_date: datetime,
        agent_id: Optional[str] = None
    ) -> CostSummary:
        """Get cost summary for a time period."""
        records = await self.get_by_date_range(start_date, end_date)
        
        if agent_id:
            records = [r for r in records if r.agent_id == agent_id]
        
        total_cost = sum(r.actual_cost for r in records)
        total_requests = len(records)
        avg_cost = total_cost / total_requests if total_requests > 0 else 0.0
        
        by_model: Dict[str, float] = {}
        by_provider: Dict[ModelProvider, float] = {}
        by_agent: Dict[str, float] = {}
        
        for r in records:
            by_model[r.model] = by_model.get(r.model, 0.0) + r.actual_cost
            by_provider[r.provider] = by_provider.get(r.provider, 0.0) + r.actual_cost
            by_agent[r.agent_id] = by_agent.get(r.agent_id, 0.0) + r.actual_cost
        
        total_tokens = {
            'input': sum(r.actual_tokens.input_tokens for r in records),
            'output': sum(r.actual_tokens.output_tokens for r in records),
            'total': sum(r.actual_tokens.total_tokens for r in records)
        }
        
        return CostSummary(
            total_cost=total_cost,
            total_requests=total_requests,
            average_cost_per_request=avg_cost,
            by_model=by_model,
            by_provider=by_provider,
            by_agent=by_agent,
            period={'start': start_date.isoformat(), 'end': end_date.isoformat()},
            total_tokens=total_tokens
        )
    
    async def delete_older_than(self, before_date: datetime) -> int:
        """Delete cost records older than a date."""
        to_delete = [
            id for id, r in self.records.items()
            if datetime.fromisoformat(r.timestamp) < before_date
        ]
        for id in to_delete:
            del self.records[id]
        return len(to_delete)
    
    async def clear(self) -> None:
        """Clear all cost records."""
        self.records.clear()
    
    def size(self) -> int:
        """Get total number of records."""
        return len(self.records)
