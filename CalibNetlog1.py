import sys
import requests
import datetime
import time
import argparse
import pandas as pd
from configparser import ConfigParser
import matplotlib.pyplot as plt

import numpy as np



from Netlog import *
from Conexion import *
from ping3 import ping

#########################################################################################
class ControlMainWindows(QtWidgets.QMainWindow):

    intentos = 0
    comm = 0
    config = {'IP': '192.168.0.245', "Sentido": "BackWard", "Modo": "Lineal", "Tiempo" : "5"}
    archivo ={}
    y = []
    x = []

#########################################################################################
    def Actualizar(self):

        conexion = self.comm.get_conectado()
        print(conexion)
       #contador = self.comm.getCounter()
        if conexion == 1:
            self.intentos = 0
            self.ui.medidoRed.setStyleSheet("QLabel { color : green; }")
            self.ui.medidoRed.setText("CONECTADO")
            contador = self.comm.getCounter()
            if contador != "Error":                             #ver que hace counter en el k64
               self.ui.medidoRaw.setText(contador[0][8::])
               if self.ui.tabWidget.currentIndex() == 0:        # Es lineal?
                   altura = self.comm.getHeigtLin()             #Lee Altura Lineal
                   self.write_csv(altura)                       #Guarda altura en el archivo
                   self.grafico(altura)
                   #print(altura)
                   if str(altura)[2:7] != "Error":
                       self.ui.medidoPhysic.setText(altura[2][:-5])
                       parametros= self.comm.getParametersLin()
                       if str(parametros)[2:7] != "Error":
                           self.ui.medidoStatusLineal.setText("Encoder " + parametros[4])
                           m = float(parametros[3]) * 4
                           if self.ui.tabLineales.currentIndex() == 0:

                               self.ui.medidoM.setText("(" + str(m) + ")")
                               self.ui.medido1.setText("(" + parametros[0][:-5] + ")")
                            #   self.ui.medido.setText("(" + str(int(parametros[0][:-5]) + 10000) + ")")
                           elif self.ui.tabLineales.currentIndex() == 1:
                               self.ui.medidoM_2.setText("(" + str(m) + ")")
                               self.ui.medido1_2.setText("(" + parametros[0][:-5] + ")")

                       else:
                           pass  # print "Error getParametersLin"
                   else:
                        pass  # print "Error getHeightLin"
            # Valores de la pestaña Rig Description

               elif  self.ui.tabWidget.currentIndex() == 1:  # esta activo RD
                   altura = self.comm.getHeightDrw()             # Lee Altura RD
                   self.write_csv(altura)                        #Guarda altura en el archivo
                   self.grafico(altura)
                   if str(altura) != "Error":
                       # print "getHeightDrw return: %s" % altura
                       if str(altura) == "ERROR":
                           self.ui.medidoPhysic.setText("0")
                       else:
                           self.ui.medidoPhysic.setText(altura[2][:-5])
                           parametros = self.comm.getParametersDrw()
                          # print(parametros)
                           if str(parametros) != "Error":
                                #print ("getParametersDrw return: %s" % parametros)
                                self.ui.medidoStatusRig.setText("Encoder " + parametros[5])
                                ppr = int(parametros[0]) / 4
                                self.ui.medidoPpr.setText("(" + str(ppr) + ")")
                                self.ui.medidoDiametro.setText("(" + parametros[1][:-2] + ")")
                                self.ui.medidoCable.setText("(" + parametros[2][:-2] + ")")
                                self.ui.medidoHpc.setText("(" + parametros[3] + ")")
                                self.ui.medidoAparejo.setText("(" + parametros[4] + ")")
                           else:
                                pass  # print "Error getParametersDrw"
                   else:
                       pass  # print "Error getHeightDrw"

        else:

            if self.intentos == 5:
                self.ui.medidoRed.setStyleSheet("QLabel { color : red; }")
                self.ui.medidoRed.setText("NO CONECTADO")
                self.comm.set_conectado(0)
            else:
                self.intentos = self.intentos + 1
                print (self.intentos)


            delay = ping(self.config['IP'], timeout=10)

            print(delay)
            if delay is not None :
                self.comm.set_conectado(1)
                self.ui.medidoRed.setStyleSheet("QLabel { color : green; }")
                self.ui.medidoRed.setText("CONECTADO")
                if (self.config['Sentido'] == "ForWard"):
                    sentido = self.comm.setCounterForWard()
                    print(sentido)
                elif (self.config['Sentido'] == "BackWard"):
                    sentido = self.comm.setCounterBackWard()
                    print(sentido)

            else:
                self.comm.set_conectado(0)
                self.ui.medidoRed.setStyleSheet("QLabel { color : red; }")
                self.ui.medidoRed.setText("NO CONECTADO")



