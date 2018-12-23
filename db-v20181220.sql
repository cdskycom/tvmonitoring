--附件表
CREATE TABLE `tvmonitoring`.`attachments` (
  `id` INT NOT NULL,
  `uuid` VARCHAR(50) NOT NULL,
  `doc_type` VARCHAR(45) NULL,
  `filename` VARCHAR(255) NULL,
  `size` BIGINT(20) NULL,
  PRIMARY KEY (`id`));

ALTER TABLE `tvmonitoring`.`attachments` 
ADD COLUMN `user_id` INT NULL AFTER `size`,
ADD INDEX `attachment_user_idx` (`user_id` ASC);
ALTER TABLE `tvmonitoring`.`attachments` 
ADD CONSTRAINT `attachment_user`
  FOREIGN KEY (`user_id`)
  REFERENCES `tvmonitoring`.`users` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;
ALTER TABLE `tvmonitoring`.`attachments` 
CHANGE COLUMN `id` `id` INT(11) NOT NULL AUTO_INCREMENT ;

-- 标签表
CREATE TABLE `tvmonitoring`.`tags` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`));

--案例表
CREATE TABLE `tvmonitoring`.`wikis` (
  `id` INT NOT NULL,
  `subject` VARCHAR(255) NOT NULL,
  `summary` VARCHAR(255) NULL,
  `attachment` INT NULL,
  `create_time` DATETIME NULL,
  `create_user` INT NULL,
  `create_user_name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_attachment_idx` (`attachment` ASC),
  INDEX `FK_user_idx` (`create_user` ASC),
  CONSTRAINT `FK_attachment`
    FOREIGN KEY (`attachment`)
    REFERENCES `tvmonitoring`.`attachments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_user`
    FOREIGN KEY (`create_user`)
    REFERENCES `tvmonitoring`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

ALTER TABLE `tvmonitoring`.`wikis` 
CHANGE COLUMN `id` `id` INT(11) NOT NULL AUTO_INCREMENT ;


--wiki-tag关联表
CREATE TABLE `tvmonitoring`.`wiki_tag` (
  `wiki_id` INT NOT NULL,
  `tag_id` INT NOT NULL,
  PRIMARY KEY (`wiki_id`, `tag_id`),
  INDEX `FK_tag_idx` (`tag_id` ASC),
  CONSTRAINT `FK_wiki`
    FOREIGN KEY (`wiki_id`)
    REFERENCES `tvmonitoring`.`wikis` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_tag`
    FOREIGN KEY (`tag_id`)
    REFERENCES `tvmonitoring`.`tags` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

--工单与附件关联表
CREATE TABLE `tvmonitoring`.`trouble_attachment` (
  `trouble_id` INT NOT NULL,
  `attachment_id` INT NOT NULL,
  PRIMARY KEY (`trouble_id`, `attachment_id`),
  INDEX `FK_attachment_idx` (`attachment_id` ASC),
  CONSTRAINT `FK_trouble_ticket`
    FOREIGN KEY (`trouble_id`)
    REFERENCES `tvmonitoring`.`trouble_tickets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_touble_attachment`
    FOREIGN KEY (`attachment_id`)
    REFERENCES `tvmonitoring`.`attachments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

