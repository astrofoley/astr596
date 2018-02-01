import composite
from astropy.table import Table
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import argparse
import spectral_analysis as sa


def make_colorbar(composites):
	params = []
	# for comp in composites:
	# 	params.append(np.average(comp.dm15_array[comp.x1:comp.x2]))
	# norm = matplotlib.colors.Normalize(vmin=np.min(params),vmax=np.max(params))
	norm = matplotlib.colors.Normalize(vmin=1.,vmax=len(composites))
	c_m = matplotlib.cm.coolwarm
	# c_m = matplotlib.cm.winter_r
	s_m = matplotlib.cm.ScalarMappable(cmap=c_m, norm=norm)
	s_m.set_array([])

	return s_m

def scaled_plot(composites):

	font = {'family' : 'serif',
        'color'  : 'black',
        'weight' : 'bold',
        'size'   : 10,
        }

	fig = plt.figure(num = 1, dpi = 100, figsize = [10,10], facecolor = 'w')
	s_m = make_colorbar(composites)

	composites, scales = composite.optimize_scales(composites, composites[0], True)

	for comp in composites:
		phase = np.average(comp.phase_array[comp.x1:comp.x2])

		plt.ylabel('Relative Flux', fontdict = font)
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.flux[comp.x1:comp.x2], color = s_m.to_rgba(phase))
		if len(comp.low_conf) > 0 and len(comp.up_conf) > 0:
			plt.fill_between(comp.wavelength[comp.x1:comp.x2], comp.low_conf[comp.x1:comp.x2], 
				             comp.up_conf[comp.x1:comp.x2], color = s_m.to_rgba(phase), alpha = 0.5)

	plt.xlabel('Rest Wavelength [$\AA$]', fontdict = font)
	cb = plt.colorbar(s_m, ax = fig.axes)
	cb.set_label('Phase', fontdict = font)
	plt.show()

def set_min_num_spec(composites, num):

	for comp in composites:
		comp.spec_bin = np.array(comp.spec_bin)
		valid_range = np.where(comp.spec_bin >= num)[0]
		comp.x1, comp.x2 = valid_range[0], valid_range[-1]


def comparison_plot(composites):

	# plt.style.use('ggplot')
	colors = [color['color'] for color in list(plt.rcParams['axes.prop_cycle'])]
	h = [3,1,1,1,1,1,1]
	font = {'family' : 'serif',
        'color'  : 'black',
        'weight' : 'bold',
        'size'   : 10,
        }

	gs = gridspec.GridSpec(7, 1, height_ratios=h, hspace = .001)
	fig = plt.figure(num = 1, dpi = 100, figsize = [10,10])
	s_m = make_colorbar(composites)
	lw = 3

	composites, scales = composite.optimize_scales(composites, composites[0], True)

	i = 0
	k = 1
	for comp in composites:
		# param = np.average(comp.dm15_array[comp.x1:comp.x2])
		param = k

		rel_flux = plt.subplot(gs[0])
		plt.setp(rel_flux.get_xticklabels(), visible=False)
		plt.ylabel('Relative Flux', fontdict = font)
		rel_flux.axes.get_yaxis().set_ticks([])
		# plt.plot(comp.wavelength[comp.x1:comp.x2], comp.flux[comp.x1:comp.x2], color = s_m.to_rgba(param))
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.flux[comp.x1:comp.x2], linewidth = lw, color = s_m.to_rgba(param))
		if len(comp.low_conf) > 0 and len(comp.up_conf) > 0:
			plt.fill_between(comp.wavelength[comp.x1:comp.x2], comp.low_conf[comp.x1:comp.x2], 
				             comp.up_conf[comp.x1:comp.x2], color = s_m.to_rgba(param), alpha = 0.5)
			# plt.fill_between(comp.wavelength[comp.x1:comp.x2], comp.low_conf[comp.x1:comp.x2], 
			# 	             comp.up_conf[comp.x1:comp.x2], color = colors[i%len(colors)], alpha = 0.5)

		var = plt.subplot(gs[1], sharex = rel_flux)
		plt.setp(var.get_xticklabels(), visible=False)
		plt.ylabel('Variance', fontdict = font)
		# plt.plot(comp.wavelength[comp.x1:comp.x2], comp.ivar[comp.x1:comp.x2], color = s_m.to_rgba(param))
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.ivar[comp.x1:comp.x2], linewidth = lw, color = s_m.to_rgba(param))

		res = plt.subplot(gs[2], sharex = rel_flux)
		plt.setp(res.get_xticklabels(), visible=False)
		plt.ylabel('Residuals', fontdict = font)
		# plt.plot(comp.wavelength[comp.x1:comp.x2], comp.flux[comp.x1:comp.x2] - composites[0].flux[comp.x1:comp.x2], color = s_m.to_rgba(param))
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.flux[comp.x1:comp.x2] - composites[0].flux[comp.x1:comp.x2], linewidth = lw, color = s_m.to_rgba(param))
		if len(comp.low_conf) > 0 and len(comp.up_conf) > 0:
			low_resid = comp.low_conf[comp.x1:comp.x2] - composites[0].flux[comp.x1:comp.x2]
			up_resid = comp.up_conf[comp.x1:comp.x2] - composites[0].flux[comp.x1:comp.x2]
			plt.fill_between(comp.wavelength[comp.x1:comp.x2], low_resid, up_resid, color = s_m.to_rgba(param), alpha = 0.5)
			# plt.fill_between(comp.wavelength[comp.x1:comp.x2], low_resid, up_resid, color = colors[i%len(colors)], alpha = 0.5)

		spec = plt.subplot(gs[3], sharex = rel_flux)
		plt.setp(spec.get_xticklabels(), visible=False)
		plt.ylabel('Spectra/Bin', fontdict = font)
		# plt.plot(comp.wavelength[comp.x1:comp.x2], comp.spec_bin[comp.x1:comp.x2], color = s_m.to_rgba(param))
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.spec_bin[comp.x1:comp.x2], linewidth = lw, color = s_m.to_rgba(param))

		phase = plt.subplot(gs[4], sharex = rel_flux)
		plt.setp(phase.get_xticklabels(), visible=False)
		plt.ylabel('Phase [d]', fontdict = font)
		# plt.plot(comp.wavelength[comp.x1:comp.x2], comp.phase_array[comp.x1:comp.x2], color = s_m.to_rgba(param))
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.phase_array[comp.x1:comp.x2], linewidth = lw, color = s_m.to_rgba(param))

		delt = plt.subplot(gs[5], sharex = rel_flux)
		plt.setp(delt.get_xticklabels(), visible=False)
		plt.ylabel('$\Delta$m$_{15}$', fontdict = font)
		# plt.plot(comp.wavelength[comp.x1:comp.x2], comp.dm15[comp.x1:comp.x2], color = s_m.to_rgba(param))
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.dm15[comp.x1:comp.x2], linewidth = lw, color = s_m.to_rgba(param))

		plt.subplot(gs[6], sharex = rel_flux)
		plt.ylabel('Redshift', fontdict = font)
		# plt.plot(comp.wavelength[comp.x1:comp.x2], comp.red_array[comp.x1:comp.x2], color = s_m.to_rgba(param))
		plt.plot(comp.wavelength[comp.x1:comp.x2], comp.red_array[comp.x1:comp.x2], linewidth = lw, color = s_m.to_rgba(param))

		i+=1
		k+=1

	plt.xlabel('Rest Wavelength [$\AA$]', fontdict = font)
	# cb = plt.colorbar(s_m, ax = fig.axes)
	# cb.set_label('Phase', fontdict = font)
	# for ax in fig.axes:
	# 	ax.set_axis_bgcolor('white')

	plt.show()

