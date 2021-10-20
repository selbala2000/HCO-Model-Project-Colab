from neuron import h
import matplotlib.pyplot as plt

class HCOcell(object):
    def __init__(self):
        self.create_sections()
        self.define_geometry()
        self.define_biophysics()
        self.setup_record()
    
    def create_sections(self):
        """Create the sections of the cell."""
        self.soma = h.Section(name='soma',cell=self)
    
    def define_geometry(self):
        """Set the geometry of the cell."""
        self.soma.nseg = 1 # create only one segment in the soma
        # gives area of .314e-3 cm^2
        self.soma.L = 1000 # (microns)
        self.soma.diam = 9.99593 # (microns)
    
    def define_biophysics(self):
        """Initialize the membrane properties of the cell."""
        self.soma.cm = 1 # Membrane capacitance (microF/cm2)
        
        self.soma.insert('leak')
        self.soma.eleak = -50 # (mV)
        
        self.soma.insert('na')
        self.soma.ena = 50
        
        self.soma.insert('kdr')
        self.soma.ek = -80
        
        self.soma.insert('capool')
        self.soma.cao = 3 # (mM)
        self.soma.cai = 50e-6 # (mM)
        
        self.soma.insert('cas')
        self.soma.insert('ka')
        self.soma.insert('kca')
        self.soma.insert('cat')
        self.soma.insert('hyper')
        self.soma.eh = -20
        
        self.default_parameters = {
            'gbar_leak': .03e-3, # (siemens/cm2)
            'gbar_na': .1,
            'gbar_kdr': .1,
            'gbar_ka': .1,
            'gbar_kca': .01,
            'gbar_cas': .001,
            'gbar_cat': .005,
            'gbar_hyper': .0001,
            'tauca_capool': self.soma.tauca_capool,
            'fca_capool': self.soma.fca_capool
        }
        self.set_biophysics(**self.default_parameters)
    
    def set_biophysics(self,**attributes):
        """Change the membrane properties of the cell."""
        for param,value in attributes.items():
            if value is not None:
                setattr(self.soma,param,value)
            elif param in self.default_parameters.keys():
                setattr(self.soma,param,self.default_parameters[param])
    
    def get_biophysics(self,**attributes):
        """Get the membrane properties of the cell."""
        for param in attributes.keys():
            attributes[param] = getattr(self.soma,param)
        return attributes
    
    def setup_record(self):
        """Set up the vectors for recording variables."""
        self.t = h.Vector()
        self.t.record(h._ref_t)
        self.vars = ['ileak_leak','ina_na','ik_kdr',
                     'ica_cas','ica_cat','ik_ka','ik_kca',
                     'ih_hyper','v','cai']
        self.clrs = ['k','y','r','orange','brown','pink','g','c']
        self.record = {}
        for v in self.vars:
            vec = h.Vector()
            vec.record(getattr(self.soma(.5),'_ref_'+v))
            self.record[v] = vec
    
    def plot_vars(self,cellid=0,figsize=None):
        """Plot recorded variables."""
        cellname = 'Cell B' if cellid>0 else 'Cell A'
        clr = 'r' if cellid>0 else 'b'
        t = self.t
        fig = plt.figure(figsize=figsize)
        axs = fig.subplots(3,1,sharex=True,gridspec_kw={'hspace':0.1})
        axs[0].set_title(cellname)
        axs[0].plot(t,self.record['v'],clr)
        axs[0].set_ylim(-90,60)
        axs[0].set_ylabel('Membrane Voltage (mV)')
        axs[2].plot(t,self.record['cai'],clr)
        axs[2].set_ylim(0,0.4)
        axs[2].set_ylabel('Calcium Pool (mM)')
        for i,v in enumerate(self.vars[:-2]):
            if getattr(self.soma,'gbar_'+v.split('_')[-1])>0:
                axs[1].plot(t,self.record[v],color=self.clrs[i],label=v)
        axs[1].legend(loc=1)
        axs[1].set_ylabel('Current (nA/cm$^2$)')
        axs[2].set_xlim(t[0],t[-1])
        axs[2].set_xlabel('Time (ms)')
        return fig, axs
    
