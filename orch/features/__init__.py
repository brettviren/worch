#!/usr/bin/env python

import os.path as osp
from glob import glob

import waflib.Logs as msg
from waflib.TaskGen import feature as waf_feature

# just one for now....
def load():
    msg.debug('orch: loading features')

    mydir = osp.dirname(__file__)
    for fpath in glob("%s/feature_*.py"%mydir):
        ffile = osp.basename(fpath)
        modname = osp.splitext(ffile)[0]
        exec("from . import %s"%modname)
    msg.debug('orch: worch features: %s' % (', '.join(sorted(registered_defaults.keys())), ))
    from waflib.TaskGen import feats as available_features
    msg.debug('orch: waf features: %s' % (', '.join(sorted(available_features.keys())), ))

# eventually this becomes load()
def load_all():
    mydir = osp.dirname(__file__)
    for fpath in glob("%s/feature_*.py"%mydir):
        ffile = osp.basename(fpath)
        modname = osp.splitext(ffile)[0]
        exec("from . import %s"%modname)
    #from . import pfi
    #return (pfi.registered_func, pfi.registered_config)

registered_defaults = dict()  # feature name -> configuration dictionary
def defaults(feats):
    ret = dict()
    for toe in feats:
        d = registered_defaults.get(toe)
        if d:
            ret.update(d)
    return ret

def register_defaults(name, **kwds):
    '''Register a set of default feature configuration items which may be overridden by user configuration.  
    '''
    registered_defaults[name] = kwds


# Returns a function that takes the decorated worch feature function
# and returns something that looks like a waf feature function
def decorator(feature_name, **feature_defaults):
    
    msg.debug('orch: making decorator for feature "%s"' % feature_name)

    # Take a worch feature function and return a function that looks
    # like a waf feature function
    def wrapper(worch_feat_func):

        msg.debug('orch: decorating feature "%s"' % feature_name)

        # A function that looks like a waf feature function and calls
        # the worch feature function
        def waf_feat(tgen):

            msg.debug('orch: calling feature "%s"' % feature_name)

            from orch.features.pfi import PackageFeatureInfo
            pfi = PackageFeatureInfo(feature_name, tgen.bld, **feature_defaults)
            worch_feat_func(pfi)

        registered_defaults[feature_name] = feature_defaults
        return waf_feature(feature_name)(waf_feat)
    return wrapper

            
