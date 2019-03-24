from sthlm2019 import aps

latitude=59.3293 #degrees north
longitude=18.0686  #degrees east

MONTHS_PER_YEAR=12
MIN_PER_HOUR=60

holidays=7.5 #2019,2020 average
vacation=6 #weeks per year
workDays=(365.25/7-vacation)*5-holidays
income=36962 #after tax, with expected bonus
workHours=8
timeValue=income*MONTHS_PER_YEAR/(workDays*workHours*MIN_PER_HOUR) #sek/min
lifeValue=timeValue #sek/min for increasing life expectancy (pollution calculations)

walkValue=2 # kr/min, walking to work is not useless, some exercise worth about 2kr/min
commutesPerMonth=25

interest=0.017 #??
inflation=0.02 #per year
ranteAvdrag=.3
expectedOwnershipTime=5

planValue=600
locationValue=800. #not for commmuting, but for e.g. eating out
natureValue=300. #can i go jogging in a forrest?
polutionValue=300. #can i go jogging in a forrest?
noiseValue=400

#commute is from apt to raysearch leaving at 8:00

conValues={'share':3000}

m2s=    [ 0,  10,  20, 30,40,50,60,70,100,1000]
m2ValPerm2=[500,400,350,350,100,60,40,10,-10]

def getAreaValue(m2):
	j=1
	val=0
	while m2s[j]<m2:
		val+=m2ValPerm2[j-1]*(m2s[j]-m2s[j-1])
		j+=1
	return val+(m2-m2s[j-1])*m2ValPerm2[j-1]

proValues={'balkonyNorth':100,
		  'balkonyEast':100,
		  'balkonySouth':200,
		  'balkonyWest':300,}

m2Price={'Södermalm':81295,
		 'Kungsholmen':84439,
		 'Enskede/Skarpnäck':55314,
		 'Östermalm':90688,
		 'Linköping':30827,
		 'Vasastan/Norrmalm':92612,
		 'Manhattan':179746
		 } #market price per area


def analyze(ap):
	#To buy an apartment i want to pay as little as possible per month. Good things about the apartment offset this cost
	#so i can pay more if it is better. I assign a value to everything and calculate an effective price per month.

	#The apartment has a certain market price which equals the expectation value (with added value appreciation) of what I might sell it
	#for in the future. It could be that a certain apartment can be bought below or above what i expect the market price to be. That will
	#be a win/loss once I sell the apartment. So instead of estimating what the apartment is worth to me
	#(which is way above market price, option is sleeping on the street :P) I should also estimate what the market value is and the difference
	#is something I earn/pay and the interest of it has to be added to the effective price.

	#If all is accounted for I should just pick the one with lowest effective price I can find.
	
	properties=dict() #various properties
	effects=dict() #all negative effects measured in sek/month

	# properties['winterSun']=
	# properties['summerSun']=

	effects['interest']=ap['price']*interest*(1-ranteAvdrag)/12
	effects['fee']=ap['fee']

	if 'booliEstimate' in ap:
		marketPrice=ap['booliEstimate']
	else:
		marketPrice=ap['area']*m2Price[ap['location']]

	effects['selling loss']=(ap['price']-marketPrice)/expectedOwnershipTime/MONTHS_PER_YEAR
	
	effectiveCommuteTime=ap['commuteTime']+ap['commutePeriod']/2

	effects['commute']=(effectiveCommuteTime*timeValue-ap['commuteWalkTime']*walkValue)

	# effectivePrice=monthlyPrice + tripCommuteCost*2*commutesPerMonth
	
	# if 'cons' in ap:
	# 	for c in ap['cons']:
	# 		effectivePrice+=conValues[c]

	# if 'pros' in ap:
	# 	for p in ap['pros']:
	# 		effectivePrice-=proValues[c]

	return effects,properties

def display(ap):
	effects,properties=analyze(ap)

	print('Apartment:',ap['name'])
	# print('m2 price: {p:.0f}% of local market value'.format(p=100*ap['price']/(ap['area']*m2Price[ap['location']])))
	# print('Effective commute time: ',effectiveCommuteTime,' min')
	# print('Monthly apartment bill:',monthlyPrice)

	tot=0
	for e in effects:
		print(' * {k}: {v:.0f} kr'.format(k=e,v=effects[e]))
		tot+=effects[e]
	print('=> TOTAL: {t:.0f} kr'.format(t=tot))

	# print('Effective price: {p:.0f} sek/month'.format(p=effectivePrice))

def main():
	print('Time value: {v:.1f} kr/min'.format(v=timeValue))

	print('Estimated size for different regions (only considering interest and average prices):')
	for k in m2Price:
		for i in range(len(m2s)-1):
			if m2ValPerm2[i]<m2Price[k]*interest/MONTHS_PER_YEAR:
				print('\t{k}: {a}-{b} m2'.format(k=k,a=m2s[i],b=m2s[i+1]))
				break

	for a in aps:
		print()
		display(a)


main()