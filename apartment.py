from pylatex import Document, Itemize, Section, Subsection, Tabular, Math, TikZ, Axis, \
	Plot, Figure, Matrix, Alignat, Center, Package
from scipy.optimize import bisect
from sthlm2019 import aps
from personalPreference import *
import math
import numpy as np
from personalData import *

#quite general information
MONTHS_PER_YEAR=12
MIN_PER_HOUR=60

#where's stockholm?
latitude=59.3293 #degrees north
longitude=18.0686  #degrees east

income=netIncome+netBonus
realtorCostPerPrice=0.0224 #svensk fast
increaseGuess=1+np.mean([-0.059,.15,.04,.16,-.086,.16,.1,.21,.1,.13,.086,.152])
sellLossFactor=.5

holidays=7.5 #2019,2020 average
vacation=6 #weeks per year
workDays=(365.25/7-vacation)*5-holidays
workHours=8
timeValue=income*MONTHS_PER_YEAR/(workDays*workHours*MIN_PER_HOUR) #sek/min
lifeValue=timeValue #sek/min for increasing life expectancy (pollution calculations)

walkValue=2 # kr/min, walking to work is not useless, some exercise worth about 2kr/min
commutesPerMonth=25

interest=0.02 #??
inflation=0.02 #per year
ranteAvdrag=.3
ranteAvdragYearlyLimit=1e5

bidStep=1e4

def getAmortizationRatio(price): #yearly ratio
	if price==0: return 0
	loanRatio=1-downPayment/price
	amr=0
	if loanRatio>.5 and loanRatio<.7:
		amr+=.01
	if loanRatio>=.7 and loanRatio<.85:
		amr+=.02
	if loanRatio>=.85:
		print('ERROR: loan would not be permitted')
	if price>4.5*grossIncome*MONTHS_PER_YEAR:
		amr+=.01
	return amr

def getInterest(price):
	return .02

def getAreaValue(m2):
	j=1
	val=0
	while m2s[j]<m2:
		val+=m2ValPerm2[j-1]*(m2s[j]-m2s[j-1])
		j+=1
	return val+(m2-m2s[j-1])*m2ValPerm2[j-1]


def analyze(ap,price=-1):
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

	if price==-1:
		price=increaseGuess*ap['startPrice']
	# properties['winterSun']=
	# properties['summerSun']=
	properties['loan']=price-downPayment
	properties['amortization']=getAmortizationRatio(price)
	properties['interest']=getInterest(price)
	properties['monthlyCost']=properties['loan']*(properties['interest']*(1-ranteAvdrag)+properties['amortization'])/12

	effects['interest']=-price*interest*(1-ranteAvdrag)/12
	effects['fee']=-ap['fee']

	if 'booliEstimate' in ap:
		marketPrice=ap['booliEstimate']
	else:
		marketPrice=ap['area']*m2Price[ap['location']]

	effects['selling loss']=-sellLossFactor*(realtorCostPerPrice*price+price-marketPrice)/expectedOwnershipTime/MONTHS_PER_YEAR
	
	effectiveCommuteTime=ap['commuteTime']+ap['commutePeriod']/2

	effects['commute']=-(effectiveCommuteTime*timeValue-ap['commuteWalkTime']*walkValue)*2*workDays/MONTHS_PER_YEAR
	
	if ap['floor']<len(floorLoss):
		effects['floor']=-floorLoss[ap['floor']]
	# effectivePrice=monthlyPrice + tripCommuteCost*2*commutesPerMonth
	
	effects['area']=getAreaValue(ap['area'])

	if 'cons' in ap:
		for c in ap['cons']:
			effects[c]=-conValues[c]
	if 'pros' in ap:
		for p in ap['pros']:
			effects[p]=proValues[p]
	for f in ap['features']:
		effects[f]=positiveFeatures[f]*ap['features'][f]
	
	return properties,effects

