# Evernote SyncLink
<p>Syncs Evernote with a local directory and mirrors the files system down to one layer with notebooks.
Takes in a Evernote developer token and a directory path and then mirrors the directory to Evernote. </p>

# Quick Start:

<p>Put developer token into code.</p>
<code>run: python main.py -directorypath /../ -developertoken ... </code>
# Options:
"-directorypath /../" Followed by a path provides a path to sync that overrides the path hardcoded in.
"-developertoken ..." specifies a developer token and overrides the token hardcoded in.
"-nomanifest" ignores the upload manifest (DEBUG ONLY will continuously upload all files)

Developer tokens:
<p>      Development server: <a href=https://sandbox.evernote.com/api/DeveloperToken.action> Click here</a></p>
<p>      Production Server server: <a href=https://www.evernote.com/api/DeveloperToken.action> Click here</a></p>




 
