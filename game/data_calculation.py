#!/usr/bin/env python
# coding: utf-8

# In[94]:


import numpy
from numpy import array, arange, abs as np_abs
import pandas as pd
from scipy.fft import irfft, rfft, rfftfreq
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import acf
from scipy.integrate import simps

import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# # Оглавление

# ЭКГ:
# * [Загрузка данных](#1)
# * [Фильтрация](#2)
# * [Нахождение R-зубцов](#3)
# * [Расчёт R-интервалов](#4)
# * [Сглаживание R-интервалов](#5)
# * [Гистограмма кардиоинтервалов](#6)
# * [Статистические метрики](#7)
# * [Метрики вариационной пульсометрии](#8)
# * [Автокоррелограмма](#9)
# * [Скатерограмма](#10)
# 
# ФПГ:
# * [Загрузка данных](#11)
# * [Фильтрация](#12)
# * [Нахождение R-зубцов](#13)
# * [Расчёт R-интервалов](#14)
# * [Сглаживание R-интервалов по 8-и записям](#20)
# * [Гистограмма кардиоинтервалов](#15)
# * [Статистические метрики](#16)
# * [Метрики вариационной пульсометрии](#17)
# * [Автокоррелограмма](#18)
# * [Скатерограмма](#19)
# 
# [Сравнение данных](#21)
# 

# # 

# # ЭКГ

# # <a class="anchor" id="1"></a>

# ## Загрузка данных 

# In[95]:


ecgFrame = pd.read_table("экг1.dat", sep='	', names=["time", "value"], header=None)
ecgFrame.reset_index(inplace = True)
ecgFrame.pop("time")

# ecgFrame = ecgFrame.head(120000)

rate = 300


# In[96]:


meanECG = ecgFrame["value"].mean() # Среднее значение ЭМГ

ecgFrame["meanedValue"] = ecgFrame["value"] - meanECG


# In[97]:


ecgFrame.plot(x = "index",
              y = ["value", "meanedValue"],
              figsize = (18,6))
plt.xticks(rotation=45)
plt.hlines(0, 0, len(ecgFrame))
plt.show()


# # <a class="anchor" id="2"></a>

# ## Фильтрация 

# In[98]:


ecg = ecgFrame["meanedValue"].to_numpy() # Список данных ЭКГ

yf = rfft(ecg) # мощность волн определённой частоты на графике
xf = rfftfreq(len(ecg), 1 / rate) # список всех частот на графике

plt.plot(xf, numpy.abs(yf))
plt.show()


# In[99]:


for i in range(len(xf)):
    if xf[i]<1 or xf[i]>30:
        yf[i]=0


# In[100]:


ecgFrame["filteredEСG"] = irfft(yf) # Восстановление графика ЭКГ по частотам с графика выше

ecgFrame.plot(x = "index",
               y = ["meanedValue", "filteredEСG"],
               figsize = (18,6))
plt.xticks(rotation=45)
plt.show()


# # <a class="anchor" id="3"></a>

# ## Нахождение R-зубцов 

# In[101]:


rPeaks, _ = find_peaks(ecgFrame["filteredEСG"], height = 1.5, distance = 150)
rPeaks = rPeaks.tolist()

plt.figure(figsize=(23, 9))
plt.hlines(0.5, 0, len(ecgFrame["filteredEСG"]))
plt.plot(ecgFrame["filteredEСG"])
plt.plot(rPeaks, ecgFrame["filteredEСG"][rPeaks], "x", label='R-зубцы')
plt.legend(loc='best')
plt.show()


# # <a class="anchor" id="4"></a>

# ## Расчёт R-интервалов

# In[102]:


rIntervalsECG = [] # Размер интервала между соседними R-зубцами в мс

for i in range(len(rPeaks) - 1):
    rIntervalsECG.append((rPeaks[i + 1] - rPeaks[i]) / rate * 1000)

rIntervalsECG.append(pd.Series(rIntervalsECG).mean())


# In[103]:


plt.figure(figsize=(18, 6))
plt.plot(rIntervalsECG, marker='o', label='Размер интервала', color='red')
    
for i in range(len(rIntervalsECG)):
    plt.annotate(str(round(rIntervalsECG[i])), (i, rIntervalsECG[i] - 50), fontsize=12, color='blue')

