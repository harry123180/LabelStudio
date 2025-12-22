# -*- coding: utf-8 -*-
"""
LabelStudio - Main Entry Point
"""
import os
import sys
import webbrowser
import threading
from app import create_app, get_data_dir
from app.utils.network import get_local_ip


def main():
    """Main entry point"""
    host = '0.0.0.0'
    port = 5000
    local_ip = get_local_ip()

    # Set data directory
    data_dir = get_data_dir()
    os.environ['LABELSTUDIO_DATA_DIR'] = data_dir

    # Print startup info
    print("=" * 55)
    print("  LabelStudio 標註工具")
    print("  LabelStudio Annotation Tool")
    print("=" * 55)
    print(f"  本機存取 Local:    http://localhost:{port}")
    print(f"  區網存取 Network:  http://{local_ip}:{port}")
    print(f"  資料目錄 Data:     {data_dir}")
    print("=" * 55)
    print("  按 Ctrl+C 停止服務 / Press Ctrl+C to stop")
    print("=" * 55)

    # Auto open browser after 1.5 seconds
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()

    # Create and run app
    app = create_app()

    # Initialize database
    with app.app_context():
        from app import db
        db.create_all()

    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    main()
