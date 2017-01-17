# Evernote SyncLink
<p>Syncs Evernote with a local directory and mirrors the files system down to one layer with notebooks.
Takes in a Evernote developer token and a directory path and then mirrors the directory to Evernote. </p>

# Quick Start:

<p>Put developer token into code.</p>
<code>python main.py -directorypath /../ -developertoken ... </code>
# Options:
<ul>
<li>"-directorypath /../" Followed by a path provides a path to sync that overrides the path hardcoded in.</li>
<li>"-developertoken ..." specifies a developer token and overrides the token hardcoded in.</li>
<li>"-nomanifest" ignores the upload manifest (DEBUG ONLY will continuously upload all files)</li>
</ul>

# Developer tokens:
<p><ul>
<li>Development server: <a href=https://sandbox.evernote.com/api/DeveloperToken.action>Click here</a></li>
<li>Production Server server: <a href=https://www.evernote.com/api/DeveloperToken.action>Click here</a></li>
</ul>




 
