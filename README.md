# reddit-imgur-parser
script to pull down files via imgur that were posted to reddit recently

- only from /r/eve (currently)
- ignores any 'album' and 'gallery' links (currently)
- saves files into directory 'imgurEVE' inside the repo

## Usage (python 3.5)
```bash
pip install requests
python parse.py > ouptut.txt  (more clean output. Also shows skipped links)
```
