"""
Lightweight tests for search handler functionality
Tests search logic without requiring actual Telegram API calls
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_handler import SearchHandler

def test_search_initialization():
    """Test that search handler initializes correctly"""
    handler = SearchHandler()
    assert handler.search_db is not None
    assert 'commands' in handler.search_db
    assert 'assets' in handler.search_db
    assert 'topics' in handler.search_db
    print("PASS: Search handler initialization test passed")

def test_exact_command_search():
    """Test exact command matching"""
    handler = SearchHandler()

    results = handler.search('btc')
    assert len(results) > 0
    assert any(r['key'] == 'btc' for r in results)
    print("PASS: Exact command search test passed")

def test_asset_search():
    """Test asset search functionality"""
    handler = SearchHandler()

    results = handler.search('bitcoin')
    assert len(results) > 0
    assert any('bitcoin' in r['name'].lower() for r in results)
    print("PASS: Asset search test passed")

def test_partial_search():
    """Test partial/fuzzy matching"""
    handler = SearchHandler()

    results = handler.search('analyt')
    assert len(results) > 0
    # Should find analytics, analysis, etc.
    assert any('analyt' in r['name'].lower() or 'analyt' in r.get('description', '').lower() for r in results)
    print("PASS: Partial search test passed")

def test_empty_search():
    """Test empty search returns no results"""
    handler = SearchHandler()

    results = handler.search('')
    assert len(results) == 0
    print("PASS: Empty search test passed")

def test_search_scoring():
    """Test that results are properly scored and sorted"""
    handler = SearchHandler()

    results = handler.search('btc')
    if len(results) > 1:
        # First result should have highest score
        assert results[0]['score'] >= results[1]['score']
    print("PASS: Search scoring test passed")

def test_search_limit():
    """Test that search respects result limits"""
    handler = SearchHandler()

    # Search for a common term that should return many results
    results = handler.search('signal', limit=3)
    assert len(results) <= 3
    print("PASS: Search limit test passed")

def test_command_formatting():
    """Test that commands are properly formatted in results"""
    handler = SearchHandler()

    results = handler.search('btc')
    btc_results = [r for r in results if r['type'] == 'command' and r['key'] == 'btc']
    if btc_results:
        assert btc_results[0]['command'] == '/btc'
    print("PASS: Command formatting test passed")

def run_all_tests():
    """Run all search handler tests"""
    print("Running Search Handler Tests...\n")

    try:
        test_search_initialization()
        test_exact_command_search()
        test_asset_search()
        test_partial_search()
        test_empty_search()
        test_search_scoring()
        test_search_limit()
        test_command_formatting()

        print("\nAll search handler tests passed!")
        return True

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
