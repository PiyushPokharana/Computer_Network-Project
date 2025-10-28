# Quick Test Script for Federated Learning System
# This script helps verify the setup is working correctly

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import torch
        print("  ✓ torch imported successfully")
        print(f"    PyTorch version: {torch.__version__}")
    except ImportError as e:
        print(f"  ✗ Failed to import torch: {e}")
        return False
    
    try:
        import socket
        print("  ✓ socket module available")
    except ImportError as e:
        print(f"  ✗ Failed to import socket: {e}")
        return False
    
    try:
        import pickle
        print("  ✓ pickle module available")
    except ImportError as e:
        print(f"  ✗ Failed to import pickle: {e}")
        return False
    
    return True

def test_model():
    """Test if the model can be instantiated"""
    print("\nTesting model...")
    try:
        from model_def import SimpleNet
        model = SimpleNet()
        print("  ✓ SimpleNet instantiated successfully")
        
        import torch
        x = torch.randn(10, 10)
        output = model(x)
        print(f"  ✓ Forward pass successful, output shape: {output.shape}")
        
        return True
    except Exception as e:
        print(f"  ✗ Model test failed: {e}")
        return False

def test_protocol():
    """Test the length-prefix protocol functions"""
    print("\nTesting communication protocol...")
    try:
        import pickle
        import torch
        from model_def import SimpleNet
        
        # Test data serialization
        model = SimpleNet()
        state_dict = model.state_dict()
        data_bytes = pickle.dumps(state_dict)
        length_bytes = len(data_bytes).to_bytes(4, 'big')
        
        print(f"  ✓ State dict serialization successful")
        print(f"    Serialized size: {len(data_bytes)} bytes")
        print(f"    Length prefix: {length_bytes.hex()}")
        
        # Test deserialization
        recovered_length = int.from_bytes(length_bytes, 'big')
        recovered_state = pickle.loads(data_bytes)
        
        print(f"  ✓ Deserialization successful")
        print(f"    Recovered length: {recovered_length} bytes")
        
        return True
    except Exception as e:
        print(f"  ✗ Protocol test failed: {e}")
        return False

def test_config():
    """Check configuration values"""
    print("\nChecking configuration...")
    
    # Check server config
    HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
    PORT = int(os.environ.get("SERVER_PORT", "5000"))
    NUM_CLIENTS = int(os.environ.get("NUM_CLIENTS", "2"))
    MIN_CLIENTS = int(os.environ.get("MIN_CLIENTS", "2"))
    
    print(f"  Server configuration:")
    print(f"    HOST: {HOST}")
    print(f"    PORT: {PORT}")
    print(f"    NUM_CLIENTS: {NUM_CLIENTS}")
    print(f"    MIN_CLIENTS: {MIN_CLIENTS}")
    
    if MIN_CLIENTS > NUM_CLIENTS:
        print(f"  ⚠ WARNING: MIN_CLIENTS ({MIN_CLIENTS}) > NUM_CLIENTS ({NUM_CLIENTS})")
        print(f"    This means aggregation will never happen!")
        return False
    
    if MIN_CLIENTS < 2:
        print(f"  ⚠ WARNING: MIN_CLIENTS ({MIN_CLIENTS}) < 2")
        print(f"    Federated learning works best with at least 2 clients")
    
    print(f"  ✓ Configuration looks good")
    return True

def main():
    print("="*60)
    print("Federated Learning System - Quick Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Model", test_model()))
    results.append(("Protocol", test_protocol()))
    results.append(("Config", test_config()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Start the server: python server.py")
        print("2. Run client(s): python client.py")
        print("   (Make sure to update SERVER_IP in client.py first!)")
    else:
        print("\n✗ Some tests failed. Please fix the issues before running.")
        sys.exit(1)

if __name__ == "__main__":
    main()
