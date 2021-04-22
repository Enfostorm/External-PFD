PFD V0 22-4-2021

=================== Doel van deze versie ===================
Een eerste werkende app maken die verschillende elementen combineert en deze op één scherm weergeeft. Er is nog geen aandacht besteed aan het mooi afwerken van de code: De enige code die gebruikt wordt is PFD.py en pfdapp.kv, andere files staan voor referentie in de map

Code in deze main files is aangepast ten opzichte van de referentiefiles!!!

=================== Functies van deze versie ===================
	- Artificiële horizon
Pitch, roll en slip worden correct weergegeven in de bovenste helft. Centerlijn kan dikker in een volgende versie, voor betere zichtbaarheid.
	- 6 infodisplays
Nog niet aangestuurd, zitten erin voor proof-of-concept
	- Kompas
Heading en headingbug worden op het kompas weergegeven. Dit kompas is een eerste test, moet nog verder afgewerkt worden.
	- Aanstuurbaarheid over een seriële link
Momenteel worden er 5 waarden door de link doorgestuurd. Momenteel gebeurt dit aan 30Hz, met flushen van de buffers kan dit misschien hoger ingesteld worden. 

=================== Gebruik van deze versie ===================
Run PFD.py op één computer (of RPi), run de serial remote op een andere computer, verbind deze met een USB-kabel -> FTDI-adapter -> GPIO-pinnen, beweeg de sliders en de PFD zal meebewegen.

=================== TODO ===================
	- Programma herschrijven zodat de verschillende widgets verschillende files gebruiken om het project overzichtelijk te houden.
	- Altitude, speed-, vertical speedindicatoren/bugs, bugknoppen toevoegen
	- Bij het kompas een heading-readout zetten
	- Meer kanalen toevoegen bij de seriële link, standaardvolgorde voor waarden opstellen
	- Encoders voor aansturen van de bugs implementeren
	- Touch-input voor kivy 90° draaien, staat blijkbaar los van de systeem-touch mapping.

Minder dringende TODO's
	- cautionary snelheden weergeven
	- cautionary snelheden instellen via USB en on-screen instellingen
	- Centerlijn artificiële horizon duidelijker zichtbaar maken
	- Headingbug vastmaken aan de heading zodat deze meebeweegt met de heading