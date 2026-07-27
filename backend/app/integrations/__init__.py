"""Integrations package"""
from .supabase_client import get_supabase_client
from .gemini_client import GeminiClient
from .n8n_client import trigger_n8n_workflow

__all__ = ["get_supabase_client",  "GeminiClient", "trigger_n8n_workflow"]
