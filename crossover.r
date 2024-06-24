library(nflfastR)
library(tidyverse)

pbp <- readr::read_csv("https://github.com/ryurko/nflscrapR-data/blob/master/play_by_play_data/regular_season/reg_pbp_2019.csv?raw=true") %>%
  dplyr::filter(home_team == "SF" & away_team == "SEA") %>%
  dplyr::select(desc, play_type, ep, epa, home_wp) %>%
  utils::head(6) %>%
  knitr::kable(digits = 3)

fastpbp <- nflfastR::fast_scraper("2019_10_SEA_SF") %>%
  nflfastR::clean_pbp() %>%
  dplyr::select(desc, play_type, ep, epa, home_wp, name) %>%
  utils::head(6) %>%
  knitr::kable(digits = 3)