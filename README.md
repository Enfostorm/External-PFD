# External-PFD
Github-repository voor bachelorproject PFD voor een UAV/flight sim
Peter van den Thillart

Serial link datavolgorde:
main --> PFD
pitch;roll;slip;heading;altitude;speed;headingRate;vSpeed;hdgBug;altBug;spdBug;vsiBug;groundTrack;altUnit;spdUnit;\n

	pitch:		[°]
	roll:		[°]
	slip:		Een waarde van 0 = geen slip, waarde van -1 = indicator beweegt zijn eigen breedte naar linkt, +1 beweegt naar rechts. Waarden boven 1 en onder -1 zijn ook toegestaan
	speed:		
	headingRate:	Rate of turn in °/s
	vSpeed:		vertical speed
	hdgBug:		Effectieve waarde van de heading-bug van de autopiloot. (= de positie van de bug op het kompas, ≠ de waarde van de bug in de knop ingesteld met de encoder)
	altBug:		Effectieve waarde van de altitude-bug van de autopiloot
	spdBug:		Effectieve waarde van de speed-bug van de autopiloot
	vsiBug:		Effectieve waarde van de vertical-speedbug van de autopiloot
	groundTrack:	Hoek van de groundtrack die op het kompas weergegeven wordt. Wordt doorgegeven in ° t.o.v. het noorden (0°).
	altUnit:		Eenheid van de hoogte in string-vorm, afgekort (bv.: 'ft' of 'm', zonder aanhalingstekens). Wordt weergegeven in de bugknoppen.
	spdUnit:		Eenheid van de snelheid in string-vorm, afgekort (bv.: 'kts' of 'km/h', zonder aanhalingstekens). Wordt weergegeven in de bugknoppen.

Aantal beduidende cijfers maakt niet veel uit, buiten de limitaties van de seriële link (aan een baud van 115200 en 60 waarden per seconde komt dit uit op een theoretisch maximum van 234 karakters per lijn.)

PFD --> main
headingBug;altBug;speedBug;vsiBug;\n

Als de parameter self.simulink_fix True is, dan wordt de string aangevuld met '000...0; totdat er 50 karakters per lijn zijn, zodat simulink deze in kan lezen.
Indien deze False is, dan zal de string korter met een variabele lijnlengte zijn.

