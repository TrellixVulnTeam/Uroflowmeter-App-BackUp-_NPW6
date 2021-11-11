import pyrebase
import numpy as np
from kivy.uix.screenmanager import Screen
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec

config = {
  "apiKey": "AIzaSyBE439nHksT0x_MZ7gaD7rx3GwJh8VIBTM",
  "authDomain": "bg4102app.firebaseapp.com",
  "databaseURL": "https://bg4102app-default-rtdb.asia-southeast1.firebasedatabase.app/",
  "storageBucket": "bg4102app.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

class PatientReportGenerator():

    Patient_Variables = "./Context/Variables_Patient.txt"
    with open(Patient_Variables, "r") as f:
        PatientID = f.read()
        
    ## REPORT HEADER
    
    def GetPatientInfo(self):
        PatientName = self.GetFullName()
        
        PatientDay1 = db.child("patientUsers").child(self.PatientID).child("start").get().val()
        PatientDay2 = self.GetDay2Date(PatientDay1)
        PatientDay3 = db.child("patientUsers").child(self.PatientID).child("end").get().val()
        
        WakeUpTime = db.child("patientUsers").child(self.PatientID).child("wakeup").get().val()
        BedTime = db.child("patientUsers").child(self.PatientID).child("sleep").get().val()
        
        return PatientName, PatientDay1, PatientDay2, PatientDay3, WakeUpTime, BedTime
    
    def GetFullName(self):
        PatientName = ""
        FirstName = db.child("patientUsers").child(self.PatientID).child("firstname").get().val()
        LastName = db.child("patientUsers").child(self.PatientID).child("lastname").get().val()
        PatientName = PatientName + FirstName + LastName
        return PatientName
    
    def GetDay2Date(self, PatientStart):
        date_1 = datetime.datetime.strptime(PatientStart, "%d-%m-%Y")
        next_day = date_1 + datetime.timedelta(days=1)
        PatientDay2 = str(next_day.day) + '-' + str(next_day.month) + '-' + str(next_day.year)
        return PatientDay2
    
    ##FETCH ALL VOID DATA
    
    def GetVoidData(self, dayID):
        
        # Void Type
        EpisodeDayID = dayID + "episode"
        PatientUroflowData_VoidType = db.child("patientData").child(self.PatientID).child(EpisodeDayID).get()
        PatientUroflowData_VoidType = PatientUroflowData_VoidType.val()
        if PatientUroflowData_VoidType != None:
            VoidType = PatientUroflowData_VoidType
            print(VoidType)
        else:
            VoidType = []
        
        #Void Volumes
        Volume = db.child("patientData").child(self.PatientID).child(dayID).child("volume").get()
        PatientUroflowData_Volume = Volume.val()
        if PatientUroflowData_Volume != None:
            VoidVolume = PatientUroflowData_Volume.split(',')
        else:
            VoidVolume = []

        #Void Times
        VoidTimeList = []
        PatientUroflowData_Time = db.child("patientData").child(self.PatientID).child(dayID).child("time").get()
        PatientUroflowData_Time = PatientUroflowData_Time.val()
        if PatientUroflowData_Time != None:
            VoidTimeArray = PatientUroflowData_Time.split(',')
            for i in range(0, len(VoidTimeArray)):
                Time = VoidTimeArray[i]
                VoidTime = Time[0] + Time[1] + ':' + Time[2] + Time[3]
                VoidTimeList.append(VoidTime)
        else:
            VoidTimeList = []
        
        #Osmolality
        Osmolality = db.child("patientData").child(self.PatientID).child(dayID).child("osmolality").get()
        PatientUroflowData_Osmolality = Osmolality.val()
        if PatientUroflowData_Osmolality != None:
            VoidOsmolality = PatientUroflowData_Osmolality.split(',')
        else:
            VoidOsmolality = []
        
        #OMax
        QMax = db.child("patientData").child(self.PatientID).child(dayID).child("qmax").get()
        PatientUroflowData_QMax = QMax.val()
        if PatientUroflowData_QMax != None:
            VoidQMax = PatientUroflowData_QMax.split(',')
        else:
            VoidQMax = []
        
        #FluidIntake
        FluidIntakeDayID = dayID + "FluidIntake"
        FluidIntake = db.child("patientData").child(self.PatientID).child(FluidIntakeDayID).child("total fluid intake").get().val()
        
        #Void Symptoms
        SymptomsExperienced = []
        
        SymptomsID = "Symptoms" + dayID
        for i in range(0, len(VoidType)):
            VoidSymptoms = dayID + "episode"+ str(i)
            FluidIntake = db.child("patientData").child(self.PatientID).child(SymptomsID).child(VoidSymptoms).get().val()
            SymptomsExperienced.append(FluidIntake)
            
        return VoidType, VoidVolume, VoidTimeList, VoidOsmolality, VoidQMax, FluidIntake, SymptomsExperienced
    
    def VoidTypeInfo(self, VoidType, VoidVolume):
        
        #Count
        NocturiaCount = 0
        NormalCount = 0
        MorningCount = 0
        
        #Volumes
        NocturiaVoidVol = []
        NormalVoidVol = []
        MorningVoidVol = []
        
        for i in range(0, len(VoidType)):
            if VoidType[i] == "First Morning Episode":
                MorningVoidVol.append(VoidVolume[i])
                MorningCount += 1
            elif VoidType[i] == "Normal Episode":
                NormalVoidVol.append(VoidVolume[i])
                NormalCount += 1
            elif VoidType[i] == "Nocturia Episode":
                NocturiaVoidVol.append(VoidVolume[i])
                NocturiaCount += 1
        
        return NocturiaCount, NormalCount, MorningCount, NocturiaVoidVol, NormalVoidVol, MorningVoidVol
    
    def DaySummaryData(self, VoidType1, VoidVolume1, FluidIntake1, NocturiaCount1, NocturiaVoidVol1, MorningVoidVol1, VoidType2, VoidVolume2, FluidIntake2, NocturiaCount2, NocturiaVoidVol2, MorningVoidVol2, VoidType3, VoidVolume3, FluidIntake3, NocturiaCount3, NocturiaVoidVol3, MorningVoidVol3):
        TotalInput1 = FluidIntake1
        TotalVoidNumber1 = len(VoidVolume1)
        VoidVolume1 = np.array(VoidVolume1).astype(float)
        TotalOutput1 = np.sum(VoidVolume1)
        NocturiaVoidVol1 = np.array(NocturiaVoidVol1).astype(float)
        MorningVoidVol1 = np.array(MorningVoidVol1).astype(float)
        NocturiaVoidVol1 = np.sum(NocturiaVoidVol1) + np.sum(MorningVoidVol1)

        if TotalVoidNumber1 != 0:
            NPI1 = (NocturiaCount1/TotalVoidNumber1)*100
        else:
            NPI1 = "Not logged yet."

        if int(NPI1) >= 30:
            NocturiaPresent1 = "Yes"
        else:
            NocturiaPresent1 = "No"
            
        TotalInput2 = FluidIntake2
        TotalVoidNumber2 = len(VoidVolume2)
        VoidVolume2 = np.array(VoidVolume2).astype(float)
        TotalOutput2 = np.sum(VoidVolume2)
        NocturiaVoidVol2 = np.array(NocturiaVoidVol2).astype(float)
        MorningVoidVol2 = np.array(MorningVoidVol2).astype(float)
        NocturiaVoidVol2 = np.sum(NocturiaVoidVol2) + np.sum(MorningVoidVol2)

        if TotalVoidNumber2 != 0:
            NPI2 = (NocturiaCount2/TotalVoidNumber2)*100
        else:
            NPI2 = "Not logged yet."

        if int(NPI2) >= 30:
            NocturiaPresent2 = "Yes"
        else:
            NocturiaPresent2 = "No"
            
        TotalInput3 = FluidIntake3
        TotalVoidNumber3 = len(VoidVolume3)
        VoidVolume3 = np.array(VoidVolume3).astype(float)
        TotalOutput3 = np.sum(VoidVolume1)
        NocturiaVoidVol3 = np.array(NocturiaVoidVol3).astype(float)
        MorningVoidVol3 = np.array(MorningVoidVol3).astype(float)
        NocturiaVoidVol3 = np.sum(NocturiaVoidVol3) + np.sum(MorningVoidVol3)

        if TotalVoidNumber3 != 0:
            NPI3 = (NocturiaCount3/TotalVoidNumber3)*100
        else:
            NPI3 = "Not logged yet."

        if int(NPI3) >= 30:
            NocturiaPresent3 = "Yes"
        else:
            NocturiaPresent3 = "No"

        TotalInput = []
        TotalInput.append(TotalInput1)
        TotalInput.append(TotalInput2)
        TotalInput.append(TotalInput3)
        
        TotalOutput = []
        TotalOutput.append(TotalOutput1)
        TotalOutput.append(TotalOutput2)
        TotalOutput.append(TotalOutput3)
        
        NocNum = []
        NocNum.append(NocturiaCount1)
        NocNum.append(NocturiaCount2)
        NocNum.append(NocturiaCount3)
        
        NPI = []
        NPI.append(str(NPI1)[:4])
        NPI.append(str(NPI2)[:4])
        NPI.append(str(NPI3)[:4])
        
        Noc = []
        Noc.append(NocturiaPresent1)
        Noc.append(NocturiaPresent2)
        Noc.append(NocturiaPresent3)

        DayData = []
        DayData.append(TotalInput)
        DayData.append(TotalOutput)
        DayData.append(NocNum)
        DayData.append(NPI)
        DayData.append(Noc)
        
        return DayData
    
    def SummaryData(self, VoidVolume1, VoidQMax1, VoidVolume2, VoidQMax2, VoidVolume3, VoidQMax3, NormalCount1, NormalCount2, NormalCount3, NormalVoidVol1, NormalVoidVol2, NormalVoidVol3):
        #Q Max Range (above 150ml)
        ConsiderVolume1 = []
        QMaxConsidered1 = []
        for i in range(0, len(VoidVolume1)):
            if int(VoidVolume1[i]) >= 150:
                ConsiderVolume1.append(i)
            else:
                pass
        for k in ConsiderVolume1:
            QMaxConsidered1.append(VoidQMax1[k])
        
        QMaxConsidered1 = np.array(QMaxConsidered1).astype(float)
        QMaxRange1 = max(QMaxConsidered1) - min(QMaxConsidered1)
        
        ConsiderVolume2 = []
        QMaxConsidered2 = []
        for ii in range(0, len(VoidVolume2)):
            if int(VoidVolume2[ii]) >= 150:
                ConsiderVolume2.append(ii)
            else:
                pass
        for kk in ConsiderVolume2:
            QMaxConsidered2.append(VoidQMax2[kk])
        
        QMaxConsidered2 = np.array(QMaxConsidered2).astype(float)
        QMaxRange2 = max(QMaxConsidered2) - min(QMaxConsidered2)
        
        ConsiderVolume3 = []
        QMaxConsidered3 = []
        for iii in range(0, len(VoidVolume3)):
            if int(VoidVolume3[iii]) >= 150:
                ConsiderVolume3.append(iii)
            else:
                pass
        for kkk in ConsiderVolume3:
            QMaxConsidered3.append(VoidQMax3[kkk])
        
        QMaxConsidered3 = np.array(QMaxConsidered3).astype(float)
        QMaxRange3 = max(QMaxConsidered3) - min(QMaxConsidered3)
        
        QMaxRange = (QMaxRange1 + QMaxRange2 + QMaxRange3)/3
        
        #Daytime Frequency Range
        DaytimeVoids = [NormalCount1, NormalCount2, NormalCount3]
        DaytimeFrequency = max(DaytimeVoids) - min(DaytimeVoids)

        # Daytime Voided Volume Range
        DaytimeVoidVolume = []
        NormalVoidVol1 = np.array(NormalVoidVol1).astype(float)
        NormalVoidVol1 = sum(NormalVoidVol1)
        DaytimeVoidVolume.append(NormalVoidVol1)
        NormalVoidVol2 = np.array(NormalVoidVol2).astype(float)
        NormalVoidVol2 = sum(NormalVoidVol2)
        DaytimeVoidVolume.append(NormalVoidVol2)
        NormalVoidVol3 = np.array(NormalVoidVol3).astype(float)
        NormalVoidVol3 = sum(NormalVoidVol3)
        DaytimeVoidVolume.append(NormalVoidVol3)
        DaytimeVoided = max(DaytimeVoidVolume) - min(DaytimeVoidVolume)
        
        QMaxRangeData = []
        QMaxRangeData.append(QMaxRange)
        DaytimeFrequencyRange = []
        DaytimeFrequencyRange.append(DaytimeFrequency)
        DaytimeVoidVolumeRange = []
        DaytimeVoidVolumeRange.append(DaytimeVoided)
        
        SummaryStructured = []
        SummaryStructured.append(QMaxRangeData)
        SummaryStructured.append(DaytimeFrequencyRange)
        SummaryStructured.append(DaytimeVoidVolumeRange)
        
        return SummaryStructured
        
    #Usual Daytime Frequency, Maximal Voided Volume (MVV) (ml), Usual Daytime Voided Volume (ml)
    def UsualDaytimeFrequency(self):...
    def MaximaVoidedVolume(self):...
    def DaytimeVoidedVolume(self):...
    
    def ControlStation(self):
    
        #Report Header
        PatientName, PatientDay1, PatientDay2, PatientDay3, WakeUpTime, BedTime = self.GetPatientInfo()
        
        #All Void Data by Day
        VoidType1, VoidVolume1, VoidTimeList1, VoidOsmolality1, VoidQMax1, FluidIntake1, SymptomsExperienced1 = self.GetVoidData("day 1")
        VoidType2, VoidVolume2, VoidTimeList2, VoidOsmolality2, VoidQMax2, FluidIntake2, SymptomsExperienced2 = self.GetVoidData("day 2")
        VoidType3, VoidVolume3, VoidTimeList3, VoidOsmolality3, VoidQMax3, FluidIntake3, SymptomsExperienced3 = self.GetVoidData("day 3")
        
        #Void Type Specific Information
        NocturiaCount1, NormalCount1, MorningCount1, NocturiaVoidVol1, NormalVoidVol1, MorningVoidVol1 = self.VoidTypeInfo(VoidType1, VoidVolume1)
        NocturiaCount2, NormalCount2, MorningCount2, NocturiaVoidVol2, NormalVoidVol2, MorningVoidVol2 = self.VoidTypeInfo(VoidType2, VoidVolume2)
        NocturiaCount3, NormalCount3, MorningCount3, NocturiaVoidVol3, NormalVoidVol3, MorningVoidVol3 =  self.VoidTypeInfo(VoidType3, VoidVolume3)
        
        #FVC Day Data (Structured)
        DayDataStructured = self.DaySummaryData(VoidType1, VoidVolume1, FluidIntake1, NocturiaCount1, NocturiaVoidVol1, MorningVoidVol1, VoidType2, VoidVolume2, FluidIntake2, NocturiaCount2, NocturiaVoidVol2, MorningVoidVol2, VoidType3, VoidVolume3, FluidIntake3, NocturiaCount3, NocturiaVoidVol3, MorningVoidVol3)
        
        #FVC Summary (Structured)
        SummaryStructured = self.SummaryData(VoidVolume1, VoidQMax1, VoidVolume2, VoidQMax2, VoidVolume3, VoidQMax3, NormalCount1, NormalCount2, NormalCount3, NormalVoidVol1, NormalVoidVol2, NormalVoidVol3)
        
        #Data for Graphs (Structured)
        
        #Data for Osmolality Graph (Structured)
        #VoidOsmolality1, VoidTimeList1
        #VoidOsmolality2, VoidTimeList2
        #VoidOsmolality3, VoidTimeList3
        
    def BuildReport(self):...
        
        
        

        
            