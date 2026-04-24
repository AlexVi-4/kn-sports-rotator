1. Swtich to the table view, to avoid scrolling, since currently it is pretty big
2. Create authorization (`USER_PASSCODE` to view the rotation, `ADMIN_PASSCODE` to manage rotations)
3. Create passcode to view the rotation
4. Make rotation persistent, so another people can see the ready rotation. Connect the database, add calendar (see db table structure below)
5. Change the ~Select players list", add the search bar, make list until end of the page, amount of players before the search bar, add the generate rotaation before the search bar

|Table        |Fields                                                               |
|-------------|---------------------------------------------------------------------|
|users        |full_name, power_level                                               |
|locations    |name, address                                                        |
|courts       |location_name, name                                                  |
|training_days|id, start_date_time, end_date_time, location_name                    |
|rotation     |training_day_id, start_date_time, end_date_time, court, team, players|
