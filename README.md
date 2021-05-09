# External-PFD
Github-repository voor bachelorproject PFD voor een UAV/flight sim
Peter van den Thillart

Serial link datavolgorde:
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
	groundTrack:	Hoek van de groundtrack die op het kompas weergegeven wordt.
	altUnit:		Eenheid van de hoogte in string-vorm, afgekort (bv.: 'ft' of 'm', zonder aanhalingstekens). Wordt weergegeven in de bugknoppen.
	spdUnit:		Eenheid van de snelheid in string-vorm, afgekort (bv.: 'kts' of 'km/h', zonder aanhalingstekens). Wordt weergegeven in de bugknoppen.
