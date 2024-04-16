\COPY Users FROM 'Users.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);
SELECT pg_catalog.setval('public.users_u_userkey_seq', (SELECT MAX(u_userkey)+1 FROM Users), false);

\COPY Category FROM 'Categories.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);
SELECT pg_catalog.setval('public.category_cat_catkey_seq', (SELECT MAX(cat_catkey)+1 FROM Category), false);

\COPY Seller FROM 'Sellers.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);
SELECT pg_catalog.setval('public.seller_s_sellerkey_seq', (SELECT MAX(s_sellerkey)+1 FROM Seller), false);

\COPY Product FROM 'Products.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);
SELECT pg_catalog.setval('public.product_p_productkey_seq', (SELECT MAX(p_productkey)+1 FROM Product), false);

\COPY ProductSeller (ps_productkey, ps_sellerkey, ps_quantity, ps_price, ps_discount, ps_createtime) FROM 'ProductSellers.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);

\COPY Cart FROM 'Carts.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);
SELECT pg_catalog.setval('public.cart_c_cartkey_seq',
                         (SELECT MAX(c_cartkey)+1 FROM Cart),
                         false);                     

\COPY ProductCart FROM 'ProductCarts.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);
SELECT pg_catalog.setval('public.productcart_pc_prodcartkey_seq',
                         (SELECT MAX(pc_prodcartkey)+1 FROM ProductCart),
                         false);


\COPY Orders FROM 'Orders.csv' WITH (FORMAT csv, DELIMITER ',', NULL '\N', HEADER);
SELECT pg_catalog.setval('public.orders_o_orderkey_seq',
                         (SELECT MAX(o_orderkey)+1 FROM Orders),
                         false);

\COPY Lineitem FROM 'LineItems.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);

\COPY ProductReview FROM 'ProductReviews.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);

\COPY SellerReview FROM 'SellerReviews.csv' WITH (FORMAT csv, DELIMITER ',', NULL '', HEADER);
