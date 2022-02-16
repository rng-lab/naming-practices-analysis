-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema ProjetoArtigoNew_C++
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema NAMING_CATEGORIES
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `NAMING_CATEGORIES` DEFAULT CHARACTER SET utf8 ;
USE `NAMING_CATEGORIES` ;

-- -----------------------------------------------------
-- Table `NAMING_CATEGORIES`.`Identificador`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NAMING_CATEGORIES`.`Identificador` (
  `nome` VARCHAR(200) NOT NULL,
  `tipo` VARCHAR(200) NOT NULL,
  `posicao` VARCHAR(200) NULL,
  `projeto` VARCHAR(450) NOT NULL,
  `arquivo` VARCHAR(400) NULL,
  `nomeClasse` VARCHAR(450) NOT NULL,
  `nomeMetodo` VARCHAR(450) NULL)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