plt.legend(loc='lower right')
plt.show()


# # <a class="anchor" id="5"></a>

# ## Сглаживание R-интервалов по 8-и записям

# In[104]:


smoothedIntervals = []
    
for i in range(7, len(rIntervalsECG)):
    summ = 0
    
    for j in range(7):
        summ += rIntervalsECG[i - j]
        
    smoothedIntervals.append(summ / 7)
    
rIntervalsECG = smoothedIntervals


# In[105]:


plt.figure(figsize=(18, 6))
plt.plot(rIntervalsECG, marker='o', label='Размер интервала', color='red')

for i in range(len(rIntervalsECG)):
    plt.annotate(str(round(rIntervalsECG[i])), (i - 0.5, rIntervalsECG[i] - 25), fontsize=12, color='blue')

plt.xlabel('Номер интервала', fontsize=12)
plt.ylabel('Продолжительность интервала, мс', fontsize=12)
plt.legend(loc='lower right')
plt.show()


# # <a class="anchor" id="6"></a>

# ## Гистограмма кардиоинтервалов

# In[106]:


minimumECG = round(min(rIntervalsECG))
maximumECG = round(max(rIntervalsECG))
print(str(minimumECG) + " " + str(maximumECG))

valuesECG = []
countsECG = []

tempConvert = pd.Series(rIntervalsECG)

for i in range(minimumECG, maximumECG, 50):
    countsECG.append(tempConvert.where(tempConvert >= i).where(tempConvert < i + 50).count())
    valuesECG.append(i)

plt.hist(x = rIntervalsECG, bins = valuesECG)
plt.show()


# # <a class="anchor" id="7"></a>

# ## Статистические метрики

# In[107]:


seriesIntervalsECG = pd.Series(rIntervalsECG)

# Математическое ожидание (RRNN) (Среднее значение)
MECG = seriesIntervalsECG.mean() / 1000
print("Математическое ожидание        = " + str(MECG) + " с")

# Среднеквадратичное отклонение (SDNN) (Средний разброс элементов относительно мат. ожидания)
SECG = seriesIntervalsECG.std(ddof = 0) / 1000
print("Среднеквадратичное отклонение  = " + str(SECG) + " с")

# Коэффициент вариации (CV) (То же среднеквадратичное отклонение, но с нормировкой по пульсу)
CVECG = SECG / MECG * 100
print("Коэффициент вариации           = " + str(CVECG))


# # <a class="anchor" id="8"></a>

# ## Метрики вариационной пульсометрии

# In[108]:


