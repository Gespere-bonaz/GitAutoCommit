# Git Auto Commit

## 📌 Introduction

Git Auto Commit is a tool that automatically commits modified files with a confirmation prompt.
If no commit is made within 15 minutes after detecting changes, a message and a modal are displayed to the user as a reminder to perform the commit.

This tool is especially useful for developers who frequently modify files and want to ensure their changes are committed regularly without manual intervention.

---

## 📂 Project Structure

```
git_observer/
│── git_observer/              # Source code directory
│   ├── __init__.py          # Initialization file
│   ├── git_handler.py       # Git commit handling module
│   ├── git_observer/        # File monitoring system
│   ├── main.py              # Main script
│
│── setup.py                 # Package configuration file
│── README.md                # Project documentation
│── LICENSE                  # Open-source license
│── requirements.txt          # Project dependencies
│── pyproject.toml            # (Optional, recommended for packaging)
│── tests/                    # Unit tests (Optional)
│
│── .gitignore                # Excludes unnecessary files
```

---

## 🔧 Installation

### 📥 Install from GitHub

```bash
git clone https://github.com/k2pme/gitobserver.git
cd gitobserver
pip install -r requirements.txt
python git_observer/main.py ou python -m git_observer.main
```

### 📦 Install via pip

Once the package is published on PyPI:

```bash
pip install gitobserver
python git_observer/main.py ou python -m git_observer.main
```

---

After installation, you don’t need to manually import the git_observer folder into your projects.
Just run the following command from your project directory :

```bash
python -m git_observer.main
```

Ou

```bash
python git_observer/main.py
```

---

## 👥 Contributors

- **k2pme** - [GitHub Profile](https://github.com/k2pme)
- **Gespere-bonaz** - [GitHub Profile](https://github.com/Gespere-bonaz)

We welcome contributions from the community! 🚀

---

## 💡 How to Contribute

We appreciate your help in improving this project. Follow these steps to contribute:

1. **Fork the repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/git-auto-commit.git
   ```
3. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature-name
   ```
4. **Make your changes** and commit them:
   ```bash
   git commit -m "Added a new feature"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature-name
   ```
6. **Create a pull request** from your branch to the main repository.

---

## 🙏 Acknowledgments

Special thanks to all contributors and open-source maintainers who make projects like this possible.

If you find this project helpful, please ⭐ star the repository on GitHub!

---

### 📧 Contact

For any inquiries or feature requests, feel free to open an issue or contact us via GitHub.

🚀 Happy Coding!# gitobserver
