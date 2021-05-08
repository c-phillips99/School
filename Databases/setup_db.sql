/*******************************************************************************
   Drop database if it exists
********************************************************************************/
DROP DATABASE IF EXISTS `Chess`;

/*******************************************************************************
   Create database
********************************************************************************/
CREATE DATABASE `Chess`;
USE `Chess`;

/*******************************************************************************
   Create Tables
********************************************************************************/
CREATE TABLE `Players`
(
    `PlayerId` VARCHAR(50) NOT NULL,
    `Username` VARCHAR(50) NOT NULL,
    `Name` VARCHAR(100),
    `Title` VARCHAR(5),
    `Country` VARCHAR(30),
    `FIDE` INT,
    `DailyRating` INT,
    `RapidRating` INT,
    `BlitzRating` INT,
    `BulletRating` INT,
    CONSTRAINT `PK_Album` PRIMARY KEY  (`PlayerId`)
);

CREATE TABLE `Clubs`
(
    `ClubId` VARCHAR(100) NOT NULL,
    `Name` VARCHAR(100) NOT NULL,
    `Country` VARCHAR(30),
    `URL`  VARCHAR(150),
    CONSTRAINT `PK_Clubs` PRIMARY KEY  (`ClubId`)
);

CREATE TABLE `Games`
(
    `GameId` INT NOT NULL AUTO_INCREMENT,
    `WhitePlayerId` VARCHAR(50) NOT NULL,
    `BlackPlayerId` VARCHAR(50) NOT NULL,
    `Date` DATETIME NOT NULL,
    `TimeClass` VARCHAR(8),
    `TimeControl` VARCHAR(10),
    `Result` CHAR(1), /* W, B, D */
    CONSTRAINT `PK_Games` PRIMARY KEY  (`GameId`, `WhitePlayerId`, `BlackPlayerId`, `Date`)
);

CREATE TABLE `Tournaments`
(
    `URLId` VARCHAR(150) NOT NULL,
    `Name` VARCHAR(50) NOT NULL,
    `TimeControl` VARCHAR(10),
    `TimeClass` VARCHAR(8),
    `Type` VARCHAR(20),
    `IsRated` BOOLEAN,
    `IsOfficial` BOOLEAN,
    CONSTRAINT `PK_Tournaments` PRIMARY KEY  (`URLId`)
);

CREATE TABLE `GameTurns`
(
    `GameId` INT NOT NULL,
    `Turn` INT NOT NULL,
    `WhiteMove` VARCHAR(10) NOT NULL,
    `BlackMove` VARCHAR(10),
    CONSTRAINT `PK_GameTurns` PRIMARY KEY  (`GameId`, `Turn`)
);

CREATE TABLE `PlayersClubs`
(
    `PlayerId` VARCHAR(50) NOT NULL,
    `ClubId` VARCHAR(100) NOT NULL,
    CONSTRAINT `PK_PlayersClubs` PRIMARY KEY  (`PlayerId`, `ClubId`)
);

CREATE TABLE `TournamentGames`
(
    `GameId` INT NOT NULL,
    `URLId` VARCHAR(150) NOT NULL,
    CONSTRAINT `PK_TournamentGames` PRIMARY KEY  (`GameId`, `URLId`)
);

/*******************************************************************************
   Create Foreign Keys
********************************************************************************/

ALTER TABLE `PlayersClubs` ADD CONSTRAINT `FK_PlayersClubsPlayersId`
    FOREIGN KEY (`PlayerId`) REFERENCES `Players` (`PlayerId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `PlayersClubs` ADD CONSTRAINT `FK_PlayersClubsClubsId`
    FOREIGN KEY (`ClubId`) REFERENCES `Clubs` (`ClubId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `TournamentGames` ADD CONSTRAINT `FK_TournamentGamesURLId`
    FOREIGN KEY (`URLId`) REFERENCES `Tournaments` (`URLId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `TournamentGames` ADD CONSTRAINT `FK_TournamentGamesGameId`
    FOREIGN KEY (`GameId`) REFERENCES `Games` (`GameId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Games` ADD CONSTRAINT `FK_GamesWhitePlayerId`
    FOREIGN KEY (`WhitePlayerId`) REFERENCES `Players` (`PlayerId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Games` ADD CONSTRAINT `FK_GamesBlackPlayerId`
    FOREIGN KEY (`BlackPlayerId`) REFERENCES `Players` (`PlayerId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `GameTurns` ADD CONSTRAINT `FK_GameTurnsGameId`
    FOREIGN KEY (`GameId`) REFERENCES `Games` (`GameId`) ON DELETE NO ACTION ON UPDATE NO ACTION;