###############################################################################
    def hora(self):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y %H:%M:%S')
        return st

###############################################################################
    def write_csv(self, altura):
        tiempo = self.hora()
        self.archivo = pd.read_csv('example.csv', header=0, index_col='Tiempo')
        self.archivo._set_value(tiempo, 'Altura', altura[2])
        self.archivo.to_csv('example.csv', encoding='utf-8')


###############################################################################

    def grafico(self, altura):

         plt.ion() # decimos de forma explícita que sea interactivo
         plt.xlabel('Tiempo')
         plt.grid()
         #plt.margins()
         plt.ylim(0,4000)

         self.y.append(int(altura[2][:-5]))    # los datos que vamos a dibujar y a actualizar

         tiempo= self.hora()
         tiempo= tiempo[11:]
         self.x.append(tiempo)

         # self.y= altura[2]  #y.append(np.random.randn(1))  # añadimos un valor aleatorio a la lista 'y'
                                       # Estas condiciones las he incluido solo para dibujar los últimos
                                        # 10 datos de la lista 'y' ya que quiero que en el gráfico se
                                         # vea la evolución de los últimos datos
         #plt.locator_params('x', tight=True, nbins=5)
         plt.xticks(range(0,500,100))
         if len(self.y) >= 500:
             self.y.pop(0)
             self.x.pop(0)
      #   if len(self.y) <= 500:
         plt.plot(self.x,self.y,scaley=False)
      #   else:
      #        plt.plot(self.x[-500:],self.y[-500:],scaley=False)

         plt.pause(0.01)  # esto pausará el gráfico
         plt.cla()  # esto limpia la información del axis (el área blanca donde
                      # se pintan las cosas.





###############################################################################
    def clickExit(self):
        sys.exit(app.exec_())

###############################################################################
    def clickEnviarPunto1(self):
        inPto1 = self.ui.entrada1.displayText()
        try:
            pto1 = float(inPto1)
        except ValueError:
            self.ui.estado.setText("Altura Referencia 1 no es un real")
            return
        rta = self.comm.setRef2(str(inPto1))
        rtastr = ','.join(rta)
        print(rtastr)
        if rtastr == 'Operación Realizada.':
            tiempo = self.hora()
            self.ui.entrada1.clear()
            self.ui.estado.setText("Punto 1 enviado correctamente " + tiempo)

###############################################################################

    def clickEnviarPunto2(self):
        inPto2 = self.ui.entrada2.displayText()
        try:
            pto2 = float(inPto2)
        except ValueError:
            self.ui.estado.setText("Altura Referencia 2 no es un real")
            return
        rta = self.comm.setRef1(str(inPto2))
        rtastr = ','.join(rta)
        print(rtastr)
        if rtastr == 'ERROR X2-X1 es igual a 0':
            tiempo = self.hora()
            self.ui.estado.setText("El punto 2 se encuentra en la misma posicion que el punto 1" + tiempo)
        elif rtastr == 'Operación Realizada.':
            tiempo = self.hora()

            self.ui.entrada2.clear()
            self.ui.estado.setText("Punto 2 enviado correctamente " + tiempo)
            self.ui.medido.setText("(" + str(pto2) + ")")

