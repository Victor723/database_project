-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Seller (
    s_sellerkey BIGINT NOT NULL,
    s_userkey BIGINT NOT NULL,
    s_registrationdate DATE NOT NULL,
    PRIMARY KEY s_sellerkey,
    FOREIGN KEY (s_userkey) REFERENCES User(u_userkey)
);
<<<<<<< Updated upstream
=======


CREATE TABLE ProductSeller (
    ps_productkey BIGINT NOT NULL,
    ps_sellerkey BIGINT NOT NULL,
    ps_quantity BIGINT NOT NULL,
    ps_price DOUBLE PRECISION NOT NULL,
    ps_discount DOUBLE PRECISION,
    ps_createtime DATE NOT NULL,
    PRIMARY KEY (ps_productkey, ps_sellerkey),
    FOREIGN KEY (ps_productkey) REFERENCES Product(p_productkey),
    FOREIGN KEY (ps_sellerkey) REFERENCES Seller(s_sellerkey)
);

CREATE TABLE ProductReview (
    pr_productkey BIGINT NOT NULL,
    pr_userkey BIGINT NOT NULL,
    pr_productname VARCHAR(255) NOT NULL,
    pr_orderkey BIGINT NOT NULL,
    pr_reviewdate DATE NOT NULL,
    pr_review TEXT NOT NULL,
    pr_rating DECIMAL(2,1) NOT NULL,
    PRIMARY KEY (pr_productkey, pr_userkey),
    FOREIGN KEY(pr_productkey) REFERENCES Product(p_productkey),
    FOREIGN KEY(pr_userkey) REFERENCES Users(u_userkey)
);

CREATE TABLE SellerReview (
    sr_sellerkey BIGINT NOT NULL,
    sr_userkey BIGINT NOT NULL,
    sr_sellername VARCHAR(255) NOT NULL,
    sr_orderkey BIGINT NOT NULL,
    sr_reviewdate DATE NOT NULL,
    sr_review TEXT NOT NULL,
    sr_rating DECIMAL(2,1) NOT NULL,
    PRIMARY KEY (sr_sellerkey, sr_userkey),
    FOREIGN KEY(sr_sellerkey) REFERENCES Seller(s_sellerkey),
    FOREIGN KEY(sr_userkey) REFERENCES Users(u_userkey)
);

CREATE TABLE Cart (
    c_cartkey BIGINT NOT NULL,
    c_userkey BIGINT NOT NULL,
    PRIMARY KEY(c_cartkey),
    FOREIGN KEY(c_userkey) REFERENCES Users(u_userkey)
);


CREATE TABLE ProductCart (
    pc_prodcartkey BIGINT NOT NULL,
    pc_cartkey BIGINT NOT NULL,
    pc_productkey BIGINT NOT NULL,
    pc_sellerkey BIGINT NOT NULL, 
    pc_savequantity BIGINT NOT NULL,
    pc_incartquantity BIGINT NOT NULL,
    PRIMARY KEY(pc_prodcartkey, pc_cartkey),
    FOREIGN KEY(pc_cartkey) REFERENCES Cart(c_cartkey),
    FOREIGN KEY(pc_productkey, pc_sellerkey) REFERENCES ProductSeller(ps_productkey, ps_sellerkey)
);

CREATE TABLE Orders (
    o_orderkey BIGINT NOT NULL,
    o_userkey BIGINT NOT NULL,
    o_totalprice DOUBLE PRECISION NOT NULL,
    o_ordercreatedate DATE NOT NULL,
    o_fulfillmentdate DATE,
    PRIMARY KEY(o_orderkey),
    FOREIGN KEY(o_userkey) REFERENCES Users(u_userkey)
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
    FOREIGN KEY(l_orderkey) REFERENCES Orders(o_orderkey),
    FOREIGN KEY(l_productkey, l_sellerkey) REFERENCES ProductSeller(ps_productkey, ps_sellerkey)
);
>>>>>>> Stashed changes
