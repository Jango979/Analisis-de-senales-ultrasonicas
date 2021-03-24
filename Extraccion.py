from pandas import read_table
import os
from scipy.signal import detrend, butter, sosfiltfilt, medfilt
from numpy import pi, amax, float
from matplotlib.pyplot import plot, figure, show, savefig,close
from shutil import rmtree


class Directorio():  # Defino una clase directorio
    """Identifico como variable de entrada para el constructor el nombre de la carpeta en la que se encuentran
    nuestros datos. Por defecto su nombre es Huesos Menopausia Osciloscopio"""

    def __init__(self, name="Huesos Menopausia Osciloscopio"):
        self.DirectorioPrincipal = name  # Vuelvo un atributo el nombre de la carpeta
        self.Dirs = os.listdir("./" + name)  # Importo todas las carpetas dentro de la carpeta principal

    def getNames(self, Dir=0):
        """El fin de esta función es el poder obtener los nombres de todos los archivos dentro
        de la carpeta señalada"""
        Docs = self.Dirs[Dir]  # En base a la variable de entrada se selecciona una subcarpeta
        print("Abriendo {}\n".format("./" + self.DirectorioPrincipal + "/" + Docs))
        self.DocumentsNames = os.listdir("./" + self.DirectorioPrincipal + "/" + Docs)
        # Se obtiene una lista de todos los archivos en la subcarpeta
        print(self.DocumentsNames)

    def Separate(self, type="Muestra"):
        """Aisla especificamente una categoria de datos"""
        self.Wished = []  # En este atributo se guardara el nombre de todos los datos
        for name in self.DocumentsNames:
            if type in name:
                self.Wished.append(name)
        if len(self.Wished) == 0:
            raise NameError("Context not found")  # Identifica si no existe ninguno con ese nombre
        else:
            print(self.Wished)


class File(Directorio):
    """Segunda clase en la cual en base a funciones de la clase anterior va
    obteniendo los datos ya sea de forma individual o grupal"""

    def __init__(self):
        self.Directorio = Directorio.__init__(self)  # Obtienes los atributos de la clase padre (Directorio)

    def GetAll(self):
        """Obtiene los nombre de todos los archivos"""
        n = len(self.Dirs)
        self.Files = []
        for i in range(0, n):
            self.getNames(i)  # Se usa el metodo de la clase padre
            self.Files.append(self.DocumentsNames)

        print(self.DocumentsNames)

    def GetOne(self, type="Muestra", Dir=0):
        """Se usan los metodos de la clase anterior para separar los datos ya sea para analizar todos los datos
        o para analizar solo un dato"""
        n = 0
        Directorio.getNames(self, Dir)  #
        if type == "All":
            self.Wished = self.DocumentsNames
        else:
            Directorio.Separate(self, type=type)

        for i in self.Wished:
            print("{}\t{}".format(n, i))
            n = n + 1

        Option = int(input("Choose a number\n"))  # Elige un archivo en especifico
        self.Option = "./" + self.DirectorioPrincipal + "/" + self.Dirs[Dir] + "/" + self.Wished[Option]
        # Guarda la direccion donde se encuentra todos los archivos para poder extraer el contenido
        self.Wished = self.Wished[Option]
        # Guarda el nombre del archivo elegido
        print("Document {} saved in attribute Option".format(self.Option))


