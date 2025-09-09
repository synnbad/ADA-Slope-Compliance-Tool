#!/usr/bin/env python3
"""
Startup script for ADA Slope Compliance Tool UI
"""
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        print("✓ Flask dependencies available")
        return True
    except ImportError:
        print("✗ Flask dependencies missing")
        return False

def install_dependencies():
    """Install UI dependencies"""
    print("Installing UI dependencies...")
    ui_dir = Path(__file__).parent
    requirements_file = ui_dir / "requirements.txt"
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def start_server():
    """Start the Flask development server"""
    print("\n" + "="*50)
    print("🚀 Starting ADA Slope Compliance Tool UI")
    print("="*50)
    print("📊 Web Interface: http://localhost:5000")
    print("🔧 API Endpoint: http://localhost:5000/api/")
    print("📁 Upload temp files to: temp_uploads/")
    print("💾 Results saved to: temp_outputs/")
    print("\n⚠️  Note: DEM files must be in projected coordinate system (meters)")
    print("📖 Use QGIS or gdalwarp to reproject geographic DEMs")
    print("="*50)
    
    # Import and run the server
    from server import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    print("ADA Slope Compliance Tool - UI Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("server.py").exists():
        print("❌ Error: Please run this script from the ui/ directory")
        print("   Current directory should contain server.py")
        sys.exit(1)
    
    # Check main project dependencies
    parent_dir = Path("..").resolve()
    main_requirements = parent_dir / "requirements.txt"
    
    if not main_requirements.exists():
        print("❌ Error: Main requirements.txt not found")
        print("   Make sure you're running from within the ADA-Slope-Compliance-Tool project")
        sys.exit(1)
    
    # Check Flask dependencies
    if not check_dependencies():
        print("\n📦 Installing UI dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please run manually:")
            print(f"   pip install -r {Path('requirements.txt').absolute()}")
            sys.exit(1)
    
    # Start the server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
