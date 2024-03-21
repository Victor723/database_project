-- \COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- -- since id is auto-generated; we need the next command to adjust the counter
-- -- for auto-generation so next INSERT will not clash with ids loaded above:
-- SELECT pg_catalog.setval('public.users_u_userkey_seq',
--                          (SELECT MAX(u_userkey)+1 FROM Users),
--                          false);
\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- -- since id is auto-generated; we need the next command to adjust the counter
-- -- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_u_userkey_seq',
                         (SELECT MAX(u_userkey)+1 FROM Users),
                         false);
\COPY Category FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.category_cat_catkey_seq',
                         (SELECT MAX(cat_catkey)+1 FROM Category),
                         false);

\COPY Seller FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.seller_s_sellerkey_seq',
                         (SELECT MAX(s_sellerkey)+1 FROM Seller),
                         false);

\COPY Product FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.product_p_productkey_seq',
                         (SELECT MAX(p_productkey)+1 FROM Product),
                         false);

-- \COPY Product FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.product_p_productkey_seq',
--                          (SELECT MAX(p_productkey)+1 FROM Product),
--                          false);

-- \COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM Purchases),
--                          false);

\COPY ProductReview FROM 'Product_Reviews.csv' WITH DELIMITER ',' NULL '' CSV

\COPY SellerReview FROM 'Seller_Reviews.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.cart_c_cartkey_seq',
                         (SELECT MAX(c_cartkey)+1 FROM Cart),
                         false);
                         
\COPY ProductSeller (ps_productkey, ps_sellerkey, ps_quantity, ps_price, ps_discount, ps_createtime) FROM 'ProductSellers.csv' WITH DELIMITER ',' NULL '' CSV HEADER;

\COPY ProductCart FROM 'ProductCarts.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.productcart_pc_prodcartkey_seq',
                         (SELECT MAX(pc_prodcartkey)+1 FROM ProductCart),
                         false);