class AnalysisByFFT():
    def __init__(self, Object):
        if hasattr(Object, "Files"):  # Si tiene el atributo Files hablamos de varios documentos
            print("Importing list of Files")
            self.Type = "Group"  # Especificamos este atributo para especificarlo de forma más accesible
            self.Directories = Object.Dirs  # Importa los directorios de otra clase
            self.Files = Object.Files  # Importa el nombre de los archivos de otra clase

        elif hasattr(Object, "Option"):  # Single
            print("Importing " + Object.Option)
            self.Type = "Single"  # Identifica que solo se analizara una unica señal
            self.Files = Object.Option  # Importa el nombre del archivo
            self.Df = read_table(Object.Option, usecols=[3, 4], names=["Time", "Intensity"]).applymap(
                "{:.11f}".format).astype(float)  # Lee el archivo y crea un Data Frame, usa las columnas 3 y 4
            # como un caso especifico para este trabajo ya que en las otras columnas tiene datos muy indicados
            # para guardar en un data frame
            self.Wished = Object.Wished  # Importa el nombre del archivo deseado y lo guarda en esta clase
            print("Database " + Object.Option)
            print(self.Df)

    def LowPass(self, x="Time", y="Intensity", freq=1):
        Time = self.Df[x]  # Separa el vector de tiempo
        Y = self.Df[y]  # Separa el vector de la señal
        self.NoOffset = detrend(Y, 0)  # Aplica un detrend a la señal para desplazarla a 0

        TimeMax = amax(Time)  # Obtiene el tiempo maximo
        Nt = len(Time)  # Obtiene la longitud de la señal
        Fs = Nt / TimeMax  # Saca la frecuencia de muestreo
        Fn = Fs / 2  # Obtiene la frecuencia de Nyquist
        Wn = 2 * freq * pi  # Obtiene la frecuencia angular

        sos = butter(9, Wn, "lowpass", fs=Fs, output="sos")  # Aplica un filtro butterworth de tipo pasa baja
        self.YFiltered = sosfiltfilt(sos, self.NoOffset)  # Aplica el filtro sobre nuestra señal con el offset
        self.MedFiltered = medfilt(self.NoOffset)  # Aplica el filtro de mediana
        # print(self.YFiltered)

    def ApplyLowPass(self, x="Time", y="Intensity", freq=1 ):
        """Este metodo hace uso del metodo del metodo anterior, aplicandolo pero
        identificandolo si es para una unica señal o para varias señales"""
        if self.Type == "Single":
            self.LowPass(x=x, y=y, freq=freq)  # Si es solo una señal se aplica solo el filtro pasa baja
        elif self.Type == "Group":
            print("Because it is a list of data, it will be processed to graph and save all the figures")
            choose = input("Type of Analysis:\nFiltered\nAll\nOriginal\n")
            # Se elige el tipo de grafica que quieres que se guarde
            path = os.getcwd() + "\\Graficas" + "\\Group"  # Se registra una dirección para posteriormente guardar
            # las graficas esto hace uso de un metodo detallado despues
            try:
                os.mkdir(path)  # Crea el archivo, si no se puede arrojara un OSError, debido a que ya existe
            except OSError:
                print("Folder already exists, deleting folder")
                rmtree(path)
                # Borra todo en la carpeta
                print("Retrying")
                os.mkdir(path)  # Vuelve a crear la carpeta

            for FirstLocation in range(0, len(self.Directories)):
                print("\n\n\nLocation {}".format(FirstLocation))
                # path=self.Directories[FirstLocation]
                # print(path)
                for SecondLocation in range(0, len(self.Files[FirstLocation])):
                    #Crea un for anidado para acceder a la localizacion de cada uno de los archivos
                    self.Wished = self.Files[FirstLocation][SecondLocation]
                    #Se aisla el nombre de cada archivo
                    path = self.Directories[FirstLocation]
                    path = "Huesos Menopausia Osciloscopio\\" + path + "\\" + self.Wished
                    print(path)
                    self.Df = self.Df = read_table(path, usecols=[3, 4], names=["Time", "Intensity"]).applymap("{:.11f}".format).astype(float)
                    #Se convierte a Data Frame
                    self.LowPass(x=x, y=y, freq=freq)
                    #Se aplica el filtro pasa - baja
                    self.Graph(x=x, Group=choose, y="Intensity")
                    #Se aplica el metodo graph creado a continuacion


    def Graph(self, x="Time", Group="Filtered", y="Intensity"):
        #Grafica para aplicar mas que nada cuando solo se quiera analizar una señal
        if self.Type == "Single":
            path = os.getcwd() + "\\Graficas" + "\\Single"
            try:
                os.mkdir(path)
            except OSError:
                print("Folder already exists, deleting folder")
                rmtree(path)
                print("Retrying")
                os.mkdir(path)
        #El siguiente proceso es cuando se trata de una lista de señales
        elif self.Type == "Group":
            path = os.getcwd() + "\\Graficas" + "\\Group"

        namefig = self.Wished.replace(".txt", Group)

        #Las graficas son separadas por el tipo de señal deseada, filtered, original o todas
        figure(1)
        if Group == "Filtered":
            plot(self.Df[x], self.YFiltered)
            #plot(self.Df[x], self.NoOffset)
            savefig(path + "\\" + namefig + "FFT Filtered")
            # show()

        elif Group == "All":
            plot(self.Df[x], self.Df[y])
            plot(self.Df[x], self.NoOffset)
            savefig(path + "\\" + namefig + " NoOffset")
            # show()

            figure(1)
            plot(self.Df[x], self.MedFiltered)
            plot(self.Df[x], self.NoOffset)
            savefig(path + "\\" + namefig + "Median Filtered.png")
            # show()

            figure(1)
            plot(self.Df[x], self.YFiltered)
            plot(self.Df[x], self.NoOffset)
            savefig(path + "\\" + namefig + " FFT Filtered")
            # show()

        elif Group == "Original":
            plot(self.Df[x], self.Df[y])
            plot(self.Df[x], self.NoOffset)
            # show()
            savefig(path + "\\" + namefig + " Original")
            # input("Continue")
        close(1)

        # def IdentifyPeaks()


# a = Directorio()
# a.getNames(1)
# a.Separate()



"""Esto es para analizar varias señales"""
b = File()
# b.GetOne()
b.GetAll()

c = AnalysisByFFT(b)
c.ApplyLowPass(freq=900)
# c.Graph(Group="Original") #Solo cuando sean individuales


"""Esto es cuando solo se quiera analizar una señal"""
#b=File()
#b.GetOne("Muestra")
#c=AnalysisByFFT(b)
#c.ApplyLowPass(2000)
#c.Graph(Group="Original")

