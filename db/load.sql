\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
<<<<<<< Updated upstream
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);
=======
\COPY Category FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Product FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Seller FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductSeller FROM 'ProductSellers.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductReview FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV
\COPY SellerReview FROM 'SellerReviews.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Lineitem FROM 'Lineitems.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV
\COPY ProductCart FROM 'ProductCarts.csv' WITH DELIMITER ',' NULL '' CSV
>>>>>>> Stashed changes
