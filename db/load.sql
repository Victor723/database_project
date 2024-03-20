-- \COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- -- since id is auto-generated; we need the next command to adjust the counter
-- -- for auto-generation so next INSERT will not clash with ids loaded above:
-- SELECT pg_catalog.setval('public.users_u_userkey_seq',
--                          (SELECT MAX(u_userkey)+1 FROM Users),
--                          false);

\COPY Product FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.product_p_productkey_seq',
                         (SELECT MAX(p_productkey)+1 FROM Product),
                         false);

-- \COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM Purchases),
--                          false);

-- \COPY ProductReview FROM 'Product_Reviews.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.productreview_pr_productkey_seq',
--                          (SELECT MAX(pr_productkey)+1 FROM ProductReview),
--                          false);

-- \COPY SellerReview FROM 'Seller_Reviews.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.sellerreview_sr_sellerkey_seq',
--                          (SELECT MAX(sr_sellerkey)+1 FROM SellerReview),
--                          false);