"""
Hybrid memory system: AgentMemory + MEMORY.md

AgentMemory provides:
- Vector search (semantic similarity)
- Auto-summarization
- Importance scoring

MEMORY.md remains:
- Human-readable curated memory
- Long-term storage
- Git versioned
"""
import os
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Try to import agentmemory, fallback to simple implementation if not available
try:
    from agentmemory import MemoryStore as AgentMemoryStore
    AGENTMEMORY_AVAILABLE = True
except ImportError:
    AGENTMEMORY_AVAILABLE = False
    logging.warning("agentmemory not installed, using fallback implementation")

logger = logging.getLogger(__name__)


class HybridMemory:
    """
    Hybrid memory system combining AgentMemory (vector search) with MEMORY.md (human-readable).
    
    Usage:
        memory = HybridMemory(agent_id="ben-d")
        
        # Store memory
        memory.remember(
            content="Waters prefers Telegram for quick decisions",
            importance=9,
            category="communication"
        )
        
        # Search memories
        results = memory.recall("How should I contact Waters?")
        
        # Summarize recent period
        summary = memory.summarize_period(days=7)
    """
    
    def __init__(self, agent_id: str = "ben-d"):
        self.agent_id = agent_id
        self.memory_dir = Path(__file__).parent.parent / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Initialize vector store if available
        if AGENTMEMORY_AVAILABLE:
            vector_path = self.memory_dir / "vector"
            vector_path.mkdir(exist_ok=True)
            self.vector_store = AgentMemoryStore(
                agent_id=agent_id,
                storage_path=str(vector_path)
            )
            logger.info(f"AgentMemory initialized for {agent_id}")
        else:
            self.vector_store = None
            logger.warning("AgentMemory not available, using file-based fallback")
        
        # Path to human-readable memory
        self.memory_md_path = Path(__file__).parent.parent / "MEMORY.md"
        
        # Fallback: simple JSON storage
        self.fallback_path = self.memory_dir / f"{agent_id}_memories.json"
        self.fallback_memories = self._load_fallback()
    
    def _load_fallback(self) -> List[Dict]:
        """Load memories from fallback JSON file."""
        if self.fallback_path.exists():
            try:
                with open(self.fallback_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load fallback memories: {e}")
        return []
    
    def _save_fallback(self):
        """Save memories to fallback JSON file."""
        try:
            with open(self.fallback_path, 'w') as f:
                json.dump(self.fallback_memories, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save fallback memories: {e}")
    
    def remember(
        self,
        content: str,
        importance: int = 5,
        category: str = "general",
        **kwargs
    ) -> bool:
        """
        Store a memory in both vector store and fallback.
        
        Args:
            content: The memory content
            importance: 1-10 importance score (10 = critical)
            category: Category for filtering
            **kwargs: Additional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            # Store in vector DB (fast search)
            if self.vector_store and AGENTMEMORY_AVAILABLE:
                self.vector_store.create(
                    content=content,
                    metadata={
                        "importance": importance,
                        "category": category,
                        "timestamp": datetime.utcnow().isoformat(),
                        "agent_id": self.agent_id,
                        **kwargs
                    }
                )
            
            # Always store in fallback (JSON file)
            self.fallback_memories.append({
                "content": content,
                "importance": importance,
                "category": category,
                "timestamp": datetime.utcnow().isoformat(),
                **kwargs
            })
            self._save_fallback()
            
            # If high importance, also log to MEMORY.md
            if importance >= 8:
                self._append_to_memory_md(content, category, importance)
            
            logger.info(f"Memory stored (importance {importance}): {content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    def _append_to_memory_md(self, content: str, category: str, importance: int):
        """Append high-importance memory to MEMORY.md."""
        try:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            entry = f"\n## {timestamp} [Importance: {importance}/10]\n\n**{category}:** {content}\n"
            
            with open(self.memory_md_path, 'a') as f:
                f.write(entry)
                
        except Exception as e:
            logger.error(f"Failed to append to MEMORY.md: {e}")
    
    def recall(
        self,
        query: str,
        n_results: int = 5,
        min_importance: int = 1,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories semantically.
        
        Args:
            query: Search query
            n_results: Number of results to return
            min_importance: Minimum importance score
            category: Filter by category (optional)
            
        Returns:
            List of matching memories with similarity scores
        """
        try:
            # Try vector search first
            if self.vector_store and AGENTMEMORY_AVAILABLE:
                filter_dict = {"importance": {"gte": min_importance}}
                if category:
                    filter_dict["category"] = category
                
                results = self.vector_store.search(
                    query=query,
                    n_results=n_results,
                    filter=filter_dict
                )
                
                if results:
                    return results
            
            # Fallback: simple keyword search in JSON memories
            return self._fallback_search(query, n_results, min_importance, category)
            
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return self._fallback_search(query, n_results, min_importance, category)
    
    def _fallback_search(
        self,
        query: str,
        n_results: int,
        min_importance: int,
        category: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Simple keyword-based fallback search."""
        query_lower = query.lower()
        words = query_lower.split()
        
        scored = []
        for memory in self.fallback_memories:
            # Filter by importance and category
            if memory.get("importance", 0) < min_importance:
                continue
            if category and memory.get("category") != category:
                continue
            
            # Simple scoring: count matching words
            content_lower = memory.get("content", "").lower()
            score = sum(1 for word in words if word in content_lower)
            
            if score > 0:
                scored.append({
                    **memory,
                    "similarity": score / len(words)  # Normalized score
                })
        
        # Sort by similarity score
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:n_results]
    
    def summarize_period(self, days: int = 7) -> str:
        """
        Auto-summarize memories from the last N days.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Summary string
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Get recent memories
            recent = [
                m for m in self.fallback_memories
                if datetime.fromisoformat(m.get("timestamp", "2000-01-01")) > cutoff
            ]
            
            if not recent:
                return f"No memories from last {days} days."
            
            # Sort by importance
            recent.sort(key=lambda x: x.get("importance", 0), reverse=True)
            
            # Build summary
            lines = [f"Summary of last {days} days ({len(recent)} memories):\n"]
            
            # Group by category
            by_category = {}
            for m in recent:
                cat = m.get("category", "general")
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(m)
            
            # Top memories by category
            for cat, memories in sorted(by_category.items()):
                lines.append(f"\n**{cat.upper()}:**")
                for m in memories[:3]:  # Top 3 per category
                    content = m.get("content", "")[:100]
                    if len(m.get("content", "")) > 100:
                        content += "..."
                    lines.append(f"  • [{m.get('importance')}/10] {content}")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return f"Error summarizing: {e}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_memories": len(self.fallback_memories),
            "vector_store_available": AGENTMEMORY_AVAILABLE and self.vector_store is not None,
            "high_importance": len([m for m in self.fallback_memories if m.get("importance", 0) >= 8]),
            "categories": list(set(m.get("category", "general") for m in self.fallback_memories)),
        }


# Convenience function
def get_memory() -> HybridMemory:
    """Get configured HybridMemory instance."""
    return HybridMemory(agent_id="ben-d")
