# webcam-display
A simple, secure display of JPEG images uploaded from a webcam.

This repo contains the server components needed to display the images uploaded from the webcam. The setup I'm using for
a webcam is listed below in the Webcam Setup section, but this will work with any set of time-stamped images placed in 
a directory on the server.


# Setup

1.  Clone this repo to a location where it can statically run from. For this example I'll be using
`/mnt/fs/Webserver/webcam-display`. 
2.  Create the virtual environment inside there in the `venv` subdirectory: `python3 -m venv venv`
3.  Activate the venv `source venv/bin/activate`
4.  Install pre-requisites `pip3 install -r requirements.txt`
5.  Create a user to run the service `adduser --system --no-create-home --group webcamsvc`
6.  Update the `webcam-server.service` to include the paths to your repo.
7.  Move the `webcam-server.service` to the systemd service path:  `/lib/systemd/system/`
8.  Enable the service `systemctl enable webcam-server.service`
9.  Start the service `systemctl start webcam-server.service`

## TODO Items

*   Python script
    *   Run as systemd service
    *   Take config options of a path for source images, path for output images, image pattern 
        (e.g. `photo_2021-12-27_07-36-22.jpg` -> `photo_*.jpg`)
    *   ~~Output current image as `current.jpg`~~
    *   ~~Keep a set of prior images....6 for last minute, 10 for last 10 min, 6 for last hour, 24, for last day.~~
    *   Keep also as lower resolution images for lower res display
    *   ~~Creates a very small json file with the most recent image timestamp (UTC) in it~~
    *   ~~Create a json file with all the prior timestamps in it.~~
*   Web interface
    *   ~~Simple static html + javascript~~
    *   ~~Displays timestamp for image (in user's timezone)~~
    *   ~~Javascript automatically checks the json file to see if the images need to be refreshed~~
    *   Ability to scroll back through prior stored images
    *   ~~Scales with window size~~
        *  automatically picks correct .jpeg for size

## Webcam Setup

The webcam this is designed for is an old Android phone, running Pavel Khlebovich's excellent 
[IPWebCam](https://play.google.com/store/apps/details?id=com.pas.webcam&hl=en_US&gl=US) app. This is in conjunction 
with his [Filoader](https://play.google.com/store/apps/details?id=com.pas.ipwebcamftp&hl=en_US&gl=US) plugin app.

IPWebCam Setup

*   The "Regular photos" plugin enabled, set at every 10 seconds.
*   The "Uploaded" plugin enabled.
    *   "Remove uploaded files" checked
    *   SFTP Uploader in use. Set hostname and user first, then select the authenticate button, upload public key to
        server.
*   Video Preferences
    *   Photo Resolution - 4032x3024
    *   Video Recording
        *   Save videos to - Directory I created: `primary:Webcam`.  Photos are stored in `primary:Webcam/photos`
*   Set permissions to enable recording
*   Screen will remain on, so put a piece of black construction paper over it to avoid light from it.


