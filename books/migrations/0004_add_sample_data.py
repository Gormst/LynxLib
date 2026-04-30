from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0003_populate_book_genres"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                INSERT INTO Authors (authorID, first, last, bio, city, country)
                SELECT *
                FROM (VALUES
                    (101, 'Octavia', 'Butler', 'Award-winning science fiction author known for speculative fiction about power, survival, and community.', 'Pasadena', 'United States'),
                    (102, 'Ursula', 'Le Guin', 'Writer of science fiction and fantasy whose books explore anthropology, language, and social systems.', 'Berkeley', 'United States'),
                    (103, 'Toni', 'Morrison', 'Nobel Prize-winning novelist whose work examines memory, family, and American history.', 'Lorain', 'United States'),
                    (104, 'Neil', 'Gaiman', 'Author of fantasy, mythology, comics, and novels for adults and younger readers.', 'Portchester', 'United Kingdom'),
                    (105, 'Kazuo', 'Ishiguro', 'Novelist known for reflective stories about memory, duty, and identity.', 'Nagasaki', 'Japan'),
                    (106, 'N.K.', 'Jemisin', 'Speculative fiction writer known for richly built worlds and social themes.', 'Iowa City', 'United States'),
                    (107, 'Brandon', 'Sanderson', 'Fantasy author known for detailed magic systems and epic series.', 'Lincoln', 'United States'),
                    (108, 'Mary', 'Shelley', 'Author of Frankenstein and a foundational figure in science fiction and gothic literature.', 'London', 'United Kingdom'),
                    (109, 'Jane', 'Austen', 'Novelist known for social comedy, romance, and sharp observations of class and manners.', 'Steventon', 'United Kingdom'),
                    (110, 'Walter', 'Isaacson', 'Biographer and historian known for books about innovators, scientists, and leaders.', 'New Orleans', 'United States'),
                    (111, 'Michelle', 'Obama', 'Author, attorney, and former First Lady of the United States.', 'Chicago', 'United States'),
                    (112, 'Cal', 'Newport', 'Computer science professor and author writing about focus, work, and technology.', 'Washington', 'United States')
                ) AS sample(authorID, first, last, bio, city, country)
                WHERE NOT EXISTS (
                    SELECT 1 FROM Authors a WHERE a.authorID = sample.authorID
                );

                INSERT INTO Books (bookID, name, series_name, publisher, pub_date, genre, price, in_circulation_from, in_circulation_until, authorID)
                SELECT *
                FROM (VALUES
                    (101, 'Kindred', '', 'Doubleday', DATE '1979-06-01', 'Science Fiction', 14.99, DATE '2023-01-01', NULL::date, 101),
                    (102, 'Parable of the Sower', 'Earthseed', 'Four Walls Eight Windows', DATE '1993-10-01', 'Science Fiction', 15.50, DATE '2023-01-01', NULL::date, 101),
                    (103, 'A Wizard of Earthsea', 'Earthsea', 'Parnassus Press', DATE '1968-09-01', 'Fantasy', 10.99, DATE '2023-01-01', NULL::date, 102),
                    (104, 'The Left Hand of Darkness', 'Hainish Cycle', 'Ace Books', DATE '1969-03-01', 'Science Fiction', 13.75, DATE '2023-01-01', NULL::date, 102),
                    (105, 'Beloved', '', 'Alfred A. Knopf', DATE '1987-09-01', 'Historical Fiction', 12.95, DATE '2023-01-01', NULL::date, 103),
                    (106, 'Song of Solomon', '', 'Alfred A. Knopf', DATE '1977-09-01', 'Fiction', 11.95, DATE '2023-01-01', NULL::date, 103),
                    (107, 'American Gods', '', 'William Morrow', DATE '2001-06-19', 'Fantasy', 16.25, DATE '2023-01-01', NULL::date, 104),
                    (108, 'The Graveyard Book', '', 'HarperCollins', DATE '2008-09-30', 'Young Adult', 9.99, DATE '2023-01-01', NULL::date, 104),
                    (109, 'Never Let Me Go', '', 'Faber and Faber', DATE '2005-03-03', 'Literary Fiction', 12.50, DATE '2023-01-01', NULL::date, 105),
                    (110, 'The Remains of the Day', '', 'Faber and Faber', DATE '1989-05-01', 'Historical Fiction', 11.50, DATE '2023-01-01', NULL::date, 105),
                    (111, 'The Fifth Season', 'The Broken Earth', 'Orbit', DATE '2015-08-04', 'Fantasy', 14.50, DATE '2023-01-01', NULL::date, 106),
                    (112, 'The Obelisk Gate', 'The Broken Earth', 'Orbit', DATE '2016-08-16', 'Fantasy', 14.50, DATE '2023-01-01', NULL::date, 106),
                    (113, 'Mistborn: The Final Empire', 'Mistborn', 'Tor Books', DATE '2006-07-17', 'Fantasy', 13.99, DATE '2023-01-01', NULL::date, 107),
                    (114, 'The Way of Kings', 'The Stormlight Archive', 'Tor Books', DATE '2010-08-31', 'Fantasy', 18.99, DATE '2023-01-01', NULL::date, 107),
                    (115, 'Frankenstein', '', 'Lackington, Hughes, Harding, Mavor & Jones', DATE '1818-01-01', 'Gothic', 7.99, DATE '2023-01-01', NULL::date, 108),
                    (116, 'The Last Man', '', 'Henry Colburn', DATE '1826-01-01', 'Science Fiction', 8.99, DATE '2023-01-01', NULL::date, 108),
                    (117, 'Pride and Prejudice', '', 'T. Egerton', DATE '1813-01-28', 'Romance', 7.50, DATE '2023-01-01', NULL::date, 109),
                    (118, 'Emma', '', 'John Murray', DATE '1815-12-23', 'Classic', 8.25, DATE '2023-01-01', NULL::date, 109),
                    (119, 'Steve Jobs', '', 'Simon & Schuster', DATE '2011-10-24', 'Biography', 17.99, DATE '2023-01-01', NULL::date, 110),
                    (120, 'The Code Breaker', '', 'Simon & Schuster', DATE '2021-03-09', 'Biography', 18.50, DATE '2023-01-01', NULL::date, 110),
                    (121, 'Becoming', '', 'Crown', DATE '2018-11-13', 'Memoir', 16.99, DATE '2023-01-01', NULL::date, 111),
                    (122, 'The Light We Carry', '', 'Crown', DATE '2022-11-15', 'Memoir', 15.99, DATE '2023-01-01', NULL::date, 111),
                    (123, 'Deep Work', '', 'Grand Central Publishing', DATE '2016-01-05', 'Nonfiction', 13.50, DATE '2023-01-01', NULL::date, 112),
                    (124, 'Digital Minimalism', '', 'Portfolio', DATE '2019-02-05', 'Nonfiction', 12.99, DATE '2023-01-01', NULL::date, 112)
                ) AS sample(bookID, name, series_name, publisher, pub_date, genre, price, in_circulation_from, in_circulation_until, authorID)
                WHERE NOT EXISTS (
                    SELECT 1 FROM Books b WHERE b.bookID = sample.bookID
                );

                INSERT INTO Users (userID, first, last, is_staff, balance, mailing_address, zipcode)
                SELECT *
                FROM (VALUES
                    (101, 'Avery', 'Johnson', FALSE, 0.00, '14 Poplar St', '38105'),
                    (102, 'Maya', 'Patel', FALSE, 1.50, '229 Cooper Ave', '38104'),
                    (103, 'Noah', 'Williams', FALSE, 0.00, '82 Madison Pl', '38103'),
                    (104, 'Sophia', 'Garcia', FALSE, 3.25, '310 Central Ave', '38111'),
                    (105, 'Liam', 'Nguyen', FALSE, 0.00, '717 Highland St', '38112'),
                    (106, 'Isabella', 'Martinez', FALSE, 7.00, '909 Union Ave', '38126'),
                    (107, 'Ethan', 'Clark', FALSE, 0.75, '44 Rhodes Ln', '38107'),
                    (108, 'Amara', 'Wilson', FALSE, 0.00, '562 Parkway Dr', '38106'),
                    (109, 'Lucas', 'Anderson', FALSE, 2.00, '124 Beale St', '38103'),
                    (110, 'Grace', 'Thomas', FALSE, 0.00, '601 Front St', '38103'),
                    (111, 'Henry', 'Moore', FALSE, 4.50, '27 Peabody Ave', '38104'),
                    (112, 'Zoe', 'Taylor', FALSE, 0.00, '88 Evergreen Ter', '38117')
                ) AS sample(userID, first, last, is_staff, balance, mailing_address, zipcode)
                WHERE NOT EXISTS (
                    SELECT 1 FROM Users u WHERE u.userID = sample.userID
                );

                INSERT INTO Checkouts (userID, bookID, out_time, in_time, due_time, fine)
                SELECT *
                FROM (VALUES
                    (101, 101, TIMESTAMP WITH TIME ZONE '2026-04-01 09:00:00+00', NULL, TIMESTAMP WITH TIME ZONE '2026-05-15 09:00:00+00', 0.00),
                    (102, 103, TIMESTAMP WITH TIME ZONE '2026-03-20 10:30:00+00', NULL, TIMESTAMP WITH TIME ZONE '2026-04-20 10:30:00+00', 1.50),
                    (103, 105, TIMESTAMP WITH TIME ZONE '2026-04-10 13:15:00+00', NULL, TIMESTAMP WITH TIME ZONE '2026-05-10 13:15:00+00', 0.00),
                    (104, 107, TIMESTAMP WITH TIME ZONE '2026-02-15 15:00:00+00', TIMESTAMP WITH TIME ZONE '2026-03-01 12:00:00+00', TIMESTAMP WITH TIME ZONE '2026-03-01 15:00:00+00', 0.00),
                    (105, 111, TIMESTAMP WITH TIME ZONE '2026-03-05 11:20:00+00', TIMESTAMP WITH TIME ZONE '2026-03-25 16:45:00+00', TIMESTAMP WITH TIME ZONE '2026-03-19 11:20:00+00', 3.00),
                    (106, 115, TIMESTAMP WITH TIME ZONE '2026-04-12 08:40:00+00', NULL, TIMESTAMP WITH TIME ZONE '2026-05-12 08:40:00+00', 0.00),
                    (107, 119, TIMESTAMP WITH TIME ZONE '2026-01-10 14:10:00+00', TIMESTAMP WITH TIME ZONE '2026-01-22 09:25:00+00', TIMESTAMP WITH TIME ZONE '2026-01-24 14:10:00+00', 0.00),
                    (108, 121, TIMESTAMP WITH TIME ZONE '2026-04-05 12:05:00+00', NULL, TIMESTAMP WITH TIME ZONE '2026-05-05 12:05:00+00', 0.00),
                    (109, 123, TIMESTAMP WITH TIME ZONE '2026-03-01 09:15:00+00', TIMESTAMP WITH TIME ZONE '2026-03-30 10:00:00+00', TIMESTAMP WITH TIME ZONE '2026-03-15 09:15:00+00', 7.50),
                    (110, 117, TIMESTAMP WITH TIME ZONE '2026-04-18 17:30:00+00', NULL, TIMESTAMP WITH TIME ZONE '2026-05-18 17:30:00+00', 0.00)
                ) AS sample(userID, bookID, out_time, in_time, due_time, fine)
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM Checkouts c
                    WHERE c.userID = sample.userID
                      AND c.bookID = sample.bookID
                      AND c.out_time = sample.out_time
                );

                INSERT INTO Reservations (userID, bookID, reservation_time)
                SELECT *
                FROM (VALUES
                    (111, 101, TIMESTAMP WITH TIME ZONE '2026-04-21 10:00:00+00'),
                    (112, 103, TIMESTAMP WITH TIME ZONE '2026-04-22 11:30:00+00'),
                    (101, 115, TIMESTAMP WITH TIME ZONE '2026-04-22 14:10:00+00'),
                    (102, 121, TIMESTAMP WITH TIME ZONE '2026-04-23 09:45:00+00'),
                    (103, 117, TIMESTAMP WITH TIME ZONE '2026-04-23 16:20:00+00'),
                    (104, 111, TIMESTAMP WITH TIME ZONE '2026-04-24 08:55:00+00')
                ) AS sample(userID, bookID, reservation_time)
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM Reservations r
                    WHERE r.userID = sample.userID
                      AND r.bookID = sample.bookID
                );

                INSERT INTO Reviews (userID, bookID, book_name, score)
                SELECT *
                FROM (VALUES
                    (101, 102, 'Parable of the Sower', 10),
                    (102, 104, 'The Left Hand of Darkness', 9),
                    (103, 106, 'Song of Solomon', 8),
                    (104, 108, 'The Graveyard Book', 9),
                    (105, 110, 'The Remains of the Day', 8),
                    (106, 112, 'The Obelisk Gate', 10),
                    (107, 114, 'The Way of Kings', 9),
                    (108, 116, 'The Last Man', 7),
                    (109, 118, 'Emma', 8),
                    (110, 120, 'The Code Breaker', 9),
                    (111, 122, 'The Light We Carry', 8),
                    (112, 124, 'Digital Minimalism', 9)
                ) AS sample(userID, bookID, book_name, score)
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM Reviews r
                    WHERE r.userID = sample.userID
                      AND r.bookID = sample.bookID
                );

                INSERT INTO FavoriteAuthors (userID, authorID)
                SELECT *
                FROM (VALUES
                    (101, 101), (102, 102), (103, 103), (104, 104),
                    (105, 106), (106, 107), (107, 108), (108, 109),
                    (109, 110), (110, 111), (111, 112), (112, 101)
                ) AS sample(userID, authorID)
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM FavoriteAuthors fa
                    WHERE fa.userID = sample.userID
                      AND fa.authorID = sample.authorID
                );

                INSERT INTO FavoriteBooks (userID, bookID, authorID)
                SELECT *
                FROM (VALUES
                    (101, 102, 101), (102, 104, 102), (103, 105, 103), (104, 107, 104),
                    (105, 111, 106), (106, 114, 107), (107, 115, 108), (108, 117, 109),
                    (109, 119, 110), (110, 121, 111), (111, 123, 112), (112, 101, 101)
                ) AS sample(userID, bookID, authorID)
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM FavoriteBooks fb
                    WHERE fb.userID = sample.userID
                      AND fb.bookID = sample.bookID
                      AND fb.authorID = sample.authorID
                );

                INSERT INTO Promotions (promID, bookID, discount_percent, start_time, end_time)
                SELECT *
                FROM (VALUES
                    (101, 102, 15, TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-06-01 00:00:00+00'),
                    (102, 104, 10, TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-06-15 00:00:00+00'),
                    (103, 108, 20, TIMESTAMP WITH TIME ZONE '2026-04-10 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-05-30 00:00:00+00'),
                    (104, 110, 12, TIMESTAMP WITH TIME ZONE '2026-04-15 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-06-30 00:00:00+00'),
                    (105, 116, 25, TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-05-20 00:00:00+00'),
                    (106, 118, 10, TIMESTAMP WITH TIME ZONE '2026-04-20 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-07-01 00:00:00+00'),
                    (107, 120, 18, TIMESTAMP WITH TIME ZONE '2026-04-05 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-06-05 00:00:00+00'),
                    (108, 122, 15, TIMESTAMP WITH TIME ZONE '2026-04-01 00:00:00+00', TIMESTAMP WITH TIME ZONE '2026-05-25 00:00:00+00')
                ) AS sample(promID, bookID, discount_percent, start_time, end_time)
                WHERE NOT EXISTS (
                    SELECT 1 FROM Promotions p WHERE p.promID = sample.promID
                );
            """,
            reverse_sql="""
                DELETE FROM Promotions WHERE promID BETWEEN 101 AND 108;
                DELETE FROM FavoriteBooks WHERE userID BETWEEN 101 AND 112;
                DELETE FROM FavoriteAuthors WHERE userID BETWEEN 101 AND 112;
                DELETE FROM Reviews WHERE userID BETWEEN 101 AND 112;
                DELETE FROM Reservations WHERE userID BETWEEN 101 AND 112;
                DELETE FROM Checkouts WHERE userID BETWEEN 101 AND 112;
                DELETE FROM Books WHERE bookID BETWEEN 101 AND 124;
                DELETE FROM Authors WHERE authorID BETWEEN 101 AND 112;
                DELETE FROM Users WHERE userID BETWEEN 101 AND 112;
            """,
        ),
    ]