###############################################################################
    def clickEnviarPyM(self):
        inM = self.ui.entradaPyMm.displayText()
        inP = self.ui.entradaPyM1.displayText()
        try:
            m = float(inM)
        except ValueError:
            self.ui.estado.setText("Pendiente M no es un real")
            return
        try:
            n = float(inP)
        except ValueError:
            self.ui.estado.setText("Punto 1 no es un real")
            return

        rta = self.comm.setRef2(str(n))
        rtastr = ','.join(rta)
        print(rtastr)
        #  self.ui.medidoM.setText(rta)
        if rtastr == 'Operación Realizada.':
            rta = self.comm.setM(str(m / 4))
            #  self.ui.medidoM.setText(rta)
            rtastr = ','.join(rta)
            print(rtastr)
            #print(data)
            if rtastr == 'Operación Realizada.':
                tiempo = self.hora()
                self.ui.entradaPyMm.clear()
                self.ui.entradaPyM1.clear()
                self.ui.estado.setText("Calibracion enviada correctamente " + tiempo)
            #    self.ui.medido.setText("("+ str(float(self.ui.medido1.text()[1:-1]) + 10000) + ")")


###############################################################################
    def clickEnviarAparejo(self):
        inAparejo = self.ui.entradaAparejo.displayText()
        try:
            aparejo = float(inAparejo)
        except ValueError:
            self.ui.estado.setText("Lineas del aparejo no es un real")
            return
        ppr = self.ui.medidoPpr.text()
        diametro = self.ui.medidoDiametro.text()
        cable = self.ui.medidoCable.text()
        hpc = self.ui.medidoHpc.text()
        tiempo = self.hora()
        rta = self.comm.setGeometry(ppr[1:-1], diametro[2:-1], cable[2:-1], hpc[2:-1], str(aparejo))
        rtastr = ','.join(rta)
        print(rtastr)
        if rtastr == 'Operación Realizada.':
            tiempo = self.hora()
         #   self.ui.entradaAparejo.clear()
            self.ui.estado.setText("Lineas de aparejo enviadas correctamente " + tiempo)

###############################################################################
    def clickEnviarAjuste(self):
        inAltura = self.ui.entradaAlturaRef.displayText()
        try:
            altura = float(inAltura)
        except ValueError:
            self.ui.estado.setText("Altura de referencia no es un real")
            return
        inCapas = self.ui.entradaCapas.displayText()
        try:
            capas = int(inCapas)
        except ValueError:
            self.ui.estado.setText("Capas completas no es un entero")
            return
        inHiladas = self.ui.entradaHiladas.displayText()
        try:
            hiladas = int(inHiladas)
        except ValueError:
            self.ui.estado.setText(
                "Cantidad de Hiladas Última capa no es un entero")
            return
        rta = self.comm.adjust(str(capas), str(hiladas), str(altura))
        rtastr = ','.join(rta)
        print(rtastr)
        if rtastr == 'Operación Realizada.':
            tiempo = self.hora()
        #   print(tiempo)
        #    self.ui.entradaAlturaRef.clear()
        #    self.ui.entradaCapas.clear()
        #    self.ui.entradaHiladas.clear()
            self.ui.estado.setText("Ajuste enviado correctamente " + tiempo)
            self.ui.medidoAlturaRef.setText("(" + str(altura)[:-2] + ")")
            self.ui.medidoHiladas.setText("(" + str(hiladas) + ")")
            self.ui.medidoCapas.setText("(" + str(capas) + ")")


 ###############################################################################
    def clickEnviarGeometria(self):
        inPpr = self.ui.entradaPpr.displayText()
        try:
            ppr = int(inPpr)
        except ValueError:
            self.ui.estado.setText("Ppr no es un entero")
            return
        inDiametro = self.ui.entradaDiametro.displayText()
        try:
            diametro = float(inDiametro)
        except ValueError:
            self.ui.estado.setText("Diametro tambor no es un real")
            return
        inCable = self.ui.entradaCable.displayText()
        try:
            cable = float(inCable)
        except ValueError:
            self.ui.estado.setText("Diametro cable no es un real")
            return
        inAparejo = self.ui.entradaAparejo.displayText()
        try:
            aparejo = float(inAparejo)
        except ValueError:
            self.ui.estado.setText("Lineas del aparejo no es un real")
            return
        inHpc = self.ui.entradaHpc.displayText()
        try:
            hpc = int(inHpc)
        except ValueError:
            self.ui.estado.setText("Hpc no es un entero")
            return
        rta = self.comm.setGeometry(str(ppr), str(diametro), str(cable), str(hpc), str(aparejo))
        rtastr = ','.join(rta)
        print(rtastr)
        if rtastr == 'Operación Realizada.':
            tiempo = self.hora()

         #   self.ui.entradaPpr.clear()
         #   self.ui.entradaDiametro.clear()
         #   self.ui.entradaCable.clear()
         #   self.ui.entradaAparejo.clear()
         #   self.ui.entradaHpc.clear()
            self.ui.estado.setText("Geometria enviada correctamente " + tiempo)

