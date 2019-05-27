RELEASE_TYPE: patch

Fix two bugs related to the source URL field in the web app:

*   Only display the source link if the database has a non-empty value; don't display an empty link
*   Only store values in the database if they're non-empty; don't store empty strings