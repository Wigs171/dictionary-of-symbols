@echo off
cd /d "C:\Users\16157\Desktop\Alchemical Dictionary"
echo.
echo === Extracting Dictionary of Symbols ===
echo.
"C:\Python313\python.exe" extract_symbols.py
echo.
echo === Generating HTML ===
echo.
"C:\Python313\python.exe" generate_symbols_html.py
echo.
echo === Done! Open symbols_dictionary.html to view ===
echo.
pause
