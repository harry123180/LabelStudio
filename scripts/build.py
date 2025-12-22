#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LabelStudio Build Script
Builds frontend and packages everything into a Windows executable
"""
import subprocess
import shutil
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')


def clean():
    """Clean previous build artifacts"""
    print("[1/5] Cleaning previous build...")
    for folder in ['dist', 'build', 'output']:
        path = os.path.join(ROOT_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"  Removed {folder}/")

    # Also clean PyInstaller artifacts
    for folder in ['dist', 'build']:
        path = os.path.join(SCRIPTS_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path)


def build_frontend():
    """Build Vue frontend"""
    print("[2/5] Building frontend...")

    # Check if node_modules exists
    node_modules = os.path.join(FRONTEND_DIR, 'node_modules')
    if not os.path.exists(node_modules):
        print("  Installing dependencies...")
        subprocess.run(['npm', 'install'], cwd=FRONTEND_DIR, shell=True, check=True)

    # Build
    subprocess.run(['npm', 'run', 'build'], cwd=FRONTEND_DIR, shell=True, check=True)

    # Move dist to root
    src = os.path.join(FRONTEND_DIR, 'dist')
    dst = os.path.join(ROOT_DIR, 'dist')
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"  Frontend built: {dst}")


def install_backend_deps():
    """Install backend dependencies"""
    print("[3/5] Checking backend dependencies...")
    requirements = os.path.join(BACKEND_DIR, 'requirements.txt')
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', '-r', requirements, '-q'
    ], check=True)


def build_executable():
    """Build executable with PyInstaller"""
    print("[4/5] Building executable...")

    spec_file = os.path.join(SCRIPTS_DIR, 'labelstudio.spec')
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        spec_file
    ], cwd=SCRIPTS_DIR, shell=True, check=True)


def package():
    """Package final output"""
    print("[5/5] Packaging...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Copy executable
    exe_src = os.path.join(SCRIPTS_DIR, 'dist', 'LabelStudio.exe')
    exe_dst = os.path.join(OUTPUT_DIR, 'LabelStudio.exe')

    if os.path.exists(exe_src):
        shutil.copy(exe_src, exe_dst)
        print(f"  Executable: {exe_dst}")

        # Get file size
        size_mb = os.path.getsize(exe_dst) / (1024 * 1024)
        print(f"  Size: {size_mb:.1f} MB")
    else:
        print("  ERROR: Executable not found!")
        return False

    return True


def main():
    print("=" * 60)
    print("  LabelStudio Build Script")
    print("=" * 60)

    try:
        clean()
        build_frontend()
        install_backend_deps()
        build_executable()
        success = package()

        print("")
        print("=" * 60)
        if success:
            print("  BUILD SUCCESSFUL!")
            print(f"  Output: {os.path.join(OUTPUT_DIR, 'LabelStudio.exe')}")
        else:
            print("  BUILD FAILED!")
        print("=" * 60)

    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
