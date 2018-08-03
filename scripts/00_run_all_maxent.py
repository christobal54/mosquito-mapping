import ccb
import numpy as np


# set the paths to the input files
base = '/home/cba/src/mosquito-mapping/'
samples_dir = base + 'maxent-inputs/'
layers = base + 'raster/'
bias = base + 'maxent-outputs/'
outdir = base + 'maxent-outputs/'

# set the species to assess
spl = ['Aedes aegypti', 'Aedes albopictus']
sp = ['aedes-aegypti', 'aedes-albopictus']

# set the resolutions to assess
res = [1000, 5000, 10000, 50000, 100000]

# set the sample geography data
geo = ['all', 'cam', 'car', 'sam']

# set the environmental subsets
env = ['clim', 'lcov', 'envs']
climlist = ['temp-max', 'temp-med', 'temp-min']
lcovlist = ['vegetation', 'trees', 'impervious', 'soil']
envslist = climlist + lcovlist

# set the maxent run options
test_pct = 25
nodata = 255

# create an array to store auc values
auc_ae_mn = np.array((len(env), len(geo), len(res)))
auc_aa_mn = np.array((len(env), len(geo), len(res)))
auc_mn_lst = [auc_ae_mn, auc_aa_mn]

# report starting!
ccb.prnt.status('starting maxent runs!')

# then set up a big ol' loop structure to run through all the different maxent permutations
for s in range(len(sp)):
    for r in range(len(res)-1, -1, -1):
        for g in range(len(geo)):
            for e in range(len(env)):
                
                # create a fresh maxent object
                mx = ccb.maxent()
                
                # set the output directory
                model_dir = '{outdir}{env}-{res:06d}-{geo}'.format(
                    outdir=outdir, env=env[e], res=res[r], geo=geo[g])
                    
                # set the input sample path
                samples = '{samples}{sp}-{geo}-training.csv'.format(
                    samples=samples_dir, sp=sp[s], geo=geo[g])
                    
                # set the environmental layers directory
                env_layers = '{layers}{res:06d}-m/'.format(
                    layers=layers, res=res[r])
                    
                # and the layers to use
                if env[e] == 'clim':
                    layer_list = climlist
                elif env[e] == 'lcov':
                    layer_list = lcovlist
                else:
                    layer_list = envslist
                    
                # set the bias file path
                bias_file = '{bias}bias-file-{res:06d}-m/Culicidae.asc'.format(
                    bias=bias, res=res[r])
                    
                # set a flag to output the maps when using all variables
                if env[e] == 'envs':
                    write_grids = True
                else:
                    write_grids = False
                    
                # set the parameters in the maxent object
                mx.set_parameters(model_dir=model_dir, samples=samples, env_layers=env_layers,
                    bias_file=bias_file, write_grids=write_grids, nodata=nodata)
                    
                # set the layers
                mx.set_layers(layer_list)
                
                # and set the test data based on the extent
                if geo[g] == 'all':
                    mx.set_parameters(pct_test_points=test_pct)
                else:
                    test_samples = '{samples}{sp}-{geo}-testing.csv'.format(
                        samples=samples_dir, sp=sp[s], geo=geo[g])
                    mx.set_parameters(test_samples=test_samples)
                    
                # print out the command to run
                #ccb.prnt.status(mx.build_cmd())
                #mx.fit()
                
                # pull the output auc values
                try:
                    # get the predictions
                    ytrue, ypred = mx.get_predictions(spl[s], test=True)
                    
                    # get the number of test data
                    n_test = len(ytrue[ytrue == 1])
                    
                    # get the indices of the background points to subset
                    ind_bck = ytrue == 0
                    n_ind_bck = ind_bck.sum()
                    
                    # get random indices