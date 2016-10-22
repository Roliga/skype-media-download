skype-media-download
====================

A simple python script to download shared images.

Usage
=====

	Usage: skype-media-download.py [OPTIONS]

	Downloads shared media that is found in messages in Skype's main.db file.

	Options:
	  -c [file]    Cookie file to use.
			 Default: './cookies.txt'
	  -d [file]    Database file to use.
			 Default: './main.db'
	  -p [dir]     Output Directory.
			 Default: './Skype Media Download'

	  -E           Disable error logging.
	  -e [file]    Where to log download errors.
			 Default: './Skype Media Download/errors.log'

	  -S           Disable success logging and skipping.
	  -s [file]    Where to log and read previous successful downloads.
		       Used to skip files that have already been downloaded.
			 Default: './Skype Media Download/success.log'

	  -D           Dry run. Don't actually download or create any files.

Log in to web.skype.com, then export your browsers cookies. The script needs these to access the media.
After that find your Skype installation's main.db file. On Windows it's located somewhere under %AppData%, on Linux it's somwhere in your home directory and on Android it's under /data/data, which you need root to access.
