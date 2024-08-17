library(tidyverse)
library(tidytext)
library(SnowballC)
library(scales)
#library(hunspell)
#library(proustr)

library(tm)
library(ggplot2)
library(dplyr)

wd = "C:\\Users\\chizi\\Documents\\GitHub\\MSIS 5223\\project-deliverable-2-apt-rent\\data"
setwd(wd)

temptable = paste(wd, "\\final_aptrent.csv", sep = "")
apt_data = read.csv(temptable, header = TRUE)

summary(apt_data)

apt_descr = apt_data %>% 
    select(descr)

tidy_dataset = apt_descr %>% 
    unnest_tokens(word, descr)

# find the most popular words
result1 = tidy_dataset %>%
  count(word) %>%
  arrange(desc(n)) %>%
  ungroup %>%
  slice(1:30)

# remove the stop words
data("stop_words")

tidy_dataset2 = tidy_dataset %>%
  anti_join(stop_words)

tidy_dataset2 %>%
  count(word) %>%
  arrange(desc(n)) %>%
  ungroup %>%
  slice(1:30)

# remove numerical
patterndigits = '\\b[0-9]+\\b'
tidy_dataset2$word = tidy_dataset2$word %>%
  str_remove_all(patterndigits)

tidy_dataset2 %>%
  count(word) %>%
  arrange(desc(n)) %>%
  ungroup %>%
  slice(1:30)

# Replace all new lines, tabs, and blank spaces with a value of nothing
tidy_dataset2$word = tidy_dataset2$word %>%
  str_replace_all('[:space:]', '')

tidy_dataset3 = tidy_dataset2 %>% 
  filter(!(word == ''))

tidy_dataset3 %>%
  count(word) %>%
  arrange(desc(n)) %>%
  ungroup %>%
  slice(1:30)

# Plot the the words with a proportion greater than 0.5
frequency = tidy_dataset3 %>%
  count(word) %>%
  arrange(desc(n)) %>%
  mutate(proportion = (n / sum(n)*100)) %>%
  filter(proportion >= 0.5)

ggplot(frequency, aes(x = proportion, y = word)) +
  geom_abline(color = "#f31616", lty = 2) +
  geom_jitter(alpha = 0.1, size = 3, width = 0.5, height = 0.5) +
  geom_text(aes(label = word), check_overlap = TRUE, vjust = 1) +
  scale_color_gradient(limits = c(0, 0.001), low = "#04b9b9", high = "gray75") +
  theme(legend.position="none") +
  labs(y = 'Word', x = 'Proportion') +
  geom_point()

# result: don't have to delete specific words

# stem the data
tidy_dataset4 = tidy_dataset3 %>%
  mutate_at("word", funs(wordStem((.), language="english")))

tidy_dataset4 %>%
  count(word) %>%
  arrange(desc(n)) %>%
  ungroup %>%
  slice(1:30)

frequency2 = tidy_dataset4 %>%
  count(word) %>%
  arrange(desc(n)) %>%
  mutate(proportion = (n / sum(n)*100)) %>%
  filter(proportion >= 0.5)

ggplot(frequency2, aes(x = proportion, y = word)) +
  geom_abline(color = "#f31616", lty = 2) +
  geom_jitter(alpha = 0.1, size = 3, width = 0.5, height = 0.5) +
  geom_text(aes(label = word), check_overlap = TRUE, vjust = 1) +
  scale_color_gradient(limits = c(0, 0.001), low = "#04b9b9", high = "gray75") +
  theme(legend.position="none") +
  labs(y = 'Word', x = 'Proportion') +
  geom_point()

# Result: The term "BEDROOM" is now 1st instead of 2nd, 
# we will use the number of bedrooms as a categorical variable to create the following models

# ------------------ Sentiment Analysis -----------------------
library(wordcloud)
library(udpipe)
library(lattice)

# we assume positive words would be much more than negative
tidy_dataset4 %>%
  inner_join(get_sentiments('bing')) %>% 
  count(sentiment) %>% 
  spread(sentiment, n, fill = 0) %>% 
  mutate(diffsent = positive - negative)

### joy vs sad
nrc_joysad = get_sentiments('nrc') %>%
  filter(sentiment == 'joy' | 
           sentiment == 'sadness')

nrow(nrc_joysad)

newjoin2 = inner_join(tidy_dataset4, nrc_joysad)

counts1 = count(newjoin2, word, sentiment)
spread2 = spread(counts1, sentiment, n, fill = 0)
spread2

# new variable - contentment = joy - sadness
(descr_joysad = tidy_dataset4 %>%
  inner_join(nrc_joysad) %>%
  count(word, sentiment) %>%
  spread(sentiment, n, fill = 0) %>%
  mutate(contentment = joy - sadness, linenumber = row_number()) %>%
  arrange(desc(contentment)))

ggplot(descr_joysad, aes(x=linenumber, y=contentment)) +
  coord_flip() +
  theme_light(base_size = 15) +
  labs(
    x='Index Value',
    y='Contentment'
  ) +
  theme(
    legend.position = 'none',
    panel.grid = element_blank(),
    axis.title = element_text(size = 10),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10)
  ) +
  geom_col()

# focus on the top 10 positive contentment words and the bottom 10 negative contentment words
(descr_joysad2 = descr_joysad %>%
    slice(1:10,164:173))

ggplot(descr_joysad2, aes(x=linenumber, y=contentment, fill=word)) +
  coord_flip() +
  theme_light(base_size = 15) +
  labs(
    title = 'Sentiment Analysis for Apartment Description - Joy vs. Sadness',
    x='Index Value',
    y='Contentment'
  ) +
  theme(
    legend.position = 'bottom',
    panel.grid = element_blank(),
    axis.title = element_text(size = 10),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    title = element_text(size = 12)
  ) +
  geom_col()

### trust vs fear
nrc_trstfear = get_sentiments('nrc') %>%
  filter(sentiment == 'trust' |
           sentiment == 'fear')

nrow(nrc_trstfear)

newjoin3 = inner_join(tidy_dataset4, nrc_trstfear)

counts2 = count(newjoin3, word, sentiment)
spread3 = spread(counts2, sentiment, n, fill = 0)
spread3

# create a new variable trustworthy = trust - fear
(descr_trstfear = tidy_dataset4 %>%
  inner_join(nrc_trstfear) %>%
  count(word, sentiment) %>%
  spread(sentiment, n, fill = 0) %>%
  mutate(trustworthy = trust - fear, linenumber = row_number()) %>%
  arrange(desc(trustworthy)) %>%
  slice(1:10,231:240))

ggplot(descr_trstfear, aes(x=linenumber, y=trustworthy, fill=word)) +
  coord_flip() +
  theme_light(base_size = 15) +
  labs(
    title = 'Sentiment Analysis for Apartment Description - Trust vs. Fear',
    x='Index Value',
    y='Trustworthiness'
  ) +
  theme(
    legend.position = 'bottom',
    panel.grid = element_blank(),
    axis.title = element_text(size = 10),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    title = element_text(size = 12)
  ) +
  geom_col()