def solveForPrice(ap,goal):
	fun=lambda p:sum(analyze(ap,price=p)[1].values())-goal
	if not fun(0)*fun(ap['startPrice']*1.5)<0:
		return 0
	return bisect(fun,0,ap['startPrice']*1.5)

def display(ap,doc):
	properties,effects=analyze(ap)
	with doc.create(Subsection(ap['name'])):
		doc.append('Definition:')
		with doc.create(Itemize(options='noitemsep')) as itemize:
			if 'url' in ap:
				itemize.add_item('url: {}'.format(ap['url']))
			itemize.add_item('floor: {}'.format(ap['floor']))
			itemize.add_item('starting price: {:.2f} Mkr'.format(ap['startPrice']/1e6))
			if 'booliEstimate' in ap:
				itemize.add_item('Booli estimated price: {:.2f} Mkr'.format(ap['booliEstimate']/1e6))
			itemize.add_item('fee: {:.0f} kr/month'.format(ap['fee']))
			ma=Math(inline=True, escape=False)
			ma.append('\\text{{area: }} {:.0f}\\,\\mathrm{{m}}^2'.format(ap['area']))
			itemize.add_item(ma)
			itemize.add_item('commute time: {:.0f} min of which {:.0f} min is walking. Frequency every {:.0f} min.'.format(ap['commuteTime'],ap['commuteWalkTime'],ap['commutePeriod']))

		doc.append('Results:')
		with doc.create(Itemize(options='noitemsep')) as itemize:
			itemize.add_item('interest: {:.1%}'.format(properties['interest']))
			itemize.add_item('amortization: {:.1%}'.format(properties['amortization']))
			itemize.add_item('monthly cost: {a:.0f} kr/month (incl. amortization)'.format(a=properties['monthlyCost']))
		# print('m2 price: {p:.0f}% of local market value'.format(p=100*ap['price']/(ap['area']*m2Price[ap['location']])))
		# print('Effective commute time: ',effectiveCommuteTime,' min')
		# print('Monthly apartment bill:',monthlyPrice)
		doc.append('Value breakdown:\n')
		with doc.create(Center()) as centered:
			with centered.create(Tabular('l|r')) as table:
				tot=0
				for e in effects:
					table.add_row((e, '{p}{v:.0f} kr/month'.format(k=e,v=effects[e],p='+' if effects[e]>0 else '')))
					tot+=effects[e]
				table.add_hline()	
				table.add_row(('TOTAL', '{t:.0f} kr/month'.format(t=tot)))

	# print('Effective price: {p:.0f} sek/month'.format(p=effectivePrice))

