-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Seller (
    s_sellerkey BIGINT NOT NULL,
    s_userkey BIGINT NOT NULL,
    s_registrationdate DATE NOT NULL,
    PRIMARY KEY s_sellerkey,
    FOREIGN KEY (s_userkey) REFERENCES User(u_userkey)
);
