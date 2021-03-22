from pandas import read_table
import os
from scipy.signal import detrend,butter,sosfiltfilt, medfilt
from numpy import pi, amax,float
from matplotlib.pyplot import plot, figure,show,savefig
from shutil import rmtree

class Directorio():
    def __init__(self, name="Huesos Menopausia Osciloscopio"):
        self.DirectorioPrincipal = name
        self.Dirs = os.listdir("./"+name) #Importe del directorio

    def getNames(self, Dir=0):
        Docs = self.Dirs[Dir]
        print("Abriendo {}\n".format("./"+self.DirectorioPrincipal+"/"+Docs))
        self.DocumentsNames = os.listdir("./"+self.DirectorioPrincipal+"/"+Docs)
        print(self.DocumentsNames)

    def Separate(self, type = "Muestra"):
        self.Wished = []
        for name in self.DocumentsNames:
            if type in name:
                self.Wished.append(name)
        if len(self.Wished) == 0:
            raise NameError("Context not found")
        else:
            print(self.Wished)

class File(Directorio):
    def __init__(self):
        self.Directorio = Directorio.__init__(self)

    def GetAll(self):
        n = len(self.Dirs)
        self.Files = []
        for i in range(0,n):
            self.getNames(i)
            self.Files.append(self.DocumentsNames)

        print(self.DocumentsNames)

    def GetOne(self, type = "Muestra", Dir = 0) :
        n = 0
        Directorio.getNames(self, Dir)
        if type == "All":
            self.Wished = self.DocumentsNames
        else:
            Directorio.Separate(self, type = type)

        for i in self.Wished:
            print("{}\t{}".format(n, i))
            n = n + 1
        Option = int(input("Choose a number\n"))
        self.Option = "./"+self.DirectorioPrincipal+"/"+self.Dirs[Dir]+"/"+self.Wished[Option]
        self.Wished = self.Wished[Option]
        print("Document {} saved in attribute Option".format(self.Option))




class AnalysisByFFT():
    def __init__(self, Object): #Group
        if hasattr(Object,"Files"):
            print("Importing list of Files")
            self.Type = "Group"
            self.Directories = Object.Dirs
            self.Files = Object.Files

        elif hasattr(Object,"Option"): #Single
            print("Importing "+Object.Option)
            self.Type="Single"
            self.Files = Object.Option
            self.Df = read_table(Object.Option, usecols=[3, 4], names=["Time", "Intensity"]).applymap(
                "{:.11f}".format).astype(float)
            self.Wished = Object.Wished
            print("Database " + Object.Option)
            print(self.Df)

    def LowPass(self,x="Time",y="Intensity",freq=1):
        Time = self.Df[x]
        Y = self.Df[y]
        self.NoOffset = detrend(Y, 0)

        TimeMax = amax(Time)
        Nt = len(Time)
        Fs = Nt / TimeMax
        Fn = Fs / 2
        Wn = 2 * freq * pi

        sos = butter(9,Wn,"lowpass",fs=Fs, output="sos")
        self.YFiltered = sosfiltfilt(sos, self.NoOffset)
        self.MedFiltered = medfilt(self.NoOffset)
        #print(self.YFiltered)


    def ApplyLowPass(self,x="Time",y="Intensity",freq = 1, ):
        if self.Type == "Single":
            self.LowPass(x = x, y = y, freq = freq)
        elif self.Type == "Group":
            print("Because it is a list of data, it will be processed to graph and save all the figures")
            choose = input("Type of Analysis:\nFiltered\nAll\nOriginal\n")

            path = os.getcwd() + "\\Graficas" + "\\Group"
            try:
                os.mkdir(path)
            except OSError:
                print("Folder already exists, deleting folder")
                rmtree(path)
                print("Retrying")
                os.mkdir(path)


            for FirstLocation in range(0,len(self.Directories)):
                print("\n\n\nLocation {}".format(FirstLocation))
                #path=self.Directories[FirstLocation]
                #print(path)
                for SecondLocation in range(0,len(self.Files[FirstLocation])):
                    self.Wished = self.Files[FirstLocation][SecondLocation]
                    path = self.Directories[FirstLocation]
                    path = "Huesos Menopausia Osciloscopio\\"+path+"\\" + self.Wished
                    print(path)
                    self.Df = self.Df = read_table(path, usecols=[3, 4], names=["Time", "Intensity"]).applymap("{:.11f}".format).astype(float)
                    self.LowPass(x = x, y = y, freq = freq)
                    self.Graph( x = x, Group = choose, y = "Intensity")


    def Graph(self,x = "Time",Group = "Filtered",y = "Intensity"):

        if self.Type == "Single":
            path = os.getcwd() + "\\Graficas" + "\\Single"
            try:
                os.mkdir(path)
            except OSError:
                print("Folder already exists, deleting folder")
                rmtree(path)
                print("Retrying")
                os.mkdir(path)
        elif self.Type == "Group":
            path = os.getcwd() + "\\Graficas" + "\\Group"

        namefig = self.Wished.replace(".txt", Group)


        figure()
        if Group == "Filtered":
            plot(self.Df[x],self.YFiltered)
            plot(self.Df[x],self.NoOffset)
            savefig(path + "\\" + namefig+"FFT Filtered")
            #show()

        elif Group == "All":
            plot(self.Df[x],self.Df[y])
            plot(self.Df[x], self.NoOffset)
            savefig(path + "\\" + namefig + " NoOffset")
            #show()

            figure()
            plot(self.Df[x],self.MedFiltered)
            plot(self.Df[x], self.NoOffset)
            savefig(path + "\\" + namefig + "Median Filtered.png")
                #show()

            figure()
            plot(self.Df[x],self.YFiltered)
            plot(self.Df[x], self.NoOffset)
            savefig(path + "\\" + namefig + " FFT Filtered")
                #show()

        elif Group == "Original":
            plot(self.Df[x],self.Df[y])
            plot(self.Df[x], self.NoOffset)
            #show()
            savefig(path + "\\" + namefig + " Original")
            #input("Continue")


        #def IdentifyPeaks()
#a = Directorio()
#a.getNames(1)
#a.Separate()

b = File()
#b.GetOne()
b.GetAll()

c = AnalysisByFFT(b)
c.ApplyLowPass()
#c.Graph(Group="Original") #Solo cuando sean individuales

