# LotusRPA

## Status: In Development ⚙️

## Warnings⚠️: 
- To run this project, make sure to install Chorme Web Driver on your PC, you can install it here: https://developer.chrome.com/docs/chromedriver/downloads
- Remember to install the version according to your Chrome Version
- You'll also need to install Python: https://www.python.org/
- You also need to install Git, to clone this repo: https://git-scm.com/downloads
- And the last app you need in your PC it's Visual Studio Code, after VSCode installation, go to VsCode Marketplace and download it Python extension.
- Don't forget to place your CPF sheet on the project root, you need to name the sheet as the following name "planilha.xlsx"

After that, just run the following command line:

First we need to clone this repo, so in the folder you want to save this repo, run: 

```javascript
git clone
```

## Some add commands
### In root folder, setup your virtual environment: 

```javascript
python -m venv .venv
.venv\Scripts\activate
```

Now let's install the project dependencies:
```javascript
pip install selenium pandas openpyxl
```

Now you can already run the project


```javascript
python main.py
```