def stacked_plot(composites):
	fig, ax = plt.subplots(1,1)
	fig.set_size_inches(20, 12., forward = True)
	ax.get_yaxis().set_ticks([])
	composites, scales = composite.optimize_scales(composites, composites[0], True)

	i = 0
	for comp in composites:
		dm15 = np.average(comp.dm15[comp.x1:comp.x2])
		comp.flux = 1.e15*comp.flux 
		ax.plot(comp.wavelength[comp.x1:comp.x2], comp.flux[comp.x1:comp.x2] - 2.*i, color = '#3F5D7D', linewidth = 5)
		plt.text(9700, comp.flux[comp.x2] - 2*i + 1, dm15)
		i+=1

	plt.ylabel('Relative Flux + const.')
	plt.xlabel('Wavelength (A)')
	plt.show()

def normalize_comps(composites):
	for comp in composites:
		norm = 1./np.amax(comp.flux[comp.x1:comp.x2])
		comp.flux = norm*comp.flux
		comp.low_conf = norm*comp.low_conf
		comp.up_conf = norm*comp.up_conf
		comp.ivar *= (norm)**2
	return composites

def normalize_comp(comp):
	norm = 1./np.amax(comp.flux[comp.x1:comp.x2])
	comp.flux = norm*comp.flux
	comp.low_conf = norm*comp.low_conf	
	comp.up_conf = norm*comp.up_conf
	comp.ivar *= (norm)**2
	return comp, norm

def main(num_queries, query_strings, boot='nb'):
	# num_queries = int(sys.argv[1])
	# query_strings = sys.argv[2:]

	composites = []
	sn_arrays = []
	boot_sn_arrays = []
	store_boots = True
	for n in range(num_queries):
		comp, arr, boots = composite.main(query_strings[n],boot=boot)
		if store_boots:
			boot_sn_arrays.append(boots)
		composites.append(comp)
		sn_arrays.append(arr)

	# composite.optimize_scales(composites, composites[0], True)
	# composites = normalize_comps(composites)

	return composites, sn_arrays, boot_sn_arrays