# Мода (Наиболее часто встречающееся значение)
MoECG = (valuesECG[(len(valuesECG) // 2) - 1] + 25) / 1000
print("Мода                           = " + str(MoECG) + " с")

# Амплитуда моды (Процент значений входящих в моду)
AMoECG = countsECG[(len(valuesECG) // 2) - 1] / len(rIntervalsECG) * 100
print("Амплитуда моды                 = " + str(AMoECG) + " %")

# Вариационный размах (Максимальная амплитуда значений)
DXECG = (maximumECG - minimumECG) / 1000
print("Вариационный размах            = " + str(DXECG) + " с")

# Вегетативный показатель ритма (Чем меньше ВПР, тем больше преобладает парасимпатический отдел)
VPRECG = 1 / (MoECG * DXECG)
print("Вегетативный показатель ритма  = " + str(VPRECG))

# Индекс напряжения регуляторных систем (Чем ниже, там сильнее парасимпатика. Чем выше, тем сильнее симпатика)
INECG = AMoECG / (2 * DXECG * MoECG)
print("Индекс напряжения              = " + str(INECG))


# # <a class="anchor" id="9"></a>

# ## Автокоррелограмма

# In[109]:


plot_acf(seriesIntervalsECG, lags = 150)
autocorrelation = acf(seriesIntervalsECG, nlags = len(seriesIntervalsECG) - 1)


# In[110]:


yf = rfft(autocorrelation) # мощность волн определённой частоты на графике
xf = rfftfreq(len(autocorrelation), 1 / 0.76) # список всех частот на графике
plt.axvline(x = 0.04, color = 'crimson')
plt.axvline(x = 0.15, color = 'crimson')

plt.plot(xf, numpy.abs(yf), color = "blue")
plt.show()


# In[111]:


VLF = []
LF = []
HF = []

for i in range(len(xf)):
    if (xf[i] <= 0.04):
        VLF.append(numpy.abs(yf[i]))
    if (xf[i] >= 0.04 and xf[i] <= 0.15):
        LF.append(numpy.abs(yf[i]))
    if (xf[i] >= 0.15):
        HF.append(numpy.abs(yf[i]))
        
allFrequenciesECG = simps(numpy.abs(yf))
VLFECG = simps(VLF / allFrequenciesECG * 100)
LFECG = simps(LF / allFrequenciesECG * 100)
HFECG = simps(HF / allFrequenciesECG * 100)


# # <a class="anchor" id="10"></a>

# ## Скатерограмма

# In[112]:


currentPeaksECG = []
nextPeaksECG = []

for i in range(len(rIntervalsECG) - 1):
    currentPeaksECG.append(rIntervalsECG[i] / 1000)
    nextPeaksECG.append(rIntervalsECG[i + 1] / 1000)

plt.figure(figsize=(5,5))
plt.plot(currentPeaksECG, nextPeaksECG,'r+')

plt.show()


# # 

# # 

# # ФПГ

# # <a class="anchor" id="11"></a>

# # Загрузка данных

# In[113]:


fpgFrame = pd.read_table("фпг1.dat", sep='	', names=["time", "value"], header=None)
fpgFrame.reset_index(inplace = True)
fpgFrame.pop("time")

# fpgFrame = fpgFrame.head(3000)

rate = 300


# In[114]:


meanFPG = fpgFrame["value"].mean() # Среднее значение ЭМГ

fpgFrame["meanedValue"] = fpgFrame["value"] - meanFPG


# In[115]:


fpgFrame.plot(x = "index",
              y = ["value", "meanedValue"],
              figsize = (18,6))
plt.xticks(rotation=45)
plt.hlines(0, 0, len(fpgFrame))
plt.show()


# # <a class="anchor" id="12"></a>

# # Фильтрация

# In[116]:


fpg = fpgFrame["meanedValue"].to_numpy() # Список данных ЭКГ

yf = rfft(fpg) # мощность волн определённой частоты на графике
xf = rfftfreq(len(fpg), 1 / rate) # список всех частот на графике

plt.plot(xf, numpy.abs(yf))
plt.show()


# In[117]:


for i in range(len(xf)):
    if xf[i]<1 or xf[i]>10:
        yf[i]=0


# In[118]:


# Может быть придётся убрать
temp = irfft(yf)
temp = numpy.append(temp, temp.mean())

fpgFrame["filteredFPG"] = temp # Восстановление графика ЭКГ по частотам с графика выше


fpgFrame.plot(x = "index",
               y = ["meanedValue", "filteredFPG"],
               figsize = (18,6))
plt.xticks(rotation=45)
plt.show()


# # <a class="anchor" id="13"></a>

# # Нахождение R-зубцов

# In[119]:


rPeaks, _ = find_peaks(fpgFrame["filteredFPG"], height = 0, distance = 150)
rPeaks = rPeaks.tolist()

plt.figure(figsize=(23, 9))
plt.plot(fpgFrame["filteredFPG"])
plt.plot(rPeaks, fpgFrame["filteredFPG"][rPeaks], "x", label='R-зубцы')
plt.legend(loc='best')
plt.show()


# # <a class="anchor" id="14"></a>

# # Расчёт R-интервалов

# In[120]:


rIntervalsFPG = [] # Размер интервала между соседними R-зубцами в мс

for i in range(len(rPeaks) - 1):
    rIntervalsFPG.append((rPeaks[i + 1] - rPeaks[i]) / rate * 1000)

rIntervalsFPG.append(pd.Series(rIntervalsFPG).mean())


# In[121]:


plt.figure(figsize=(18, 6))
plt.plot(rIntervalsFPG, marker='o', label='Размер интервала', color='red')

for i in range(len(rIntervalsFPG)):
    plt.annotate(str(round(rIntervalsFPG[i])), (i - 0.5, rIntervalsFPG[i] - 25), fontsize=12, color='blue')

plt.xlabel('Номер интервала', fontsize=12)
plt.ylabel('Продолжительность интервала, мс', fontsize=12)
plt.legend(loc='lower right')
plt.show()


# # <a class="anchor" id="20"></a>

# # Сглаживание R-интервалов по 8-и записям

# In[122]:


smoothedIntervals = []
    
for i in range(7, len(rIntervalsFPG)):
    summ = 0
    
    for j in range(7):
        summ += rIntervalsFPG[i - j]
        
    smoothedIntervals.append(summ / 7)
    
rIntervalsFPG = smoothedIntervals


# In[123]:


plt.figure(figsize=(18, 6))
plt.plot(rIntervalsFPG, marker='o', label='Размер интервала', color='red')

for i in range(len(rIntervalsFPG)):
    plt.annotate(str(round(rIntervalsFPG[i])), (i - 0.5, rIntervalsFPG[i] - 25), fontsize=12, color='blue')

plt.xlabel('Номер интервала', fontsize=12)
plt.ylabel('Продолжительность интервала, мс', fontsize=12)
plt.legend(loc='lower right')
plt.show()


# # <a class="anchor" id="15"></a>

# # Гистограмма кардиоинтервалов

# In[124]:


minimumFPG = round(min(rIntervalsFPG))
maximumFPG = round(max(rIntervalsFPG))
print(str(minimumFPG) + " " + str(maximumFPG))

valuesFPG = []
countsFPG = []

tempConvert = pd.Series(rIntervalsFPG)

for i in range(minimumFPG, maximumFPG, 50):
    countsFPG.append(tempConvert.where(tempConvert >= i).where(tempConvert < i + 50).count())
    valuesFPG.append(i)

plt.hist(x = rIntervalsFPG, bins = valuesFPG)
plt.show()


# # <a class="anchor" id="16"></a>

# # Статистические метрики

# In[125]:


seriesIntervalsFPG = pd.Series(rIntervalsFPG)

# Математическое ожидание (RRNN) (Среднее значение)
MFPG = seriesIntervalsFPG.mean() / 1000
print("Математическое ожидание        = " + str(MFPG) + " с")

# Среднеквадратичное отклонение (SDNN) (Средний разброс элементов относительно мат. ожидания)
SFPG = seriesIntervalsFPG.std(ddof = 0) / 1000
print("Среднеквадратичное отклонение  = " + str(SFPG) + " с")

# Коэффициент вариации (CV) (То же среднеквадратичное отклонение, но с нормировкой по пульсу)
CVFPG = SFPG / MFPG * 100
print("Коэффициент вариации           = " + str(CVFPG))


# # <a class="anchor" id="17"></a>

# # Метрики вариационной пульсометрии

# In[126]:


# Мода (Наиболее часто встречающееся значение)
MoFPG = (valuesFPG[(len(valuesFPG) // 2) - 1] + 25) / 1000
print("Мода                           = " + str(MoFPG) + " с")

# Амплитуда моды (Процент значений входящих в моду)
AMoFPG = countsFPG[(len(valuesFPG) // 2) - 1] / len(rIntervalsFPG) * 100
print("Амплитуда моды                 = " + str(AMoFPG) + " %")

# Вариационный размах (Максимальная амплитуда значений)
DXFPG = (maximumFPG - minimumFPG) / 1000
print("Вариационный размах            = " + str(DXFPG) + " с")

# Вегетативный показатель ритма (Чем меньше ВПР, тем больше преобладает парасимпатический отдел)
VPRFPG = 1 / (MoFPG * DXFPG)
print("Вегетативный показатель ритма  = " + str(VPRFPG))

# Индекс напряжения регуляторных систем (Чем ниже, там сильнее парасимпатика. Чем выше, тем сильнее симпатика)
INFPG = AMoFPG / (2 * DXFPG * MoFPG)
print("Индекс напряжения              = " + str(INFPG))


# # <a class="anchor" id="18"></a>

# # Автокоррелограмма

# In[127]:


plot_acf(seriesIntervalsFPG, lags = 150)
autocorrelationFPG = acf(seriesIntervalsFPG, nlags = len(seriesIntervalsFPG) - 1)


# In[128]:


yf = rfft(autocorrelationFPG) # мощность волн определённой частоты на графике
xf = rfftfreq(len(autocorrelationFPG), 1 / 0.76) # список всех частот на графике
plt.axvline(x = 0.04, color = 'crimson')
plt.axvline(x = 0.15, color = 'crimson')

plt.plot(xf, numpy.abs(yf), color = "blue")
plt.show()


# In[129]:


VLF = []
LF = []
HF = []

for i in range(len(xf)):
    if (xf[i] <= 0.04):
        VLF.append(numpy.abs(yf[i]))
    if (xf[i] >= 0.04 and xf[i] <= 0.15):
        LF.append(numpy.abs(yf[i]))
    if (xf[i] >= 0.15):
        HF.append(numpy.abs(yf[i]))
        
allFrequenciesFPG = simps(numpy.abs(yf))
VLFFPG = simps(VLF / allFrequenciesFPG * 100)
LFFPG = simps(LF / allFrequenciesFPG * 100)
HFFPG = simps(HF / allFrequenciesFPG * 100)


# # <a class="anchor" id="19"></a>

# # Скатерограмма

# In[130]:


currentPeaksFPG = []
nextPeaksFPG = []

for i in range(len(rIntervalsFPG) - 1):
    currentPeaksFPG.append(rIntervalsFPG[i] / 1000)
    nextPeaksFPG.append(rIntervalsFPG[i + 1] / 1000)

plt.figure(figsize=(5,5))
plt.plot(currentPeaksFPG, nextPeaksFPG,'r+')

plt.show()


# # 

# # <a class="anchor" id="21"></a>

# # Сравнение данных

# In[131]:


plt.hist(x = rIntervalsECG, bins = valuesECG, label='ЭКГ')
plt.hist(x = rIntervalsFPG, bins = valuesFPG, label='ФПГ')
plt.legend(loc='upper right')
plt.show()


# In[132]:


print("                                   ЭКГ         ФПГ        Норма")
print("Минимум                        =  " + str(round(minimumECG / 1000, 2)) + " с      " + str(round(minimumFPG / 1000, 2)) + " с     0.7 с")
print("Максимум                       =  " + str(round(maximumECG / 1000, 2)) + " с      " + str(round(maximumFPG / 1000, 2)) + " с     0.9 с")
print("Математическое ожидание        =  " + str(round(MECG, 2)) + " с      " + str(round(MFPG, 2)) + " с     0.74-0.86 c")
print("Среднеквадратичное отклонение  =  " + str(round(SECG, 2)) + " с      " + str(round(SFPG, 2)) + " с     0.075-0.145 с")
print("Коэффициент вариации           =  " + str(round(CVECG, 2)) + "        " + str(round(CVFPG, 2)) + "       5-7")


# In[142]:


print("                                   ЭКГ         ФПГ        Норма")
print("Сверхмедленные волны           =  " + str(round(VLFECG, 2)) + " %     " + str(round(VLFFPG, 2)) + " %    20-50 %")
print("Медленны волны                 =  " + str(round(LFECG, 2)) + " %     " + str(round(LFFPG, 2)) + " %    20-50 %")
print("Высокочастотные волны          =  " + str(round(HFECG, 2)) + " %      " + str(round(HFFPG, 2)) + " %    15-45 %")


# In[153]:


print("                                   ЭКГ         ФПГ        Норма")
print("Мода                           =  " + str(round(MoECG, 2)) + " с      " + str(round(MoFPG, 2)) + " с      ---")
print("Амплитуда моды                 =  " + str(round(AMoECG, 2)) + " %     " + str(round(AMoFPG, 2)) + " %    30-50 %")
print("Вариационный размах            =  " + str(round(DXECG, 2)) + " с      " + str(round(DXFPG, 2)) + " с     ---")
print("Вегетативный показатель ритма  =  " + str(round(VPRECG, 2)) + "        " + str(round(VPRFPG, 2)) + "       3-10")
print("Индекс напряжения              =  " + str(round(INECG)) + "         " + str(round(INFPG)) + "        30-200 (но лучше 80-140)")


# In[134]:


plt.figure(figsize=(5,5))
plt.plot(currentPeaksECG, nextPeaksECG,'bx')
plt.plot(currentPeaksFPG, nextPeaksFPG,'r+')

plt.show()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




