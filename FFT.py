from Extraccion import Directorio,File
from scipy.fft import fft, fftfreq, fftshift
from pandas import read_table, DataFrame
from matplotlib.pyplot import figure, plot, savefig, close
from shutil import rmtree
import numpy as np
import os


class FFT:
    def __init__(self, name = "Huesos Menopausia Osciloscopio"):
        self.Dir = File(name = name)
        self.Dir.GetAll()
        self.ApplyFFT()

    def ApplyFFT(self):
        SavePath = os.getcwd() + "\\Graficas" + "\\GroupFFT"
        try:
            os.mkdir(SavePath)  # Crea el archivo, si no se puede arrojara un OSError, debido a que ya existe
        except OSError:
            print("Folder already exists, deleting folder")
            rmtree(SavePath)
            # Borra todo en la carpeta
            print("Retrying")
            os.mkdir(SavePath)  # Vuelve a crear la carpeta

        for FirstLocation in range(0,len(self.Dir.Files)):
            for SecondLocation in range(0, len(self.Dir.Files[FirstLocation])):
                Wished = self.Dir.Files[FirstLocation][SecondLocation]

                namefig = Wished.replace(".txt", " FFT")
                path = self.Dir.Dirs[FirstLocation]
                print(path)
                path = self.Dir.DirectorioPrincipal+"\\"+path+"\\"+Wished
                print(path)
                self.Df = read_table(path, usecols=[3, 4], names=["Time", "Intensity"]).applymap(
                    "{:.11f}".format).astype(float)

                Time = list(self.Df["Time"])
                y = list(self.Df["Intensity"])

                #print(Time); print(y)

                N = len(Time)
                yf = fft(y)
                xf = fftshift(fftfreq(N, 1/N))
                yf = 1/(N* np.abs(yf))

                l = (len(yf)//2)-1
                yfTemp = list(yf)
                self.ToDf = yfTemp[l:]

                figure(1)
                plot(xf, yf)

                DfExtracted = DataFrame(self.ToDf)
                DfExtracted.to_csv(SavePath+"\\"+namefig+".csv")
                savefig(SavePath + "\\" + namefig)

                close()



            #df = DataFrame(self.ToDF, columns=["SignalFFT"])
            #print(df)
            #df.to_csv(self.Dir.Files)


a = FFT()