#########################################################################################
    def __init__(self,parent=None):
        super(ControlMainWindows, self).__init__(parent)
        # Crea los elementos graficos
        self.ui = Ui_ventana()
        self.ui.setupUi(self)




# Agrega comportamiento a los botones
        QtCore.QObject.connect(self.ui.botonExit, QtCore.SIGNAL('clicked()'), self.clickExit)
        QtCore.QObject.connect(self.ui.botonEnviarGeometria, QtCore.SIGNAL('clicked()'), self.clickEnviarGeometria)
        QtCore.QObject.connect(self.ui.botonEnviarAjuste, QtCore.SIGNAL('clicked()'), self.clickEnviarAjuste)
        QtCore.QObject.connect(self.ui.botonEnviarAparejo, QtCore.SIGNAL('clicked()'), self.clickEnviarAparejo)
        QtCore.QObject.connect(self.ui.botonEnviarPyM, QtCore.SIGNAL('clicked()'), self.clickEnviarPyM)
        QtCore.QObject.connect(self.ui.botonEnviar1, QtCore.SIGNAL('clicked()'), self.clickEnviarPunto1)
        QtCore.QObject.connect(self.ui.botonEnviar2, QtCore.SIGNAL('clicked()'), self.clickEnviarPunto2)



        config = ConfigParser()
        config.read("config.conf")
        self.config['IP'] = config.get('Configuracion', 'IP')
        self.config['Sentido'] = config.get('Configuracion', 'Sentido')

        self.config['Tiempo'] = config.get('Configuracion', 'Tiempo')
        self.config['Modo'] = config.get('Configuracion', 'Modo')
        if self.config['Modo'] == "Lineal":
            self.ui.tabWidget.setTabEnabled(1, 0)
        elif self.config['Modo'] == "RD":
            self.ui.tabWidget.setTabEnabled(0, 0)
        ip = self.config['IP']




        self.comm = Comunicacion(ip)

        timer = QtCore.QTimer(self)
        self.connect(timer, QtCore.SIGNAL("timeout()"), self.Actualizar)
        # timer.start(int(sys.argv[4]))

        timer.start(int(self.config['Tiempo']))

        self.comm.set_conectado(0)
        self.ui.medidoRed.setStyleSheet("QLabel { color : red; }")
        self.ui.medidoRed.setText("NO CONECTADO")


        delay = ping(self.config['IP'], timeout=10)
        print("ping es: " , delay)
        if delay is not None :
            self.comm.set_conectado(1)
            self.ui.medidoRed.setStyleSheet("QLabel { color : green; }")
            self.ui.medidoRed.setText("CONECTADO")
            if (self.config['Sentido'] == "ForWard"):
                sentido = self.comm.setCounterForWard()

            elif (self.config['Sentido'] == "BackWard"):
                sentido = self.comm.setCounterBackWard()


        else:
            self.comm.set_conectado(0)
            self.ui.medidoRed.setStyleSheet("QLabel { color : red; }")
            self.ui.medidoRed.setText("NO CONECTADO")



if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    miVentanaPrincipal = ControlMainWindows()
    miVentanaPrincipal.show()
    sys.exit(app.exec_())




