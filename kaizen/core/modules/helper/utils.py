from dotenv import load_dotenv

load_dotenv()


IGNORE_DIRS = [
    # Version Control & IDEs
    ".git",
    ".github",
    ".svn",
    ".hg",
    ".idea",
    ".vscode",
    ".settings",
    ".vs",
    # Package Managers & Dependencies
    "node_modules",
    "bower_components",
    "vendor",
    "site-packages",
    "vendor/bundle",
    # Python Build/Cache/Test
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "egg-info",
    "htmlcov",
    ".ipynb_checkpoints",
    # JS/TS Build/Cache
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".docusaurus",
    ".cache",
    # Rust / Java / C++ Build/Cache
    "target",
    ".gradle",
    "bin",
    "obj",
    "cmake-build-debug",
    "cmake-build-release",
    "ios/build",
    "android/build",
    ".expo",
    # General Output
    "coverage",
    "publish",
]


IGNORE_FILES = [
    # Environment Variables
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",
    # System files
    ".DS_Store",
    "Thumbs.db",
    # JS/TS Lockfiles
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    # Rust Lockfiles
    "Cargo.lock",
    # Ruby & PHP Lockfiles
    "Gemfile.lock",
    "composer.lock",
    # TS Build Info
    "tsconfig.tsbuildinfo",
]


IGNORE_EXTENSIONS = [
    # Media & Images
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".svg",
    # Documents
    ".pdf",
    # Archives & Zips
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    # Executables & Binaries
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".dmg",
    ".iso",
    # Databases
    ".db",
    ".sqlite",
    # Python Compiled
    ".pyc",
    ".pyo",
    ".pyd",
    # Java/Kotlin Compiled
    ".class",
    ".jar",
    ".war",
    ".ear",
    # C/C++ Compiled
    ".o",
    ".obj",
    ".a",
    ".lib",
    ".out",
    ".dylib",
    # C#/.NET Compiled
    ".pdb",
    ".suo",
    ".user",
]
