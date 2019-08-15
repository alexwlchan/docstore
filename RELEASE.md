RELEASE_TYPE: patch

This changes the way database migrations work, so they should be a lot faster and properly atomic.  When you start an instance docstore and it needs to run a migration, the web server should start a lot faster.