-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE ProductReview (
    pr_productkey BIGINT NOT NULL,
    pr_userkey BIGINT NOT NULL,
    pr_productname VARCHAR(255) NOT NULL,
    pr_orderkey BIGINT NOT NULL,
    pr_reviewdate DATE NOT NULL,
    pr_review TEXT NOT NULL,
    PRIMARY KEY (pr_productkey, pr_userkey),
    FOREIGN KEY(pr_productkey) REFERENCES Product(p_productkey),
    FOREIGN KEY(pr_userkey) REFERENCES User(u_userkey)
);

CREATE TABLE SellerReview (
    sr_sellerkey BIGINT NOT NULL,
    sr_userkey BIGINT NOT NULL,
    sr_sellername VARCHAR(255) NOT NULL,
    sr_orderkey BIGINT NOT NULL,
    sr_reviewdate DATE NOT NULL,
    sr_review TEXT NOT NULL,
    sr_rating INT NOT NULL,
    PRIMARY KEY (sr_sellerkey, sr_userkey),
    FOREIGN KEY(sr_sellerkey) REFERENCES Seller(s_sellerkey),
    FOREIGN KEY(sr_userkey) REFERENCES User(u_userkey)
);