def main():
	geometry_options = {"tmargin": "2cm", "lmargin": "2cm"}
	doc = Document(geometry_options=geometry_options)
	doc.packages.append(Package('enumitem'))
	doc.packages.append(Package('hyperref'))

	with doc.create(Section('Personal preferences')):
		doc.append('Positive features:\n')
		with doc.create(Center()) as centered:
			with centered.create(Tabular('l|r')) as table:
				table.add_hline()	
				for p in proValues:
					table.add_row((p, '+{v:.0f} kr/month'.format(v=proValues[p])))
				table.add_hline()
		doc.append('Negative features:\n')
		with doc.create(Center()) as centered:
			with centered.create(Tabular('l|r')) as table:
				table.add_hline()	
				for p in conValues:
					table.add_row((p, '{v:.0f} kr/month'.format(v=-conValues[p])))
				table.add_hline()

	doc.append('Intermediate results:\n')
	with doc.create(Itemize(options='noitemsep')) as itemize:
		itemize.add_item('Time value: {v:.1f} kr/min'.format(v=timeValue))

	doc.append('Estimated size for different regions (only considering interest and average prices):\n')
	with doc.create(Center()) as centered:
		with centered.create(Tabular('l|r')) as table:
			table.add_hline()	
			for k in m2Price:
				for i in range(len(m2s)-1):
					if m2ValPerm2[i]<m2Price[k]*interest/MONTHS_PER_YEAR:
						ma=Math(inline=True, escape=False)
						ma.append('{a}-{b}\\,\\mathrm{{m}}^2'.format(a=m2s[i],b=m2s[i+1]))
						table.add_row((k, ma))
						table.add_hline()
						break

	with doc.create(Section('Apartments')):
		for a in aps:
			display(a,doc)
	
	
	with doc.create(Section('Summary')):
		doc.append('Effective values (kr/month):')

		saps=[a for a in aps if 'soldFor' in a]
		asaps=[analyze(a,price=a['soldFor']) for a in saps]
		aaps=[analyze(a) for a in aps]
		scats=set()
		stots=[]
		for a in asaps:
			tot=0
			for e in a[1]:
				scats.add(e)
				tot+=a[1][e]
			stots.append(tot)

		with doc.create(Center()) as centered:
			with centered.create(Tabular('l'+'|r'*(len(saps)))) as table:
				table.add_row(['SCORE']+[a['name'][:6]+'..' for a in saps])
				table.add_hline()
				for c in scats:
					table.add_row([c]+['{:.0f}'.format(a[1][c]) if c in a[1] else '' for a in asaps])
				table.add_hline()
				table.add_row(['TOTAL']+['{:.0f}'.format(t) for t in stots])
				table.add_empty_row()
				table.add_row(['PRICES']+['' for a in saps])
				table.add_row(['Ad price']+['{:.0f}'.format(ap['startPrice']) for ap in saps])
				table.add_row(['Sold price']+['{:.0f}'.format(ap['soldFor']) for ap in saps])
				table.add_row(['Booli']+['{:.0f}'.format(ap['booliEstimate']) if 'booliEstimate' in ap else '-' for ap in saps])
				table.add_row(['My top bid']+['{:.0f}'.format(solveForPrice(ap,goalValue)//bidStep*bidStep) for ap in saps])
		paps=[a for a in aps if 'soldFor' not in a]
		aaps=[analyze(a) for a in paps]
		cats=set()
		tots=[]
		for a in aaps:
			tot=0
			for e in a[1]:
				cats.add(e)
				tot+=a[1][e]
			tots.append(tot)
		with doc.create(Center()) as centered:
			with centered.create(Tabular('l'+'|r'*(len(paps)))) as table:
				table.add_row(['SCORE (est.)']+[a['name'][:6]+'..' for a in paps])
				table.add_hline()
				for c in cats:
					table.add_row([c]+['{:.0f}'.format(a[1][c]) if c in a[1] else '' for a in aaps])
				table.add_hline()
				table.add_row(['TOTAL']+['{:.0f}'.format(t) for t in tots])
				table.add_row(['accept est.']+['{:.0f}'.format(sum(analyze(a,price=a['acceptPrice'])[1].values())) if 'acceptPrice' in a else '-' for a in paps])
				table.add_empty_row()
				table.add_row(['PRICES']+['' for a in paps])
				table.add_row(['Ad price']+['{:.0f}'.format(ap['startPrice']) for ap in paps])
				table.add_row(['Booli']+['{:.0f}'.format(ap['booliEstimate']) if 'booliEstimate' in ap else '-' for ap in paps])
				table.add_row(['Accept']+['{:.0f}'.format(ap['acceptPrice']) if 'acceptPrice' in ap else '-' for ap in paps])
				table.add_row(['Top bid']+['{:.0f}'.format(ap['bids'][-1]) if 'bids' in ap else '-' for ap in paps])
				table.add_row(['My top bid']+['{:.0f}'.format(solveForPrice(ap,goalValue)//bidStep*bidStep) for ap in paps])
				table.add_row(['Action']+[(('BID' if sum(analyze(ap,price=ap['bids'][-1])[1].values())>goalValue else 'STOP') if 'bids' in ap else '') for ap in paps])
				
								# for a in aps:
				# 	properties,effects=analyze(a)
				# 	table.add_row((a['name'],'{:.0f} kr/month'.format(sum(effects.values()))))
				

	doc.generate_pdf('apartment', clean_tex=False)

main()