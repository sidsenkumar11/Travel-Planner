USE team1;

# Given a username or email address, is that user in the database?
select EXISTS(select username, email from user where username = 'soham32' or email = 'sdeval3@gatech.edu') as yes_or_no;

#Given a username or email address, is that user an admin user?
select is_admin from user where username = 'siddhi16' or email = 'sshah3@gatech.edu';

#Which attractions are open right now in Paris?
select distinct(attraction_name) from hour natural join attraction natural join address where curtime() between hour_start_time and hour_end_time and city = 'Paris';

#Which attractions in Paris don't require reservations?
select attraction_name from address natural join attraction where city = 'Paris' and attraction.attraction_name not in (select attraction_name from timeslot);

#Which attractions in Metz are free?
select attraction_name from (address join attraction using (address_id)) join activity using (attraction_name) where cost = 0 and city = 'Metz';

#Show the details for one attraction?
select * from attraction limit 1;

#List all the reviews for an attraction.
select * from review where attraction_name = 'Eiffel Tower';

#List all the reviews written by a particular user.
select * from review where username = 'vooha20';

#Show the details of one review.
select * from review limit 1;

#List the trips in the database for a particular user.
select * from trip where username = 'soham32';

#For an attraction that requires reservations and already has some reservations for a time slot, how many spots remain for that time slot?
select attraction_name, timeslot_id, timeslot_num_people - sum(reserves_num_people) as spots_left from timeslot natural join reserves group by timeslot_id;

#For one of the trips in the database that has two or more paid activities, what is the total cost of the trip?
select sum(cost) as total_cost from activity join trip using (trip_id) where trip_id = 1;

#For one of the public transportation locations in your database, which attractions are nearest to that location (list it as the nearest public transportation)?
select attraction_name from attraction where nearest_transport = 'Palais Royal - Musee du Louvre (Subway Station)';
