import numpy as np
import os
import json
from tc_python import * 

with TCPython() as start:
	#el_list = ["V","Cr","Ti","W","Ta","Zr","C","N"]
	#el_list = ["V","Cr","Ti","Si"]
	el_list = ["V","Cr","Ti"]
	x_cr = 0.1
	x_ti = 0.1
	#x_w = 0.01
	#x_ta = 0.006
	#x_zr = 0.005
	#x_c = 0.0001
	#x_n = 0.0001
	#comp_list = [1-x_cr-x_ti-x_w-x_ta-x_zr-x_c-x_n,x_cr,x_ti,x_w,x_ta,x_zr,x_c,x_n]
	#comp_list = [1-x_cr-x_ti-x_si,x_cr,x_ti,x_si]
	comp_list = [1-x_cr-x_ti,x_cr,x_ti]
	calculation = (
		start
			.set_cache_folder(os.path.basename(__file__) + "_cache")
			.select_database_and_elements("TCHEA7",el_list)
			.without_default_phases()
			.select_phase("BCC_B2#1")
			.select_phase("C15_Laves#1")
			.select_phase("BCC_B2#2")
			.select_phase("HCP_A3#1")
			.get_system()
			.with_single_equilibrium_calculation()
			.set_condition("T",873.15)
			.set_condition("X({})".format(el_list[1]),comp_list[1])
			.set_condition("X({})".format(el_list[2]),comp_list[2])
			#.set_condition("X({})".format(el_list[3]),comp_list[3])
			#.set_condition("X({})".format(el_list[4]),comp_list[4])
			#.set_condition("X({})".format(el_list[5]),comp_list[5])
			#.set_condition("X({})".format(el_list[6]),comp_list[6])
			#.set_condition("X({})".format(el_list[7]),comp_list[7])
			.disable_global_minimization()
			#.with_options()
			#.set_max_no_of_iterations(1000)
	)

	# load in the data from json 
	good_compositions = json.load(open('./ternary_plot_data.json','r'))
	
	# create list_of_x_cr
	print("Creating list of compositions")
	compositions = []
	for d in good_compositions:
		#if d['color'] != 'yellow' or d['color'] != 'red':
		comp = {}
		comp['Cr'] = (d['Cr'])
		comp['Ti'] = (d['Ti'])
		compositions.append(comp)
	
	list_of_phases = []
	list_of_conditions = []
	

	#results_dict = {}
	results = []
	i = 0
	for comp in compositions:
		x_Cr = comp['Cr']
		x_Ti = comp['Ti']
		#print("Calculating for Cr = {} and Ti = {}".format(x_Cr,x_Ti))
		try:
			calc_result = (calculation
					.set_condition("X({})".format(el_list[1]),x_Cr)
					.set_condition("X({})".format(el_list[2]),x_Ti)
					#.with_options()
					#.set_max_no_of_iterations(1000)
					.calculate()
					)
					#.set_condition("X({})".format(el_list[3]),x_W)
					#.set_condition("X({})".format(el_list[4]),x_Ta)
					#.set_condition("X({})".format(el_list[5]),x_Zr)
			bal = 1 - x_Cr - x_Ti
			comp = {el_list[0] : bal , el_list[1] : x_Cr, el_list[2] : x_Ti}
			phases_present = calc_result.get_stable_phases()
			#print(phases_present)
			phases_dict = {}
			for phase in phases_present:
				phase_amount = calc_result.get_value_of(ThermodynamicQuantity.mole_fraction_of_a_phase(phase))
				#print("Mole Fraction of ",phase, " = ", phase_amount)
				#temp_phases.append("X_{0}={1}".format(phase,phase_amount))
				phases_dict[phase]=phase_amount
			#results_dict["{}".format(i)] = {'Composition' : comp , 'Phases' : phases_dict}
			results.append({'Composition' : comp , 'Phases' : phases_dict})
			if i % 1000 == 0:
				print(f'On Composition {i} out of {len(compositions)}')
			
			i += 1
		except UnrecoverableCalculationException as e:
			print('Could not calculate. Continuing with next...')

	
json_object = json.dumps(results)
with open("fixed_all_results.json", "w") as outfile:
	outfile.write(json_object)
