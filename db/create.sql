-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.


CREATE TABLE Product (
    p_productkey BIGINT PRIMARY KEY NOT NULL,
    p_shortname VARCHAR(255) NOT NULL,
    p_description TEXT NOT NULL,
    p_imageurl VARCHAR(255) NOT NULL,
    p_price DOUBLE PRECISION NOT NULL,
    p_category_key BIGINT NOT NULL,
    p_link TEXT NOT NULL,
    FOREIGN KEY (p_category_key) REFERENCES Category(cat_key)
);

CREATE TABLE ProductSeller (
    ps_productkey BIGINT NOT NULL,
    ps_sellerkey BIGINT NOT NULL,
    ps_quantity BIGINT NOT NULL,
    ps_price DOUBLE PRECISION NOT NULL,
    ps_discount DOUBLE PRECISION,
    ps_createtime DATE NOT NULL,
    PRIMARY KEY (ps_productkey, ps_sellerkey),
    FOREIGN KEY (ps_productkey) REFERENCES Product(p_productkey)
);

CREATE TABLE Category (
    cat_key BIGINT PRIMARY KEY NOT NULL,
    cat_name VARCHAR(255) NOT NULL
);

