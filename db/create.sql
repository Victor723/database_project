-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE ProductCart (
    pc_prodcartkey BIGINT NOT NULL,
    pc_cartkey BIGINT NOT NULL,
    pc_productkey BIGINT NOT NULL,
    pc_sellerkey BIGINT NOT NULL, 
    pc_savequantity BIGINT NOT NULL,
    pc_incartquantity BIGINT NOT NULL,
    PRIMARY KEY(pc_prodcartkey, pc_cartkey),
    FOREIGN KEY(pc_cartkey) REFERENCES Cart(c_cartkey),
    FOREIGN KEY(pc_productkey) REFERENCES ProductSeller(ps_productkey),
    FOREIGN KEY(pc_sellerkey) REFERENCES ProductSeller(ps_sellerkey)
);

CREATE TABLE Cart (
    c_cartkey BIGINT NOT NULL,
    c_userkey BIGINT NOT NULL
    PRIMARY KEY(c_cartkey),
    FOREIGN KEY(c_userkey) REFERENCES User(u_userkey)
);


CREATE TABLE Lineitem (
    l_linenumber BIGINT NOT NULL,
    l_orderkey BIGINT NOT NULL,
    l_productkey BIGINT NOT NULL,
    l_sellerkey BIGINT NOT NULL,
    l_quantity BIGINT NOT NULL,
    l_originalprice DOUBLE PRECISION NOT NULL,
    l_fulfillmentdate DATE,
    l_discount DOUBLE PRECISION,
    l_tax DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(l_linenumber, l_orderkey),
    FOREIGN KEY(l_orderkey) REFERENCES Order(o_orderkey),
    FOREIGN KEY(l_productkey) REFERENCES ProductSeller(ps_productkey),
    FOREIGN KEY(l_sellerkey) REFERENCES ProductSeller(ps_sellerkey)

);

CREATE TABLE Order (
    o_orderkey BIGINT NOT NULL,
    o_userkey BIGINT NOT NULL,
    o_totalprice BIGINT NOT NULL,
    o_ordercreatedate DATE NOT NULL,
    o_fulfillmentdate DATE
    PRIMARY KEY(o_orderkey),
    FOREIGN KEY(o_userkey) REFERENCES User(u_userkey)
);
