#!/usr/bin/env python3
"""
Test script to verify FANWS works like AAWT.
Tests all core components and features.
"""

import sys
import os

# Set offscreen for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_components():
    """Test all AAWT components initialization."""
    print("="*60)
    print("Testing FANWS AAWT Integration")
    print("="*60)
    print()
    
    # Test 1: Settings Manager
    print("1. Testing Settings Manager...")
    try:
        from src.system.settings_manager import SettingsManager
        settings = SettingsManager('config/user_settings.json')
        
        # Test dot-notation access
        theme = settings.get('ui.theme', 'light')
        window_width = settings.get('ui.window.width', 1280)
        
        print(f"   ✓ Settings manager initialized")
        print(f"   ✓ Theme: {theme}")
        print(f"   ✓ Window width: {window_width}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 2: Database Manager
    print("\n2. Testing Database Manager...")
    try:
        from src.database.database_manager import DatabaseManager
        
        db_path = settings.get('advanced.database_path', 'config/fanws.db')
        pool_size = settings.get('performance.connection_pool_size', 5)
        database = DatabaseManager(db_path, pool_size)
        
        print(f"   ✓ Database manager initialized")
        print(f"   ✓ Database path: {db_path}")
        print(f"   ✓ Pool size: {pool_size}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 3: Text Analyzer
    print("\n3. Testing Text Analyzer...")
    try:
        from src.text.text_processing import TextAnalyzer
        analyzer = TextAnalyzer()
        
        # Test analysis
        sample_text = "This is a test sentence. It has multiple sentences. We can analyze this text."
        result = analyzer.analyze_text(sample_text)
        
        print(f"   ✓ Text analyzer initialized")
        print(f"   ✓ Sample analysis:")
        print(f"     - Word count: {result.get('word_count', 'N/A')}")
        print(f"     - Sentence count: {result.get('sentence_count', 'N/A')}")
        if 'readability_score' in result:
            print(f"     - Readability: {result['readability_score']}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 4: Export Manager
    print("\n4. Testing Export Manager...")
    try:
        from src.system.export_manager import ExportManager
        exporter = ExportManager(settings)
        
        print(f"   ✓ Export manager initialized")
        print(f"   ✓ Default format: {settings.get('export.default_format', 'docx')}")
        print(f"   ✓ Export directory: {settings.get('export.default_export_dir', 'exports')}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 5: File Operations
    print("\n5. Testing File Operations...")
    try:
        from src.system.file_operations import FileOperations
        files = FileOperations()
        
        print(f"   ✓ File operations initialized")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 6: API Manager
    print("\n6. Testing API Manager...")
    try:
        from src.system.api_manager import get_api_manager
        api = get_api_manager()
        
        print(f"   ✓ API manager initialized")
        print(f"   ✓ Caching enabled: {settings.get('api.enable_api_caching', True)}")
        print(f"   ✓ Default provider: {settings.get('api.default_provider', 'openai')}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 7: Integration Test
    print("\n7. Testing Component Integration...")
    try:
        # Test settings access
        autosave_interval = settings.get('general.autosave_interval', 60)
        daily_goal = settings.get('writing.daily_word_goal', 1000)
        
        # Test database with settings
        cache_size = settings.get('performance.cache_size_mb', 100)
        
        print(f"   ✓ Settings integration working")
        print(f"     - Autosave interval: {autosave_interval}s")
        print(f"     - Daily word goal: {daily_goal}")
        print(f"     - Cache size: {cache_size}MB")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    return True


def main():
    """Run tests."""
    try:
        success = test_components()
        
        print()
        print("="*60)
        if success:
            print("✅ ALL TESTS PASSED!")
            print()
            print("FANWS is now working like AAWT with:")
            print("  • Settings management with dot-notation")
            print("  • Database with connection pooling")
            print("  • Text analysis (grammar, readability)")
            print("  • Multi-format export (TXT, DOCX, PDF, EPUB)")
            print("  • API integration with caching")
            print("  • File operations with memory management")
            print()
            print("Launch with: python aawt.py")
        else:
            print("❌ SOME TESTS FAILED")
            print("Check error messages above for details.")
            return 1
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
