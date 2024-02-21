-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Seller (
    sr_sellerkey BIGINT NOT NULL PRIMARY KEY,
    sr_userkey BIGINT NOT NULL,
    sr_registrationdate DATE NOT NULL
);

   ALTER TABLE Seller
ADD CONSTRAINT seller_user_fk
   FOREIGN KEY (sr_userkey) REFERENCES user(u_userkey);
