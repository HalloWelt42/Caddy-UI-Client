# UI Anpassungs-Guide für Caddy Manager

## 1. Tabellen-Anpassungen

### Zeilenhöhe ändern
```python
# In jedem Widget mit QTableWidget:
self.table.verticalHeader().setDefaultSectionSize(60)  # Pixel-Höhe
```

### Spaltenbreite anpassen
```python
# Feste Breite:
self.table.setColumnWidth(0, 200)  # Spalte 0, 200 Pixel

# Automatische Anpassung:
header = self.table.horizontalHeader()
header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Füllt verfügbaren Platz
header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Passt sich Inhalt an
header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Feste Breite
```

### Zeilen-Farben alternieren
```python
self.table.setAlternatingRowColors(True)  # Aktiviert abwechselnde Farben
```

## 2. Button-Anpassungen

### Button-Größe
```python
button = QPushButton("Text")
button.setFixedSize(100, 40)  # Breite, Höhe in Pixel
button.setMinimumHeight(40)   # Mindesthöhe
button.setMaximumWidth(200)   # Maximalbreite
```

### Button-Stil mit ObjectName
```python
# Im Widget:
button.setObjectName("primaryButton")  # Setzt CSS-Klasse

# In dark_theme.py anpassen:
QPushButton#primaryButton {
    background-color: #0d7377;
    color: white;
    border: none;
    padding: 10px 20px;  /* Mehr Padding für größere Buttons */
}
```

### Icons zu Buttons
```python
import qtawesome as qta

# Icon mit Farbe
button = QPushButton(qta.icon('fa5s.play', color='#27ae60'), "Start")

# Icon-Größe anpassen
icon = qta.icon('fa5s.save', color='white', options=[{'scale_factor': 1.5}])
button.setIcon(icon)
```

## 3. Farben ändern

### In dark_theme.py

```python
# Hauptfarben ändern:
QWidget {
    background-color: #1e1e1e;  /* Hintergrund */
    color: #e0e0e0;             /* Text */
}

# Akzentfarbe (Türkis) ändern:
# Suche und ersetze alle Vorkommen von #0d7377 mit deiner Farbe

# Status-Farben:
.status-running { background-color: #27ae60; }  /* Grün */
.status-stopped { background-color: #c0392b; }  /* Rot */
.status-error { background-color: #e67e22; }    /* Orange */
```

### Inline-Farben in Widgets
```python
# Text-Farbe
label.setStyleSheet("color: #ff0000;")  # Rot

# Hintergrund
widget.setStyleSheet("background-color: #2d2d2d;")

# Kombiniert
widget.setStyleSheet("""
    background-color: #2d2d2d;
    color: white;
    border: 2px solid #0d7377;
    border-radius: 8px;
    padding: 10px;
""")
```

## 4. Layout-Anpassungen

### Abstände (Spacing)
```python
layout = QVBoxLayout()
layout.setSpacing(10)  # Pixel zwischen Elementen
layout.setContentsMargins(10, 10, 10, 10)  # Links, Oben, Rechts, Unten
```

### Widget-Größen
```python
widget.setMinimumSize(300, 200)  # Minimalgröße
widget.setMaximumSize(800, 600)  # Maximalgröße
widget.setFixedSize(400, 300)    # Feste Größe
```

## 5. Schriften

### Global in dark_theme.py
```python
QWidget {
    font-family: "SF Pro Display", -apple-system, sans-serif;
    font-size: 14px;  /* Basis-Schriftgröße */
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: 600;
}
```

### Inline für einzelne Widgets
```python
font = QFont()
font.setPointSize(16)
font.setBold(True)
font.setFamily("Monaco")
widget.setFont(font)
```

## 6. Icons anpassen

### Verfügbare Icon-Sets in QtAwesome
- `fa5s` - Font Awesome 5 Solid
- `fa5r` - Font Awesome 5 Regular
- `fa5b` - Font Awesome 5 Brands
- `mdi` - Material Design Icons

