csvpath <- "/home/jg/Code/football/team_grades_2021.csv"

data <- read.csv(csvpath)
prsh <- data[ , c("PRSH")]
cov <- data[ , c("COV")]
wins <- data[ , c("W")]

regprsh <- lm(wins ~ prsh)
regcov <- lm(wins ~ cov)

plot(prsh, wins, axes = FALSE,
    main = "Passrush vs. Wins",
    xlab = "PFF Passrushing grade",
    xlim = c(0,100),
    ylab = "Wins",
    ylim = c(0,max(wins))
)
axis(1, at = 0:100)
axis(2, at = 0:max(wins))
abline(regprsh)
plot(cov, wins, axes = FALSE,
     main = "Coverage vs. Wins",
     xlab = "PFF Coverage grade",
     xlim = c(0,100),
     ylab = "Wins",
     ylim = c(0,max(wins))
)
axis(1, at = 0:100)
axis(2, at = 0:max(wins))

abline(regcov)