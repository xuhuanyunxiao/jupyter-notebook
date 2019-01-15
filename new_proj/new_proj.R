

library(readxl)
library(lavaan)
library(semPlot)
library(OpenMx)
library(GGally)
library(corrplot) 

file_folder <- "D:/XH/Python_Project/notebook/new_proj"
# getwd()
setwd(file_folder)

data <- read_excel('data_sel_1.xlsx')


model1 = 'Z ~ x1 + x2 + x3 + Y

2Y ~ x1 + x2'

fit1 = cfa(model1, data = data1)
summary(fit1, fit.measures = TRUE, standardized = TRUE, rsquare = TRUE)
semPaths(fit1, 'std', layout = 'circle') 