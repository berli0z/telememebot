# rename this file to config.py after you have finished editing it

# constants
## production mode
TOKEN ='xxxxxxx:yyyyyyyyyyyyyyyyyyyyy' # token for the prod telegram bot
CHANNEL_ID = '-100xxxxxxxxx' # id for the control channel (where only admins are, they will approve memes)

## test mode:
#TOKEN ='xxxxxxx:yyyyyyyyyyyyyyyyyyyyy'
#CHANNEL_ID = '-100xxxxxxxxx'

GOOGLE_CREDENTIALS = 'mycredentials.json' # where the file is
SPREADSHEET = "https://docs.google.com/spreadsheets/d/your_spreadsheet_id_here/"
FOLDER_ID = 'folder_id_of_drive_to_save_images'


# flask api config
DOC_URL = "https://docs.google.com/spreadsheet/ccc?key=GOOGLE_SHEETS_ID_HERE&output=csv"
WAIT_SECONDS = 3600
user = 'YOUR_ADMIN_USERNAME_FOR_API_AUTH'
pwd = 'AND_THE_PASSWORD'

# names for the categories keyboard
categories_keyboard = [['1.Ragecomics/lolcats'],
                    ['2.goldenage/impact/marketing'],
                    ['3.relatable,twitter'],
                    ['4.political/hyperstitional'],
                    ['5.chad&virgin/queer/wojak/NPC'],
                    ['6.me_irl/tumblr/instawave'],
                    ['7.metameme/recursive'],
                    ['8.esoteric/conspiracy'],
                    ['9.surreal'],
                    ['10.friedmemes/blacktwitter'],
                    ['0.Unknown']]