def make_animation(composites):
	fig, ax = plt.subplots()
	plt.xlim([3000,10000])
	plt.ylim([0.,5.e-15])
	s_m = make_colorbar(composites)

	phase = np.average(composites[0].phase_array[composites[0].x1:composites[0].x2])
	line, = ax.plot(composites[0].wavelength[composites[0].x1:composites[0].x2], 
					composites[0].flux[composites[0].x1:composites[0].x2], color = s_m.to_rgba(phase))

	def animate(i):
		if i == 0:
			ax.cla()
		phase = np.average(composites[i].phase_array[composites[i].x1:composites[i].x2])
		ax.plot(composites[i].wavelength[composites[i].x1:composites[i].x2], 
					composites[i].flux[composites[i].x1:composites[i].x2], color = s_m.to_rgba(phase))
		plt.xlim([3000,10000])
		plt.ylim([0.,5.e-15])
		# line.set_xdata(composites[i].wavelength[composites[i].x1:composites[i].x2])
		# line.set_ydata(composites[i].flux[composites[i].x1:composites[i].x2])  # update the data
		return line,

	animation.FuncAnimation(fig, animate, np.arange(0, len(composites)), repeat = True)
	plt.show()

def plot_comp_and_all_spectra(comp, SN_Array):
	# norm = 1./np.amax(comp.flux)
	# comp.flux = comp.flux*norm
	# for SN in SN_Array:
	# 	SN.flux = SN.flux*norm
	# composite.optimize_scales(SN_Array,comp, True)
	plt.rc('font', family='serif')
	fig, ax = plt.subplots(1,1)
	fig.set_size_inches(10, 8, forward = True)
	plt.minorticks_on()
	plt.xticks(fontsize = 20)
	ax.xaxis.set_ticks(np.arange(np.round(comp.wavelength[comp.x1:comp.x2][0],-3), np.round(comp.wavelength[comp.x1:comp.x2][-1],-3),1000))
	plt.yticks(fontsize = 20)
	plt.tick_params(
	    which='major', 
	    bottom='on', 
	    top='on',
	    left='on',
	    right='on',
	    length=10)
	plt.tick_params(
		which='minor', 
		bottom='on', 
		top='on',
		left='on',
		right='on',
		length=5)
	for i in range(len(SN_Array)):
	    # plt.plot(SN_Array[i].wavelength[SN_Array[i].x1:SN_Array[i].x2], SN_Array[i].flux[SN_Array[i].x1:SN_Array[i].x2], color = '#7570b3', alpha = .5)
	    plt.plot(SN_Array[i].wavelength[SN_Array[i].x1:SN_Array[i].x2], SN_Array[i].flux[SN_Array[i].x1:SN_Array[i].x2])
	plt.plot(comp.wavelength[comp.x1:comp.x2], comp.flux[comp.x1:comp.x2], 'k', linewidth = 6)
	plt.ylabel('Relative Flux', fontsize = 30)
	plt.xlabel('Wavelength ' + "($\mathrm{\AA}$)", fontsize = 30)
	# "SELECT * from Supernovae inner join Photometry ON Supernovae.SN = Photometry.SN where phase >= -3 and phase <= 3 and morphology >= 9"
	# plt.savefig('../../Paper_Drafts/scaled.png', dpi = 300, bbox_inches = 'tight')
	plt.show()


def save_comps_to_files(composites):
	for SN in composites:
		phase = np.round(np.average(SN.phase_array[SN.x1:SN.x2]), 1)
		vel = np.round(np.average(SN.vel[SN.x1:SN.x2]), 1)
		print phase, vel

	#save to file
	for SN in composites:
		phase = np.round(np.average(SN.phase_array[SN.x1:SN.x2]), 1)
		vel = np.round(np.average(SN.vel[SN.x1:SN.x2]), 1)

		if phase >= 0.:
			sign = 'p'
		else:
			sign = 'm'
		abs_phase = np.absolute(phase)
		phase_str = str(abs_phase)

		abs_vel = np.absolute(vel)
		vel_str = str(abs_vel)

		with open('../../' + sign + phase_str + 'days' + '.flm', 'w') as file:
			wave = np.array(SN.wavelength[SN.x1:SN.x2])
			flux = np.array(SN.flux[SN.x1:SN.x2])
			data = np.array([wave,flux])
			data = data.T
			np.savetxt(file, data)

		plt.plot(SN.wavelength[SN.x1:SN.x2], SN.flux[SN.x1:SN.x2])
	plt.show()

if __name__ == "__main__":
	composites = []
	SN_Arrays = []
	boot_sn_arrays = []
	store_boots = True

	boot = sys.argv[1]
	query_strings = sys.argv[2:]

	num_queries = len(query_strings)

	for n in range(num_queries):
		c, sn_arr, boots = composite.main(query_strings[n], boot)
		composites.append(c)
		SN_Arrays.append(sn_arr)
		if store_boots:
			boot_sn_arrays.append(boots)
	# composite.optimize_scales(composites, composites[0], True)

	
	plot_comp_and_all_spectra(composites[0], SN_Arrays[0])
	set_min_num_spec(composites, 5)
	normalize_comps(composites)
	# for comp in composites:
	# 	sa.measure_si_velocity(comp)
	
	#plotting rutines to visualize composites
	# set_min_num_spec(composites, 5)
	comparison_plot(composites)
	# # scaled_plot(composites)
	# stacked_plot(composites)

	# save_comps_to_files(composites)
	
		