### Icon-Suche
```python
# Alle verfügbaren Icons anzeigen:
import qtawesome as qta
print(qta.icon_browser.run())  # Öffnet Icon-Browser
```

### Icon-Optionen
```python
icon = qta.icon('fa5s.cog',
    color='#ffffff',           # Farbe
    color_active='#00ff00',    # Farbe beim Hover
    options=[{
        'scale_factor': 1.5,   # Größe
        'opacity': 0.8         # Transparenz
    }]
)
```

## 7. Clickable Links (wie in Routes)

```python
# Item als Link stylen
item.setForeground(Qt.GlobalColor.blue)
font = item.font()
font.setUnderline(True)
item.setFont(font)

# URL speichern
item.setData(Qt.ItemDataRole.UserRole, "https://example.com")

# Click-Handler
def on_item_clicked(item):
    if item.column() == 0:  # Nur erste Spalte
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            QDesktopServices.openUrl(QUrl(url))
```

## 8. Status-Indikatoren

### Farbige Status-Badges
```python
def set_status_color(item, status):
    if status == "running":
        item.setForeground(Qt.GlobalColor.green)
        item.setText("● Running")  # Mit Punkt
    elif status == "stopped":
        item.setForeground(Qt.GlobalColor.red)
        item.setText("● Stopped")
```

### Custom Status Widget
```python
class StatusBadge(QLabel):
    def __init__(self, status="unknown"):
        super().__init__()
        self.set_status(status)
    
    def set_status(self, status):
        styles = {
            "running": "background: #27ae60; color: white;",
            "stopped": "background: #c0392b; color: white;",
            "unknown": "background: #95a5a6; color: white;"
        }
        self.setStyleSheet(f"""
            {styles.get(status, styles['unknown'])}
            padding: 5px 10px;
            border-radius: 12px;
        """)
        self.setText(status.upper())
```

## 9. Tooltips

```python
widget.setToolTip("Hilfreicher Text")
widget.setToolTipDuration(5000)  # 5 Sekunden

# HTML in Tooltips
widget.setToolTip("""
    <b>Fett</b><br>
    <i>Kursiv</i><br>
    <span style='color: red;'>Rot</span>
""")
```

## 10. Wo finde ich was?

### Farben & Themes
- `client/ui/styles/dark_theme.py` - Globale Styles

### Widget-spezifische Anpassungen
- `client/ui/widgets/dashboard.py` - Dashboard Layout
- `client/ui/widgets/route_manager.py` - Routes Tabelle
- `client/ui/widgets/docker_manager.py` - Docker Tabelle

### Fenster-Layout
- `client/ui/windows/main_window.py` - Hauptfenster, Tabs, Menüs

### Icons
- Font Awesome Cheatsheet: https://fontawesome.com/v5/cheatsheet
- In Code: `qta.icon('fa5s.ICON_NAME')`

## Beispiel: Button größer und grüner machen

```python
# In deinem Widget:
button = QPushButton(qta.icon('fa5s.check', color='white'), "Bestätigen")
button.setObjectName("bigGreenButton")
button.setMinimumHeight(50)

# In dark_theme.py ergänzen:
QPushButton#bigGreenButton {
    background-color: #27ae60;
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 15px 30px;
    border-radius: 8px;
}

QPushButton#bigGreenButton:hover {
    background-color: #2ecc71;
}
```

## Tipp: Live-Reload für Style-Änderungen

Füge diese Funktion zu main_window.py hinzu:
```python
def reload_styles(self):
    """Lädt Styles neu (F5 drücken)"""
    from client.ui.styles.dark_theme import DARK_THEME_STYLE
    self.setStyleSheet(DARK_THEME_STYLE)

# In __init__:
reload_action = QAction("Reload Styles", self)
reload_action.setShortcut("F5")
reload_action.triggered.connect(self.reload_styles)
self.addAction(reload_action)
```

Dann kannst du mit F5 die Styles neu laden ohne Neustart!