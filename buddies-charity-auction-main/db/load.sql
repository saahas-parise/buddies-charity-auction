\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Charities FROM 'Charities.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.charities_id_seq',
                         (SELECT MAX(id)+1 FROM Charities),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Sells FROM 'Sells.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases), 
                         false);

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_id_seq',
                         (SELECT MAX(id)+1 FROM Orders), 
                         false);

\COPY Wishlist FROM 'Wishes.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.wishlist_id_seq',
                         (SELECT MAX(id)+1 FROM Wishlist),
                         false);
\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.cart_id_seq',
                         (SELECT MAX(id)+1 FROM Cart),
                         false);

\COPY Reviews FROM 'Reviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.reviews_id_seq',
                         (SELECT MAX(id)+1 FROM Reviews),
                         false);

\COPY Reviewtransactions FROM 'Reviewtransactions.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.reviewtransactions_id_seq',
                         (SELECT MAX(id)+1 FROM Reviewtransactions),
                         false);

\COPY Bids FROM 'Bids.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.bids_id_seq',
                         (SELECT MAX(id)+1 FROM Bids),
                         false);

\COPY Messages FROM 'Messages.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.messages_id_seq',
                         (SELECT MAX(id)+1 FROM Messages),
                         false);

\COPY MessageThreads FROM 'MessageThreads.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.messagethreads_id_seq',
                         (SELECT MAX(id)+1 FROM MessageThreads),
                         false);

