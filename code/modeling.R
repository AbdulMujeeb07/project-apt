library(psych)
library(ggplot2)
library(Hmisc)
library(car)
library(corrplot)
library(dplyr)
library(Metrics)
library(tidyverse)
library(olsrr)
library(lmtest)
#install.packages("Metrics")

wd = "C:\\Users\\chizi\\Documents\\GitHub\\MSIS 5223\\project-deliverable-2-apt-rent\\data"
setwd(wd)

temptable = paste(wd, "\\final_aptrent.csv", sep = "")
apt_data = read.csv(temptable, header = TRUE)

str(apt_data)
year_apt <- apt_data$year
num_bed <- apt_data$beds
num_bath <- apt_data$baths
price <- apt_data$price
area <- apt_data$sqft

df_model <- data.frame(year_apt, num_bed, num_bath, area, price)
head(df_model)

## 3 Visualizations
# The 1st is the distribution of price - right skewed
# qq plot and the Histogram of price

# The 2nd is the plot of target variable components
# Bedrooms
describe(apt_data$beds)
# Bathrooms
describe(apt_data$baths)
# area
describe(apt_data$sqft)
# year
describe(apt_data$year)
# price
describe(apt_data$price)

pairs(df_model, panel=panel.smooth)
# Result: only sftp can research a linear relationship with price.
# The rest variables like bathrooms, bedrooms, even thought their data type are integers, we still need categorize regression

cor(df_model)
corrplot(cor(df_model),method = 'color',addCoef.col = 'black')

# Data spliting
# we select 60% (train) and 40% (test) because this portion give similar mean, median, min, max
df_model$id <- 1:nrow(df_model)

train_data <- df_model %>% dplyr::sample_frac(0.60)
test_data <- dplyr::anti_join(df_model, train_data, by = 'id')

nrow(df_model)
nrow(train_data)
nrow(test_data)

describe(df_model)
describe(train_data)
describe(test_data)

# multiple regression for initial model
model_reg = lm(df_model$price~df_model$num_bed+df_model$num_bath+df_model$area+df_model$year_apt)
summary(model_reg)

train_reg = lm(train_data$price~train_data$num_bed+train_data$num_bath+train_data$area+train_data$year_apt)
summary(train_reg)

test_reg = lm(test_data$price~test_data$num_bed+test_data$num_bath+test_data$area+test_data$year_apt)
summary(test_reg)

# Multicollinearity
ols_vif_tol(model_reg)
ols_vif_tol(train_reg)
ols_vif_tol(test_reg)

# Nomality
durbinWatsonTest(model_reg)
durbinWatsonTest(train_reg)
durbinWatsonTest(test_reg)

# mean_absolute_error
mae(df_model$price, predict(model_reg))
mae(train_data$price, predict(train_reg))
mae(test_data$price, predict(test_reg))

# mean square error
mse <- function(model_reg) 
mse <- function(train_reg) 
mse <- function(test_reg) 
mean(model_reg$residuals^2)
mean(train_reg$residuals^2)
mean(test_reg$residuals^2)
