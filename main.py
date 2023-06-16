import sys
import pyqtgraph as pg
import matplotlib.pyplot as plt
from pyqtgraph import ImageView
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QUrl, QPoint
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData


class ReproductorMusica(QMainWindow):
    def __init__(self):
        super(ReproductorMusica, self).__init__()
        loadUi('reproductor_gui.ui', self)

        # variables
        self.clic_psicion = QPoint()
        self.estado = True
        self.play_list = []
        self.posicion = 0
        self.indice = ''
        self.num = 0

        # control de los botones
        self.bt_abrir.clicked.connect(self.abrir_archivo)
        self.bt_normal.hide()
        self.bt_pausa.hide()
        self.bt_volumen_0.hide()
        self.bt_volumen_100.hide()
        self.bt_reproducir.setEnabled(False)

        # Creamos el objeto player
        self.player = QMediaPlayer()
        self.player.setVolume(50)

        # Control de los botonoes y slider para la musica
        self.slider_tiempo.sliderMoved.connect(lambda x: self.player.setPosition(x))
        self.slider_volumen.valueChanged.connect(self.variar_volumen)
        self.player.positionChanged.connect(self.posicion_cancion)
        self.player.durationChanged.connect(self.duracion_cancion)
        self.player.stateChanged.connect(self.estado_tiempo)

        # control barra de titulos
        self.bt_minimizar.clicked.connect(lambda :self.showMinimized())
        self.bt_normal.clicked.connect(self.control_bt_normal)
        self.bt_maximizar.clicked.connect(self.control_bt_maximizar)
        self.bt_cerrar.clicked.connect(lambda: self.close())

        # control musica
        self.bt_reproducir.clicked.connect(self.reproducir_musica)
        self.bt_pausa.clicked.connect(self.pausar_musica)
        self.bt_atras.clicked.connect(self.retroceder_musica)
        self.bt_adelante.clicked.connect(self.adelantar_musica)
        
        self.lista_musica.doubleClicked.connect(self.reproducir_musica)
        self.lista_musica.clicked.connect(self.seleccion_canciones)

        # Eliminar barra y de titulo - opacidad
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.95)

        # SeizeGrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        # Mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        # Grafica
        self.graphWidget = pg.PlotWidget(title= 'SPECTRUM')
        self.grafica_layout.addWidget(self.graphWidget)
        self.espectrum_grafica()
        self.update_datos()

    def abrir_archivo(self):
        if len(self.play_list)>0:
            # self.play_list.clear()
            # self.lista_musica.clear()
            self.bt_reproducir.setEnabled(False)
        
        archivo = QFileDialog()
        archivo.setFileMode(QFileDialog.ExistingFiles)
        nombre = archivo.getOpenFileName(self, 'Abrir archivos de audio', filter= 'Audio Files (*.mp3 *.ogg *.wav)')
        
        self.musica = nombre[0]
        nombres_musica = []
        try:
            for music in nombre[0].split(';'):
                direccion = music.split('/')
                nombre_cancion = direccion[-1]
                nombres_musica.append(nombre_cancion)
            self.dir = '/'.join(direccion[:-1])
            self.lista_musica.addItems(nombres_musica)
        except UnboundLocalError:
            pass
    
    def reproducir_musica(self):
        if self.estado:
            self.estado = False
            self.bt_reproducir.hide()
            self.bt_pausa.show()
            self.indice = self.lista_musica.currentRow().__index__()
            path = self.lista_musica.currentItem().text()

            cancion_x = f'{self.dir}/{path}'
            print(cancion_x)
            url = QUrl.fromLocalFile(cancion_x)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.setPosition(self.posicion)
            self.play_list.append(path)
            
            if len(self.play_list)>2:
                self.play_list.pop(0)
            if self.lista_musica.currentItem().text() != self.play_list[0]:
                self.posicion = 0
                self.player.setPosition(self.posicion)
            self.player.play()
        else:
            self.pausar_musica()
            self.estado = True
        
    def metadata_cancion(self):
        if self.player.isMetaDataAvailable():
            titulo = self.player.metaData(QMediaMetaData.Title)
            artista = self.player.metaData(QMediaMetaData.AlbumArtist)
            genero = self.player.metaData(QMediaMetaData.Genre)
            annio = str(self.player.metaData(QMediaMetaData.Year))

            self.titulo_cancion.setText(f'TITULO: {titulo}')
            self.artista_cancion.setText(f'ARTISTA: {artista}')
            self.genero_cancion.setText(f'GENERO: {genero}')
            self.annio_cancion.setText(f'AÑO: {annio}')
    
    def pausar_musica(self):
        if self.estado:
            self.estado = False
            self.player.pause()
            self.posicion = self.player.position()
            self.bt_reproducir.show()
            self.bt_pausa.hide()

    def seleccion_canciones(self):
        self.estado = True
        self.bt_reproducir.show()
        self.bt_pausa.hide()
        self.bt_reproducir.setEnabled(True)
   
    def adelantar_musica(self):
        self.estado = True
        try:
            self.lista_musica.setCurrentRow(self.indice+1)
            self.reproducir_musica()
        except AttributeError:
            pass
    
    def retroceder_musica(self):
        self.estado = True
        try:
            self.lista_musica.setCurrentRow(self.indice-1)
            self.reproducir_musica()
        except AttributeError:
            pass

    def estado_tiempo(self, estado):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.bt_reproducir.hide()
            self.bt_pausa.show()
            self.estado = True
        else:
            self.bt_reproducir.show()
            self.bt_pausa.hide()
            self.estado = False
        if self.player.position() == self.player.duration() and not self.player.position()==0:
            try:
                self.estado = True
                self.lista_musica.setCurrentRow(self.indice+1)
                self.reproducir_musica()
            except:
                pass
          
    def duracion_cancion(self, t):
        self.slider_tiempo.setRange(0,t)
        m, s = (divmod(t*0.001, 60))
        self.indicador_tiempo.setText(str(f'{int(m)}:{int(s)}'))


    def posicion_cancion(self, t):
        self.slider_tiempo.setValue(t)
        m, s = divmod(t*0.001, 60)
        self.indicador_posicion.setText(str(f'{int(m)}:{int(s)}'))

    def variar_volumen(self, valor):
        self.player.setVolume(valor)
        self.indicador_volumen.setText(str(valor))
        if valor==0:
            self.bt_volumen_0.show()
            self.bt_volumen_50.hide()
            self.bt_volumen_100.hide()
        elif valor>0 and valor<50:
            self.bt_volumen_0.hide()
            self.bt_volumen_50.show()
            self.bt_volumen_100.hide()
        elif valor>=50:
            self.bt_volumen_0.hide()
            self.bt_volumen_50.hide()
            self.bt_volumen_100.show()
    
    def espectrum_grafica(self):
        x = np.linspace(0, 100,10)
        self.data = np.random.normal(size=(10,100))

        self.curva = self.graphWidget.plot(x, np.sin(x),symbol='o', color='#b012eb', pen='#b012eb', width= 2, brush='g', symbolBrush='#b012eb', symbolPen='#b012eb', symbolSize=10)
        self.graphWidget.hideAxis('left')
        self.graphWidget.hideAxis('bottom')
        # self.graphWidget.showGrid(x=True, y=True)
        # self.graphWidget.setBackground('101010')
        # self.graphWidgetsetLabels(left="AMPLITUD", bottom="TIEMPO")

    def update_datos(self):
        self.metadata_cancion()
        self.curva.setData(self.data[self.num % 10])
        if self.num == 0:
            self.graphWidget.enableAutoRange('xy', False)
        self.num +=1
        QtCore.QTimer.singleShot(100, self.update_datos)

    def control_bt_normal(self):
        self.showNormal()
        self.bt_normal.hide()
        self.bt_maximizar.show()
    
    def control_bt_maximizar(self):
        self.showMaximized()
        self.bt_maximizar.hide()
        self.bt_normal.show()

    ## SizeGrip
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)
    
    ## Mover ventana
    def mousePressEvent(self, event):
        self.clic_psicion = event.globalPos()

    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.clic_psicion)
                self.clic_psicion = event.globalPos()
        if event.globalPos().y() <=5 or event.globalPos().x() <=5:
            self.showMaximized()
            self.bt_maximizar.hide()
            self.bt_normal.show()
        else:
            self.showNormal()
            self.bt_normal.hide()
            self.bt_maximizar.show()

if __name__== '__main__':
    app = QApplication(sys.argv)
    mi_app = ReproductorMusica()
    mi_app.show()
    sys.exit(app.exec_()) 