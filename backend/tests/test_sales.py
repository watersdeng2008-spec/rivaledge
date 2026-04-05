"""
Tests for sales agent components.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Test lead scoring
def test_calculate_priority_score():
    """Test lead priority scoring algorithm."""
    from services.sales_db import calculate_priority_score
    
    # High value lead
    high_value = {
        "title": "VP Product",
        "company_size": "51-200",
        "industry": "SaaS",
        "email": "test@example.com",
        "company_website": "https://example.com",
        "linkedin_url": "https://linkedin.com/in/test"
    }
    score = calculate_priority_score(high_value)
    assert score >= 70  # Should be high priority
    
    # Low value lead
    low_value = {
        "title": "Intern",
        "company_size": "1000+",
        "industry": "Retail",
    }
    score = calculate_priority_score(low_value)
    assert score < 50  # Should be low priority


# Test LinkedIn parser
def test_linkedin_parser():
    """Test LinkedIn CSV parsing."""
    from services.research_agent import LinkedInParser
    
    csv_content = """First Name,Last Name,Title,Company,Company Industry,Company Size,Profile Link
John,Doe,VP Product,Acme Inc,SaaS,51-200,https://linkedin.com/in/johndoe
Jane,Smith,CEO,TechCorp,Software,11-50,https://linkedin.com/in/janesmith"""
    
    parser = LinkedInParser()
    leads = parser.parse_csv(csv_content)
    
    assert len(leads) == 2
    assert leads[0]["name"] == "John Doe"
    assert leads[0]["title"] == "VP Product"
    assert leads[0]["source"] == "linkedin"


# Test Apollo client (mocked)
def test_apollo_search():
    """Test Apollo search with mocked API."""
    from services.research_agent import ApolloClient
    
    with patch('services.research_agent.httpx.post') as mock_post:
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "people": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "title": "VP Product",
                    "organization": {"name": "Acme Inc", "estimated_num_employees": 100},
                    "linkedin_url": "https://linkedin.com/in/johndoe",
                    "email": "john@acme.com"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        client = ApolloClient(api_key="test-key")
        results = client.search_people(titles=["VP Product"], limit=10)
        
        assert len(results) == 1
        assert results[0]["name"] == "John Doe"
        assert results[0]["email"] == "john@acme.com"


# Test Hunter client (mocked)
def test_hunter_find_email():
    """Test Hunter email finding with mocked API."""
    from services.research_agent import HunterClient
    
    with patch('services.research_agent.httpx.get') as mock_get:
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"email": "john@acme.com"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        client = HunterClient(api_key="test-key")
        email = client.find_email("acme.com", "John", "Doe")
        
        assert email == "john@acme.com"


# Test Research Agent orchestration
def test_research_agent_enrich_and_save():
    """Test lead enrichment and saving."""
    from services.research_agent import ResearchAgent
    
    with patch('services.research_agent.create_lead') as mock_create, \
         patch('services.research_agent.get_lead_by_email') as mock_get:
        
        mock_get.return_value = None  # No existing lead
        mock_create.return_value = "test-uuid-123"
        
        agent = ResearchAgent()
        lead_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "title": "VP Product",
            "company": "Acme Inc",
            "source": "test"
        }
        
        # Mock pain signal detection
        agent._detect_pain_signals = Mock(return_value=["competitor_monitoring"])
        
        result = agent._enrich_and_save(lead_data)
        
        assert result == "test-uuid-123"
        mock_create.assert_called_once()


# Test circuit breaker (CSkill pattern)
def test_circuit_breaker():
    """Test circuit breaker functionality."""
    from services.ai import check_circuit_breaker, reset_circuit_breaker
    
    # Initially not tripped
    status = check_circuit_breaker()
    assert status["tripped"] == False
    assert status["consecutive_failures"] == 0
    
    # Reset should work
    reset_circuit_breaker()
    status = check_circuit_breaker()
    assert status["tripped"] == False


# Test context budgets (CSkill pattern)
def test_context_budgets():
    """Test context budget management."""
    from services.ai import get_context_budget, CONTEXT_BUDGETS
    
    # Check default budgets exist
    assert "simple_task" in CONTEXT_BUDGETS
    assert "standard_task" in CONTEXT_BUDGETS
    assert "complex_task" in CONTEXT_BUDGETS
    
    # Check budget retrieval
    budget = get_context_budget("simple_task")
    assert budget > 0
    assert budget < CONTEXT_BUDGETS["complex_task"]


# Test API endpoints (integration tests would need FastAPI test client)
def test_lead_create_model():
    """Test lead creation Pydantic model."""
    from routers.sales import LeadCreate
    
    lead = LeadCreate(
        email="test@example.com",
        name="Test User",
        title="VP Product",
        company="Acme Inc",
        source="test"
    )
    
    assert lead.email == "test@example.com"
    assert lead.source == "test"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
