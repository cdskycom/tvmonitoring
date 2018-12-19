CREATE TABLE `tvmonitoring`.`region` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `region_code` VARCHAR(12) NOT NULL,
  `region_name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`));

INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510100000001', '高升桥实验室');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510100000000', '成都');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510100000002', '天府新区');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510300000000', '自贡');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510400000000', '攀枝花');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510500000000', '泸州');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510600000000', '德阳');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510700000000', '绵阳');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510800000000', '广元');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '510900000000', '遂宁');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511000000000', '内江');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511100000000', '乐山');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511300000000', '南充');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511400000000', '眉山');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511500000000', '宜宾');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511600000000', '广安');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511700000000', '达州');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511800000000', '雅安');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '511900000000', '巴中');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '512000000000', '资阳');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '513200000000', '阿坝');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '513300000000', '甘孜');
INSERT INTO `tvmonitoring`.`region` (`id`, `region_code`, `region_name`) VALUES (NULL, '513400000000', '凉山');

ALTER TABLE `tvmonitoring`.`trouble_tickets` 
ADD INDEX `starttime_idx` (`starttime` ASC);

ALTER TABLE `tvmonitoring`.`trouble_category` 
ADD COLUMN `category_type` VARCHAR(4) NULL AFTER `name`;

update tvmonitoring.trouble_category set category_type='INIT';
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('CDN问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('直播源问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('出流节点问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('中兴业务平台问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('易视腾业务平台问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('运营类问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('订购类问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('RMS问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('牌照方问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('本地接入侧问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('CP方问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('RMS问题', 'CONF');
INSERT INTO `tvmonitoring`.`trouble_category` (`name`, `category_type`) VALUES ('咨询类问题', 'CONF');

ALTER TABLE `tvmonitoring`.`trouble_tickets` 
ADD COLUMN `confirmed_type` VARCHAR(45) NULL AFTER `dealingtime`;


