1. Swtich to the table view, to avoid scrolling, since currently it is pretty big
2. Create admin authorization
3. Create passcode to view the rotation
4. Make rotation persistent, so another people can see the ready rotation. Connect the database, add calendar
5. Change the ~Select players list", add the search bar, make list until end of the page, amount of players before the search bar, add the generate rotaation before the search bar

||Table||Fields||
|users|full_name, power_level|
|courts|name|
|training_calendar|id, start_date_time, end_date_time, location|
|rotation|training_calendar_id, start_date_time, end_date_time, court, team, players|
