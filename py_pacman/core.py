#Install Dependents

import importlib
import importlib.util
import subprocess
import sys

def p_load(*packages):
    """
    Load packages, installing them if missing.
    Supports aliases: ('pandas', 'pd')
    Mimics R's pacman::p_load behavior.
    """

    for pkg in packages:
        # Handle tuple input for alias support
        if isinstance(pkg, tuple):
            name, alias = pkg
        else:
            name, alias = pkg, pkg

        # Handle submodules (e.g. matplotlib.pyplot)
        base_pkg = name.split('.')[0]

        # Check if installed
        if importlib.util.find_spec(base_pkg) is None:
            print(f"📦 Installing missing package: {base_pkg}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", base_pkg])
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {base_pkg}. Skipping.")
                continue
        else:
            print(f"✅ {base_pkg} already installed.")

        # Import the module
        try:
            module = importlib.import_module(name)
            # Warn if alias already exists
            if alias in globals():
                print(f"⚠️ Alias '{alias}' already exists and will be overwritten.")
            globals()[alias] = module
            print(f"📚 Loaded {name} as '{alias}'")
        except Exception as e:
            print(f"❌ Failed to import {name}: {e}")


def p_load_v(*packages):
    """
    Load packages with optional versioning (e.g. 'pandas==2.2.1').
    Supports aliases: ('pandas==2.2.1', 'pd')
    """

    for pkg in packages:
        if isinstance(pkg, tuple):
            name, alias = pkg
        else:
            name, alias = pkg, pkg

        # Handle versioned installs
        if '==' in name:
            base_pkg = name.split('==')[0]
            version = name.split('==')[1]
        else:
            base_pkg, version = name, None

        # Check if already installed
        spec = importlib.util.find_spec(base_pkg)
        reinstall = False

        if spec is None:
            print(f"📦 Installing missing package: {name}")
        elif version:
            # Check if installed version matches
            try:
                installed_version = importlib.import_module(base_pkg).__version__
                if installed_version != version:
                    print(f"⚠️ Version mismatch for {base_pkg}: {installed_version} != {version}")
                    reinstall = True
            except AttributeError:
                print(f"⚠️ Could not check version for {base_pkg}, reinstalling just in case.")
                reinstall = True

        # Install (or reinstall with version)
        if spec is None or reinstall:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", name])
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {name}. Skipping.")
                continue

        # Import
        try:
            module = importlib.import_module(base_pkg)
            if alias in globals():
                print(f"⚠️ Alias '{alias}' already exists and will be overwritten.")
            globals()[alias] = module
            print(f"📚 Loaded {base_pkg} as '{alias}' (version {getattr(module, '__version__', 'unknown')})")
        except Exception as e:
            print(f"❌ Failed to import {base_pkg}: {e}")