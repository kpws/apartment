

expectedOwnershipTime=5 #years
goalValue=10000

#commute is from apt to raysearch leaving at 8:00

conValues={'share':4000,'crappyShower':800}
proValues={'sauna':200,
		  'balconyNorth':75,
		  'balconyEast':150,
		  'balconySouth':200,
		  'balconyWest':300}

m2s=    [ 0,  10,  20, 30, 40,50,60,70,100,1000]
m2ValPerm2=[500,400,350,300,200,100,40,10,-10]

floorLoss=[2000,600,400,300,200,100,50,0]

m2Price={'Södermalm':81295,
		 'Kungsholmen':84439,
		 'Enskede/Skarpnäck':55314,
		 'Östermalm':90688,
		 'Linköping':30827,
		 'Vasastan/Norrmalm':92612,
		 'Manhattan':179746
		 } #market price per area

positiveFeatures={
'location':1200, #nice location (disregarding commute)
'quality':800, #build quality
'plan':900,  #smart interior plan that makes it practical
'estetics':400,  #beatiful interior, makes it pleasant inside
'building':200
}  #beautiful building, makes it pleasant to the eye when coming home every day