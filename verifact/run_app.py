import sys
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt
from verifact.gui import App
from pathlib import Path

def run():
    app = QApplication(sys.argv)
    splash = QSplashScreen(img_splash())
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
    splash.show()
    app.processEvents() 
    
    window = App()
    window.show()
    splash.finish(window)
    sys.exit(app.exec())
    
def img_splash():
    img = Path(__file__).parent.parent / "images" / "splash.png"
    pixmap = QPixmap(img).scaled(400, 300, Qt.KeepAspectRatio)
    
    # Modifie la police et couleur du texte
    color = QColor(205, 92, 92)
    font = QFont()
    font.setBold(True)
    font.setPointSize(10)
    
    # Créer un QPainter pour dessiner sur le QPixmap
    painter = QPainter(pixmap)
    painter.setFont(font)
    painter.setPen(color)
    
    # Dessiner le texte
    text_rect = pixmap.rect()
    text_rect.moveTop(pixmap.rect().top() + 57)  # Décale le texte de x pixels vers le bas
    painter.drawText(text_rect, Qt.AlignHCenter, "Chargement...")
    painter.end()
    
    return pixmap