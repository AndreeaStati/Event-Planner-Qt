
## 🔧 Instalare și rulare

 1. Instalează Python 3.10+

 2. Clonează repo-ul:
```bash
git clone https://github.com/AndreeaStati/Event-Planner-Qt.git
cd Event-Planner-Qt/
```

 3. Creează și activează un mediu virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

 4. Instalează dependențele
```bash
pip install --upgrade pip
pip install PySide6
```

 5. Instalează pachetele necesare pentru Qt (DOAR Linux – Ubuntu/Debian)
```bash
sudo apt update
sudo apt install \
    libxcb-xinerama0 \
    libxcb-xinerama0-dev \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-xfixes0 \
    libxrender1 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-cursor0
```
Se execută o singură dată pe sistem, nu per proiect.
 
 6. Ruleaza aplicatia
```bash
python main.py
```
