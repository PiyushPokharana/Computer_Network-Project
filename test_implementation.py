"""
Quick test script to verify all implementations are working

Run this after implementing all features to check:
1. Server imports work
2. Visualization tools can be imported
3. All required files exist
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import server
        print("  ✓ server.py imports successfully")
    except Exception as e:
        print(f"  ✗ server.py import failed: {e}")
        return False
    
    try:
        import visualize_training
        print("  ✓ visualize_training.py imports successfully")
    except Exception as e:
        print(f"  ✗ visualize_training.py import failed: {e}")
        return False
    
    try:
        import visualize_metrics
        print("  ✓ visualize_metrics.py imports successfully")
    except Exception as e:
        print(f"  ✗ visualize_metrics.py import failed: {e}")
        return False
    
    try:
        import visualize_all
        print("  ✓ visualize_all.py imports successfully")
    except Exception as e:
        print(f"  ✗ visualize_all.py import failed: {e}")
        return False
    
    try:
        import monitor
        print("  ✓ monitor.py imports successfully")
    except Exception as e:
        print(f"  ✗ monitor.py import failed: {e}")
        return False
    
    return True

def test_server_features():
    """Test that server has new features"""
    print("\nTesting server features...")
    
    try:
        from server import MetricsCollector
        print("  ✓ MetricsCollector class exists")
        
        # Test instantiation
        metrics = MetricsCollector()
        print("  ✓ MetricsCollector can be instantiated")
        
        # Test methods
        assert hasattr(metrics, 'start_round'), "Missing start_round method"
        assert hasattr(metrics, 'end_round'), "Missing end_round method"
        assert hasattr(metrics, 'record_send'), "Missing record_send method"
        assert hasattr(metrics, 'record_receive'), "Missing record_receive method"
        assert hasattr(metrics, 'save_metrics'), "Missing save_metrics method"
        assert hasattr(metrics, 'print_summary'), "Missing print_summary method"
        print("  ✓ All required methods exist")
        
        return True
    except Exception as e:
        print(f"  ✗ Server feature test failed: {e}")
        return False

def test_files_exist():
    """Test that all required files exist"""
    print("\nChecking required files...")
    
    required_files = [
        'server.py',
        'client.py',
        'model_def.py',
        'data_utils.py',
        'visualize_training.py',
        'visualize_metrics.py',
        'visualize_all.py',
        'monitor.py',
        'view_parameters.py',
        'requirements.txt'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (missing)")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("="*60)
    print("Testing Federated Learning Implementation")
    print("="*60)
    
    results = {
        'imports': test_imports(),
        'server_features': test_server_features(),
        'files': test_files_exist()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Implementation is complete.")
        print("\nNext steps:")
        print("  1. Run server: python server.py")
        print("  2. Run clients: python client.py")
        print("  3. Monitor training: python monitor.py")
        print("  4. Visualize results: python visualize_all.py")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
