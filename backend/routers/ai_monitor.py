"""
AI monitoring router — token usage tracking and cost optimization.

Provides visibility into AI costs and context management efficiency.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from auth import get_current_user
from services.ai import get_token_usage_stats, audit_context_efficiency, get_model_info

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/usage")
def get_ai_usage_stats(
    days: int = 7,
    current_user: dict = Depends(get_current_user),
):
    """
    Get AI token usage statistics.
    
    Query params:
    - days: Number of days to analyze (default: 7, max: 30)
    
    Returns breakdown by model, task, and daily costs.
    """
    try:
        days = min(days, 30)  # Cap at 30 days
        stats = get_token_usage_stats(days)
        return {
            "success": True,
            "period_days": days,
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get AI usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


@router.get("/audit")
def audit_ai_efficiency(
    current_user: dict = Depends(get_current_user),
):
    """
    Audit AI context management for inefficiencies.
    
    Identifies:
    - High token usage requests
    - Expensive model usage
    - Long prompts
    - Cache performance
    
    Returns recommendations for optimization.
    """
    try:
        audit = audit_context_efficiency()
        return {
            "success": True,
            "audit": audit,
        }
    except Exception as e:
        logger.error(f"Failed to audit AI efficiency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to audit: {str(e)}",
        )


@router.get("/models")
def get_ai_models(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current AI model configuration and pricing.
    """
    try:
        info = get_model_info()
        return {
            "success": True,
            "models": info,
        }
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get models: {str(e)}",
        )


@router.get("/dashboard")
def get_ai_dashboard(
    days: int = 7,
    current_user: dict = Depends(get_current_user),
):
    """
    Get comprehensive AI monitoring dashboard data.
    
    Combines usage stats, audit results, and model info.
    """
    try:
        days = min(days, 30)
        
        usage = get_token_usage_stats(days)
        audit = audit_context_efficiency()
        models = get_model_info()
        
        # Calculate efficiency metrics
        total_requests = usage.get("total_requests", 0)
        cache_hits = usage.get("cache_hits", 0)
        cache_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Cost per request
        total_cost = usage.get("total_cost_usd", 0)
        avg_cost = total_cost / total_requests if total_requests > 0 else 0
        
        return {
            "success": True,
            "period_days": days,
            "summary": {
                "total_requests": total_requests,
                "total_cost_usd": total_cost,
                "cache_hit_rate": round(cache_rate, 2),
                "avg_cost_per_request": round(avg_cost, 6),
                "inefficiencies_found": len(audit.get("inefficiencies", [])),
            },
            "usage": usage,
            "audit": audit,
            "models": models,
        }
    except Exception as e:
        logger.error(f"Failed to get AI dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard: {str(e)}",
        )
